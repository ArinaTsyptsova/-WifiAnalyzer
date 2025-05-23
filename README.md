# Wi Fi Анализатор

## Как запустить проект

Для начала убедитесь, что у вас установлена последняя версия Python (рекомендуется версии >= 3.8).

1. Установите зависимости проекта командой:

bash
pip install -r requirements.txt

2. Откройте терминал и выполните:

python app.py

## Ключевые файлы
app.py: Главная точка входа приложения. Осуществляет координацию всего функционала: создание окна, подключение графического интерфейса, запуск процесса сканирования и обновление графиков.

scan.py: Реализует логику сканирования доступных Wi-Fi сетей. Используется команда netsh wlan show networks mode=bssid для Windows.

classifier.py: Содержит логику разделения сетей по диапазонам частот (2.4 GHz и 5 GHz).

interface.py: Графический интерфейс приложения, созданный с использованием библиотеки Tkinter. Включает дерево (TreeView) для отображения данных о сетях и панели инструментов для управления сканированием.

graphs.py: Библиотека для визуализации графиков уровня сигнала и временной динамики. Интегрирована с библиотекой Matplotlib.

## Возможности программы
Автоматическое сканирование доступных Wi-Fi сетей.
Визуализация уровня сигнала по каналам.
Динамическая диаграмма, отражающая изменение уровня сигнала во времени.
Удобный фильтр по типу сети (2.4 GHz, 5 GHz).
Экспорт данных в формате JSON для дополнительного анализа.

## Примеры использования
Открыв программу, нажмите кнопку "Запустить сканирование". После некоторого ожидания вы получите таблицу с полной информацией о доступных сетях, а также графики уровня сигнала и его изменения по времени.

## Установка зависимостей
Перед началом работы убедитесь, что установлены следующие пакеты:

tkinter: стандартный модуль Python для создания графического интерфейса.

matplotlib: библиотека для построения графиков.

pip install -r requirements.txt
