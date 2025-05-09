import json


def classify_networks(networks):
    """Разделяет список сетей на две группы: работающие на частоте 2.4 ГГц и 5 ГГц."""
    classified_networks = {"2.4 GHz": [], "5 GHz": []}

    # Проходим по каждому элементу входящего словаря сетей
    for _, network_list in networks.items():
        for network in network_list:
            # Извлекаем значение канала (frequency band), используемое для классификации
            channel = network.get("канал")

            # Если канал указан численно, определяем диапазон частоты
            if channel is not None and channel.isdigit():
                ch_num = int(channel)

                # Определяем принадлежность сети к диапазону 2.4 ГГц или 5 ГГц
                if 1 <= ch_num <= 13:
                    classified_networks["2.4 GHz"].append(network)
                elif 36 <= ch_num <= 173:
                    classified_networks["5 GHz"].append(network)
                else:
                    pass  # Можно оставить пустым, либо обработать другие случаи

            else:
                # Обработка случаев, когда канал отсутствует или имеет неверный формат
                print(
                    f"Внимание: некорректный канал '{channel}' для сети {network['ssid']}!"
                )

    return classified_networks


def print_classified_results(classified_networks):
    """
    Функция выводит сети, разделённые по частотам, в удобной форме для чтения человеком.
    """
    # Перебираем каждый диапазон частот (2.4 GHz и 5 GHz)
    for freq_band, networks in classified_networks.items():
        print(f"\n--- {freq_band.upper()} ---")  # Заголовок блока

        # Если сети найдены, выводим информацию о каждой
        if len(networks) > 0:
            for idx, network in enumerate(networks, start=1):
                print(f"Сеть №{idx}:")
                print(f" SSID: {network['ssid']}")  # Название сети
                print(
                    f" BSSIDs: {', '.join(network.get('bssid', ['N/A']))}"
                )  # MAC-адреса точек доступа
                print(
                    f" Уровень сигнала: {network.get('signal_strength', '')}%"
                )  # Мощность сигнала
                print(
                    f" Тип сети: {network.get('тип_сети', '')}"
                )  # Технология связи (Wi-Fi стандарт)
                print(
                    f" Проверка подлинности: {network.get('проверка_подлинности', '')}"
                )  # Метод аутентификации
                print(
                    f" Шифрование: {network.get('шифрование', '')}"
                )  # Используемый алгоритм шифрования
                print(
                    f" Тип радио: {network.get('тип_радио', '')}"
                )  # Тип радиопередачи
                print(f" Канал: {network.get('канал', '')}\n")  # Номер канала передачи
        else:
            print("Нет доступных сетей.")  # Сообщение, если сеть не найдена


# Блок основного скрипта закомментирован для удобства повторного использования функций
# if __name__ == '__main__':
#     # Читаем данные из файла JSON
#     with open('parsed_networks.json', 'r', encoding='utf-8') as f:
#         parsed_networks = json.load(f)

#     # Разделяем сети по диапазонам
#     classified_networks = classify_networks(parsed_networks)

#     # Выводим классифицированные сети
#     print_classified_results(classified_networks)
