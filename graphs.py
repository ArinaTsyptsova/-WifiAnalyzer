import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import datetime

global_active = True  # Флаг для управления активностью графика


# Функция рисования графика уровней сигналов по каналам
def draw_signal_level_graph(parent):
    fig, ax = plt.subplots(figsize=(7, 5))  # Создание фигуры и осей для графика
    canvas = FigureCanvasTkAgg(
        fig, master=parent
    )  # Привязываем фигуру к родительскому компоненту Tkinter
    canvas.draw()  # Рисуем начальное состояние графика
    canvas.get_tk_widget().pack(fill="both", expand=True)  # Отображаем виджет графики

    # Внутренняя функция для обновления графика по новым данным
    def update_plot(data):
        global global_active
        if not global_active:
            return  # Выходим, если график отключён

        channels = set()  # Множество уникальных номеров каналов
        signals = {}  # Словарь для хранения информации о сигналах разных SSID

        # Собираем данные по сигналам и каналам
        for ssid, networks in data.items():
            for network in networks:
                if "канал" in network and "signal_dbm" in network:
                    channel = int(
                        network["канал"]
                    )  # Преобразование строки канала в число
                    signal_dbm = float(network["signal_dbm"])  # Амплитуда сигнала в dBm

                    channels.add(channel)  # Сохраняем уникальный номер канала
                    if ssid not in signals:
                        signals[ssid] = {"channels": [], "signals": []}
                    signals[ssid]["channels"].append(channel)
                    signals[ssid]["signals"].append(signal_dbm)

        # Очищаем оси перед перерисовкой
        ax.clear()

        # Генерируем случайные цвета для различных SSID
        colors = [
            "#" + "".join(np.random.choice(list("0123456789ABCDEF"), size=6))
            for _ in range(len(signals))
        ]

        # Строим гистограмму сигналов
        for idx, (ssid, info) in enumerate(signals.items()):
            # Поднимаем столбики над уровнем "-100" для наглядности визуализации
            bottom_values = [-100] * len(info["channels"])  # Базовая линия
            heights = [
                (sig_val + 100) for sig_val in info["signals"]
            ]  # Высота столбца относительно базовой линии

            # Строим гистограмму для текущего SSID
            ax.bar(
                info["channels"],  # Положение столбцов
                heights,  # Высота столбцов
                bottom=bottom_values,  # Начало столбцов от -100
                width=0.8,
                align="center",
                label=ssid,
                color=colors[idx],
            )

        # Настраиваем границы и метки графика
        ax.set_ylim(-100, 0)  # Ограничиваем вертикальные значения (-100..0)
        ax.set_xticks(sorted(channels))  # Устанавливаем метки X по каналам
        ax.set_xticklabels(
            [f"{ch}" for ch in sorted(channels)]
        )  # Метки подписаны номерами каналов

        # Оформляем легенду и заголовок
        ax.legend(loc="upper right")
        ax.set_title("Уровень сигнала по каналам")
        ax.set_xlabel("Номер канала")
        ax.set_ylabel("Амплитуда (dBm)")

        # Пересчитываем и обновляем график
        canvas.draw_idle()

    # Функция деактивации графика
    def deactivate():
        global global_active
        global_active = False  # Меняем глобальную переменную на false

    return canvas, update_plot, deactivate


# Функция рисования временной зависимости изменения сигнала
def draw_temporal_signal_graph(parent):
    fig, ax = plt.subplots(figsize=(7, 5))  # Создаем новый график
    canvas = FigureCanvasTkAgg(fig, master=parent)  # Связываем его с окном Tkinter
    canvas.draw()  # Отрисовываем базовый пустой график
    canvas.get_tk_widget().pack(fill="both", expand=True)  # Встраиваем графику в окно

    timeseries = {}  # Хранит временные ряды для каждого SSID
    lines = {}  # Хранит линии для построения графика
    global_active = True  # Управляет состоянием активности графика

    # Внутренняя функция для обновления графика временных рядов
    def update_temporal_plot(data):
        global global_active
        if not global_active:
            return  # Ничего не делаем, если график выключен

        current_time = datetime.datetime.now()  # Текущее время

        # Обрабатываем новые данные и добавляем их в временную серию
        for ssid, networks in data.items():
            last_signal_dbm = None
            for network in networks:
                if "signal_dbm" in network:
                    last_signal_dbm = float(network["signal_dbm"])

            # Формируем временные серии для каждого SSID
            if ssid not in timeseries:
                timeseries[ssid] = (
                    [current_time],
                    [last_signal_dbm],
                )  # Начальная точка
            else:
                timeseries[ssid][0].append(current_time)  # Добавляем новое время
                timeseries[ssid][1].append(
                    last_signal_dbm
                )  # Добавляем новую амплитуду сигнала

        # Очистка текущих осей перед построением нового графика
        ax.clear()

        # Генерация цветов для линий
        colors = [
            "#" + "".join(np.random.choice(list("0123456789ABCDEF"), size=6))
            for _ in range(len(timeseries))
        ]

        # Построение графика для каждого SSID
        for idx, (ssid, series) in enumerate(timeseries.items()):
            (line,) = ax.plot(
                series[0], series[1], marker="o", label=ssid, color=colors[idx]
            )  # Линии на графике с маркерами
            lines[ssid] = (
                line  # Сохраняем ссылку на линию для последующего использования
            )

        # Настройка границ и оформления графика
        ax.set_ylim(-100, 0)  # Диапазон y (-100...0)
        ax.legend(loc="upper left")  # Легенда слева вверху
        ax.set_title("Изменение уровня сигнала по времени")
        ax.set_xlabel("Время")
        ax.set_ylabel("Амплитуда (dBm)")

        # Обновление содержимого окна графика
        canvas.draw_idle()

    # Деактивация графика
    def deactivate():
        global global_active
        global_active = False  # Переключаем активность графика

    return canvas, update_temporal_plot, deactivate
