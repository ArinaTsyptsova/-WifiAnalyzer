import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo
import threading
import time
import json
import os
from scan import scan_wifi_net, parse_windows_scan_results
from graphs import (
    draw_signal_level_graph,
    draw_temporal_signal_graph,
)


class WifiAnalyzerInterface(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Анализатор Wi-Fi")
        self.geometry("1600x800")
        self.selected_networks = []
        self.network_data = {}
        self.scan_stopped = True  # Начальное состояние: сканирование остановлено
        self.create_widgets()
        self.update_ui()

        # Регистрируем обработчик события закрытия окна
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        """
        Принудительно завершает процесс при закрытии окна.
        """
        pid = os.getpid()  # Получаем идентификатор текущего процесса
        os.kill(pid, 9)  # Принудительно завершаем процесс (SIGKILL в Linux/MacOS)
        sys.exit(0)  # На всякий случай вызываем exit для гарантии завершения

    def create_widgets(self):
        # Верхняя панель управления
        menu_frame = ttk.Frame(self)
        menu_frame.pack(fill=tk.X, pady=(10, 20))

        # Кнопка запуска сканирования
        btn_scan_start = ttk.Button(
            menu_frame, text="Запустить сканирование", command=self.start_scanning
        )
        btn_scan_start.grid(row=0, column=0, padx=5)

        # Кнопка остановки сканирования
        btn_scan_stop = ttk.Button(
            menu_frame, text="Остановить сканирование", command=self.stop_scanning
        )
        btn_scan_stop.grid(row=0, column=1, padx=5)

        # Кнопки фильтра частот
        buttons = ["Все сети", "2.4 GHz", "5 GHz"]
        for idx, freq in enumerate(buttons):
            cmd = lambda x=freq: self.filter_by_frequency(x)
            button = ttk.Button(menu_frame, text=freq, command=cmd)
            button.grid(row=0, column=idx + 2, padx=5)

        # Основные компоненты интерфейса
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Таблица с сетями
        table_frame = ttk.Frame(main_container)
        table_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Структура таблицы
        columns = (
            "№",
            "Имя сети (SSID)",
            "Канал",
            "Сила сигнала (%)",
            "Сила сигнала (dBm)",
            "Тип сети",
            "Проверка подлинности",
            "Шифрование",
            "Радиотип",
        )
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        # Прокрутка дерева
        scroll_v = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scroll_v.set)
        scroll_h = ttk.Scrollbar(
            main_container, orient="horizontal", command=self.tree.xview
        )
        self.tree.configure(xscrollcommand=scroll_h.set)

        # Заголовки колонок
        for col_idx, col in enumerate(columns):
            self.tree.heading(
                col_idx, text=col, command=lambda c=col_idx: self.sort_column(c)
            )
            self.tree.column(col_idx, anchor=tk.W, minwidth=0, stretch=1)

        # Графики
        graph_container = ttk.Frame(main_container)
        graph_container.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        # Левый график (уровень сигнала)
        graph_left, update_left, deactivate_left = draw_signal_level_graph(
            graph_container
        )
        graph_left.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Правый график (временная динамика)
        graph_right, update_right, deactivate_right = draw_temporal_signal_graph(
            graph_container
        )
        graph_right.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Сохраняем функции обновления и деактивации графиков
        self.update_signal_level = update_left
        self.deactivate_signal_level = deactivate_left
        self.update_temporal = update_right
        self.deactivate_temporal = deactivate_right

        # Упаковка элементов
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_v.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_h.pack(side=tk.BOTTOM, fill=tk.X)

    def sort_column(self, col_idx):
        """Сортировка столбца"""
        items = list(self.tree.get_children(""))
        try:
            items = sorted(
                items, key=lambda i: self.tree.item(i)["values"][col_idx], reverse=False
            )
        except ValueError:
            pass
        for idx, item in enumerate(items):
            self.tree.move(item, "", idx)

    def filter_by_frequency(self, choice):
        """Фильтрация по диапазону частот"""
        if choice == "Все сети":
            filtered_data = self.network_data
        elif choice == "2.4 GHz":
            filtered_data = {
                key: val
                for key, val in self.network_data.items()
                if any(int(net["канал"]) <= 13 for net in val)
            }
        elif choice == "5 GHz":
            filtered_data = {
                key: val
                for key, val in self.network_data.items()
                if any(int(net["канал"]) >= 36 for net in val)
            }
        self.populate_table(filtered_data)

    def populate_table(self, data):
        """Заполняем таблицу новыми данными"""
        self.tree.delete(*self.tree.get_children())  # Очищаем таблицу
        row_id = 1
        for _, networks in sorted(data.items()):
            for net in networks:
                values = (
                    row_id,
                    net.get("ssid"),
                    net.get("канал"),
                    f"{net.get('signal_strength')}%",
                    net.get("signal_dbm"),
                    net.get("тип_сети"),
                    net.get("проверка_подлинности"),
                    net.get("шифрование"),
                    net.get("тип_радио"),
                )
                self.tree.insert("", tk.END, values=values)
                row_id += 1

    def update_ui(self):
        """Обновляем интерфейс (таблицу и графики)"""
        try:
            with open("parsed_networks.json", "r", encoding="utf-8") as file:
                self.network_data = json.load(file)
        except Exception as e:
            print(f"Ошибка загрузки файла: {e}")
            return

        # Обновляем графики и таблицу
        self.update_signal_level(self.network_data)
        self.update_temporal(self.network_data)
        self.populate_table(self.network_data)

    def stop_scanning(self):
        """
        Метод, отвечающий за остановку процесса сканирования.
        """
        self.scan_stopped = True  # Устанавливаем флаг, говоря о необходимости остановки

    def start_scanning(self):
        """
        Начало процесса сканирования.
        """
        self.scan_stopped = False  # Снимаем флаг остановки
        self.scan_thread = threading.Thread(target=self.scan_and_update)
        self.scan_thread.start()

    def scan_and_update(self):
        """
        Процесс сканирования и обновления данных.
        Проверяет состояние флага self.scan_stopped и завершает работу, если установлен флаг.
        """
        while not self.scan_stopped:
            result_lines = scan_wifi_net()
            networks = parse_windows_scan_results(result_lines)
            with open("parsed_networks.json", "w", encoding="utf-8") as file:
                json.dump(networks, file, ensure_ascii=False, indent=4)
            self.update_ui()
            time.sleep(1)  # Пауза между итерациями сканирования
