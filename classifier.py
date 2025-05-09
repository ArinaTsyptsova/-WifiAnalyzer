import json

def classify_networks(networks):
    classified_networks = {"2.4 GHz": [], "5 GHz": []}

    for _, network_list in networks.items():
        for network in network_list:
            channel = network.get('канал')  # Получаем канал
            if channel is not None and channel.isdigit():  # Проверяем, что канал существует и является числом
                ch_num = int(channel)
                if 1 <= ch_num <= 13:
                    classified_networks["2.4 GHz"].append(network)
                elif 36 <= ch_num <= 173:
                    classified_networks["5 GHz"].append(network)
                else:
                    pass  # Возможно предусмотреть обработку ситуации с нестандартными каналами
            else:
                print(f"Внимание: некорректный канал '{channel}' для сети {network['ssid']}!")

    return classified_networks


def print_classified_results(classified_networks):
    """
    Выводит сети, разделённые по частотам.
    """
    for freq_band, networks in classified_networks.items():
        print(f"\n--- {freq_band.upper()} ---")
        if len(networks) > 0:
            for idx, network in enumerate(networks, start=1):
                print(f"Сеть №{idx}:")
                print(f" SSID: {network['ssid']}")
                print(f" BSSIDs: {', '.join(network.get('bssid', ['N/A']))}")
                print(f" Уровень сигнала: {network.get('signal_strength', '')}%")
                print(f" Тип сети: {network.get('тип_сети', '')}")
                print(f" Проверка подлинности: {network.get('проверка_подлинности', '')}")
                print(f" Шифрование: {network.get('шифрование', '')}")
                print(f" Тип радио: {network.get('тип_радио', '')}")
                print(f" Канал: {network.get('канал', '')}\n")
        else:
            print("Нет доступных сетей.")


# if __name__ == '__main__':
#     # Чтение данных из JSON-файла
#     with open('parsed_networks.json', 'r', encoding='utf-8') as f:
#         parsed_networks = json.load(f)

#     # Классификация сетей
#     classified_networks = classify_networks(parsed_networks)

#     # Вывод результатов
#     print_classified_results(classified_networks)