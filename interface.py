import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo
import threading
import time
import json
import os
from scan import scan_wifi_net, parse_windows_scan_results
from graphs import (
    draw_signal_level_graph,  # Функция для рисования графика уровня сигнала
    draw_temporal_signal_graph,  # Функция для рисования графика динамики сигнала
)


class WifiAnalyzerInterface(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Анализатор Wi-Fi")  # Назначаем имя окна
        self.geometry("1600x800")  # Размер окна приложения
        self.selected_networks = (
            []
        )  # Список выбранных сетей (не используется в данном примере)
        self.network_data = {}  # Данные о сетях Wi-Fi
        self.scan_stopped = True  # Начальное состояние: сканирование остановлено
        self.create_widgets()  # Создание UI-компонентов
        self.update_ui()  # Первоначальное заполнение интерфейса данными

        # Регистрация обработчика события закрытия окна
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        """
        Завершение процесса принудительным способом при закрытии окна.
        """
        pid = os.getpid()  # Получаем PID текущего процесса
        os.kill(
            pid, 9
        )  # Отправляем сигнал SIGKILL для принудительного завершения процесса
        sys.exit(0)  # Выход из программы (на всякий случай)

    def create_widgets(self):
        # Верхняя панель меню
        menu_frame = ttk.Frame(self)
        menu_frame.pack(fill=tk.X, pady=(10, 20))  # Рамка меню сверху окна

        # Кнопка старта сканирования
        btn_scan_start = ttk.Button(
            menu_frame, text="Запустить сканирование", command=self.start_scanning
        )
        btn_scan_start.grid(row=0, column=0, padx=5)  # Располагаем кнопку слева

        # Кнопка остановки сканирования
        btn_scan_stop = ttk.Button(
            menu_frame, text="Остановить сканирование", command=self.stop_scanning
        )
        btn_scan_stop.grid(row=0, column=1, padx=5)  # Вторая кнопка справа от первой

        # Фильтры по частотному диапазону
        buttons = ["Все сети", "2.4 GHz", "5 GHz"]  # Варианты фильтров
        for idx, freq in enumerate(buttons):
            cmd = lambda x=freq: self.filter_by_frequency(
                x
            )  # Передача аргументов в фильтр
            button = ttk.Button(menu_frame, text=freq, command=cmd)
            button.grid(
                row=0, column=idx + 2, padx=5
            )  # Каждую кнопку размещаем рядом друг с другом

        # Основной контейнер компонентов
        main_container = ttk.Frame(self)
        main_container.pack(
            fill=tk.BOTH, expand=True
        )  # Контейнер занимает всё доступное пространство

        # Таблица с информацией о сетях
        table_frame = ttk.Frame(main_container)
        table_frame.pack(
            side=tk.TOP, fill=tk.BOTH, expand=True
        )  # Таблица располагается сверху контейнера

        # Определение структуры таблицы
        columns = (
            "№",
            "Имя сети (SSID)",
            "Канал",
            "Сила сигнала (%)",
            "Сила сигнала (dBm)",
            "Тип сети",
            "Проверка подлинности",
            "Шифрование",
            "Тип радио",
        )
        self.tree = ttk.Treeview(
            table_frame, columns=columns, show="headings"
        )  # Дерево таблиц

        # Прокручиваемые полосы для таблицы
        scroll_v = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.tree.yview
        )  # Полоса прокрутки вертикально
        self.tree.configure(yscrollcommand=scroll_v.set)
        scroll_h = ttk.Scrollbar(
            main_container, orient="horizontal", command=self.tree.xview
        )  # Горизонтальная полоса прокрутки
        self.tree.configure(xscrollcommand=scroll_h.set)

        # Заголовки колонок
        for col_idx, col in enumerate(columns):
            self.tree.heading(
                col_idx, text=col, command=lambda c=col_idx: self.sort_column(c)
            )  # Возможность сортировки по клику на заголовке
            self.tree.column(
                col_idx, anchor=tk.W, minwidth=0, stretch=1
            )  # Параметры колонок

        # Графическая область для отображения двух видов графиков
        graph_container = ttk.Frame(main_container)
        graph_container.pack(
            side=tk.BOTTOM, fill=tk.BOTH, expand=True
        )  # Расположены внизу экрана

        # Левый график: уровень сигнала по каналам
        graph_left, update_left, deactivate_left = draw_signal_level_graph(
            graph_container
        )
        graph_left.get_tk_widget().pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True
        )  # Отображение графика

        # Правый график: временная динамика сигнала
        graph_right, update_right, deactivate_right = draw_temporal_signal_graph(
            graph_container
        )
        graph_right.get_tk_widget().pack(
            side=tk.RIGHT, fill=tk.BOTH, expand=True
        )  # Отображение второго графика

        # Сохраняем функции обновления и деактивации графиков
        self.update_signal_level = update_left
        self.deactivate_signal_level = deactivate_left
        self.update_temporal = update_right
        self.deactivate_temporal = deactivate_right

        # Упаковка остальных элементов
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_v.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_h.pack(side=tk.BOTTOM, fill=tk.X)

    def sort_column(self, col_idx):
        """Метод для сортировки таблицы по указанному индексу колонки."""
        items = list(self.tree.get_children(""))  # Получаем все элементы таблицы
        try:
            items = sorted(
                items, key=lambda i: self.tree.item(i)["values"][col_idx], reverse=False
            )  # Сортируем элементы по нужному полю
        except ValueError:
            pass  # Игнорируем ошибку, если нельзя отсортировать (например, строковые данные)
        for idx, item in enumerate(items):
            self.tree.move(
                item, "", idx
            )  # Перемещаем элементы согласно порядку сортировки

    def filter_by_frequency(self, choice):
        """Фильтрует сети по выбранному диапазону частот."""
        if choice == "Все сети":
            filtered_data = self.network_data  # Показывать все доступные сети
        elif choice == "2.4 GHz":
            filtered_data = {
                key: val
                for key, val in self.network_data.items()
                if any(int(net["канал"]) <= 13 for net in val)
            }  # Оставляем только сети с каналом ≤ 13
        elif choice == "5 GHz":
            filtered_data = {
                key: val
                for key, val in self.network_data.items()
                if any(int(net["канал"]) >= 36 for net in val)
            }  # Оставляем только сети с каналом ≥ 36
        self.populate_table(filtered_data)  # Обновляем таблицу фильтрованными данными

    def populate_table(self, data):
        """Обновляет содержимое таблицы новыми данными."""
        self.tree.delete(*self.tree.get_children())  # Удаляем старые записи
        row_id = 1  # Начинаем нумеровать строки заново
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
                self.tree.insert(
                    "", tk.END, values=values
                )  # Добавляем новую запись в таблицу
                row_id += 1  # Следующий порядковый номер строки

    def update_ui(self):
        """Обновляет интерфейс: считывает данные из файла и обновляет графики и таблицу."""
        try:
            with open("parsed_networks.json", "r", encoding="utf-8") as file:
                self.network_data = json.load(
                    file
                )  # Загружаем сохранённые данные о сетях
        except Exception as e:
            print(f"Ошибка загрузки файла: {e}")
            return

        # Обновляем графики и таблицу
        self.update_signal_level(self.network_data)
        self.update_temporal(self.network_data)
        self.populate_table(self.network_data)

    def stop_scanning(self):
        """
        Останавливает процесс сканирования.
        """
        self.scan_stopped = (
            True  # Устанавливаем флаг, сообщающий о прекращении сканирования
        )

    def start_scanning(self):
        """
        Запускает процесс сканирования.
        """
        self.scan_stopped = False  # Снимаем флаг остановки
        self.scan_thread = threading.Thread(
            target=self.scan_and_update
        )  # Создаем поток для фоновой обработки
        self.scan_thread.start()  # Запускаем поток

    def scan_and_update(self):
        """
        Выполняет циклический процесс сканирования и обновления данных.
        Продолжает работать пока не будет установлено условие остановки.
        """
        while not self.scan_stopped:
            result_lines = (
                scan_wifi_net()
            )  # Запрашивает сканирование беспроводных сетей
            networks = parse_windows_scan_results(
                result_lines
            )  # Парсим полученные результаты
            with open("parsed_networks.json", "w", encoding="utf-8") as file:
                json.dump(
                    networks, file, ensure_ascii=False, indent=4
                )  # Сохраняем результаты в файл
            self.update_ui()  # Обновляем интерфейс с новыми данными
            time.sleep(1)  # Пауза между итерациями сканирования
