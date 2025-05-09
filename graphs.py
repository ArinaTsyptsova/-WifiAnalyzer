import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import datetime

global_active = True  # Переменная для контроля активности графика


def draw_signal_level_graph(parent):
    fig, ax = plt.subplots(figsize=(7, 5))
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

    # Функция обновления графика
    def update_plot(data):
        global global_active
        if not global_active:
            return  # Если график неактивен, ничего не делаем

        channels = set()
        signals = {}

        for ssid, networks in data.items():
            for network in networks:
                if "канал" in network and "signal_dbm" in network:
                    channel = int(network["канал"])
                    signal_dbm = float(network["signal_dbm"])

                    channels.add(channel)
                    if ssid not in signals:
                        signals[ssid] = {"channels": [], "signals": []}
                    signals[ssid]["channels"].append(channel)
                    signals[ssid]["signals"].append(signal_dbm)

        ax.clear()
        colors = [
            "#" + "".join(np.random.choice(list("0123456789ABCDEF"), size=6))
            for _ in range(len(signals))
        ]

        for idx, (ssid, info) in enumerate(signals.items()):
            # Изменяем начальную точку и высоту баров
            bottom_values = [-100] * len(info['channels'])
            heights = [(sig_val + 100) for sig_val in info['signals']]
            
            ax.bar(
                info["channels"],   # положение столбцов
                heights,           # высота столбцов относительно -100
                bottom=bottom_values,  # начало столбцов от -100
                width=0.8,
                align="center",
                label=ssid,
                color=colors[idx],
            )

        ax.set_ylim(-100, 0)
        ax.set_xticks(sorted(channels))
        ax.set_xticklabels([f"{ch}" for ch in sorted(channels)])

        ax.legend(loc="upper right")
        ax.set_title("Уровень сигнала по каналам")
        ax.set_xlabel("Номер канала")
        ax.set_ylabel("Амплитуда (dB)")
        canvas.draw_idle()

    # Функция для отключения графика
    def deactivate():
        global global_active
        global_active = False

    return canvas, update_plot, deactivate


def draw_temporal_signal_graph(parent):
    fig, ax = plt.subplots(figsize=(7, 5))
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

    timeseries = {}
    lines = {}
    global_active = True  # Переменная для контроля активности графика

    # Функция обновления временного графика
    def update_temporal_plot(data):
        global global_active
        if not global_active:
            return  # Если график неактивен, ничего не делаем

        current_time = datetime.datetime.now()

        for ssid, networks in data.items():
            last_signal_dbm = None
            for network in networks:
                if "signal_dbm" in network:
                    last_signal_dbm = float(network["signal_dbm"])

            if ssid not in timeseries:
                timeseries[ssid] = ([current_time], [last_signal_dbm])
            else:
                timeseries[ssid][0].append(current_time)
                timeseries[ssid][1].append(last_signal_dbm)

        ax.clear()
        colors = [
            "#" + "".join(np.random.choice(list("0123456789ABCDEF"), size=6))
            for _ in range(len(timeseries))
        ]

        for idx, (ssid, series) in enumerate(timeseries.items()):
            (line,) = ax.plot(
                series[0], series[1], marker="o", label=ssid, color=colors[idx]
            )
            lines[ssid] = line

        ax.set_ylim(-100, 0)
        ax.legend(loc="upper left")
        ax.set_title("Изменение уровня сигнала по времени")
        ax.set_xlabel("Время")
        ax.set_ylabel("Амплитуда (dB)")
        canvas.draw_idle()

    # Функция для отключения графика
    def deactivate():
        global global_active
        global_active = False

    return canvas, update_temporal_plot, deactivate
