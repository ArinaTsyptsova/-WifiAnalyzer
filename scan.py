import subprocess
import re
from collections import defaultdict
import json


def scan_wifi_net():
    """
    Выполняет команду для сканирования Wi-Fi сетей в операционной системе Windows.
    Возвращает список строк с результатами сканирования.
    """
    command = ["netsh", "wlan", "show", "networks", "mode=Bssid"]

    try:
        # Запускаем команду и получаем результат
        result = subprocess.run(
            command,
            capture_output=True,  # Захват стандартного вывода
            text=True,  # Работаем с текстом
            encoding="cp866",  # Использование русской кодировки для Windows
        )

        # Проверяем успешность выполнения команды
        if result.returncode != 0:
            raise Exception(f"Команда завершилась с ошибкой: {result.stderr}")

        # Возвращаем результат командной строки, разбивая его на отдельные строки
        return result.stdout.splitlines()

    except subprocess.CalledProcessError as e:
        print(f"Ошибка выполнения команды: {e}")
        return None


def percentage_to_dbm(percentage):
    """
    Преобразует процентное значение уровня сигнала в эквивалентное значение в единицах dBm.
    Сигнал Wi-Fi измеряется в диапазоне примерно от -100 до -30 dBm.
    """
    min_signal = -100  # Нижний предел уровня сигнала в dBm
    max_signal = -30  # Верхний предел уровня сигнала в dBm
    dbm_value = min_signal + ((max_signal - min_signal) / 100) * percentage
    return round(dbm_value, 2)


def parse_windows_scan_results(lines):
    """
    Анализирует строки результата сканирования Wi-Fi сетей и формирует структуру данных
    в виде списка сетей с соответствующими параметрами.
    """
    networks = defaultdict(list)  # Хранилище для списков сетей
    current_network = {}  # Объект для сбора информации о текущей сети

    for line in lines:
        if not line.strip():
            continue  # Пропускаем пустые строки

        # Поиск блоков "SSID X:" и "BSSID Y:"
        pattern = r"(SSID|BSSID)\s+\d+: (.+)"
        match = re.search(pattern, line)
        if match:
            key, value = match.groups()
            key = key.lower()  # Приводим ключ к нижнему регистру

            if key == "ssid":
                # Если нашли новую сеть, записываем предыдущую и начинаем сбор новой
                if current_network:
                    # Проверяем наличие обязательного поля 'ssid'
                    if "ssid" in current_network:
                        networks[current_network["ssid"]].append(current_network.copy())
                    else:
                        print(f"Предупреждение: пропущено имя сети ({value})")

                current_network = {"ssid": value}  # Новая сеть начинается

            elif key == "bssid":
                # Добавляем MAC-адреса устройств данной сети
                value = value.strip()
                current_network.setdefault("bssid", []).append(value)
            continue

        # Поиск уровня сигнала
        if "Сигнал:" in line:
            signal_match = re.search(r"Сигнал:\s+(\d+)%", line)
            if signal_match:
                signal_percentage = int(signal_match.group(1))
                signal_dbm = percentage_to_dbm(signal_percentage)  # Преобразуем % в dBm
                current_network["signal_strength"] = (
                    signal_percentage  # Уровнь сигнала в %
                )
                current_network["signal_dbm"] = signal_dbm  # Уровень сигнала в dBm
                continue

        # Остальные параметры сети
        additional_params_patterns = {
            "Тип сети": r"Тип сети\s*:\s*(.*)",  # Тип сети (WPA/WEP/Open)
            "Проверка подлинности": r"Проверка подлинности\s*:\s*(.*)",  # Аутентификация (PSK/EAP)
            "Шифрование": r"Шифрование\s*:\s*(.*)",  # Алгоритм шифрования (AES/TKIP)
            "Тип радио": r"Тип радио\s*:\s*(.*)",  # Стандарт связи (802.11a/b/g/n/ac)
            "Канал": r"Канал\s*:\s*(.*)",  # Номер канала
        }

        # Поиск соответствующих параметров
        for param_name, regex_pattern in additional_params_patterns.items():
            match = re.search(regex_pattern, line)
            if match:
                value = match.group(1).strip()
                current_network[param_name.lower().replace(" ", "_")] = value
                break

    # Последнюю сеть добавляем отдельно, если она осталась незакрытой
    if current_network and "ssid" in current_network:
        networks[current_network["ssid"]].append(current_network.copy())

    return dict(networks)


def print_results(networks):
    """
    Выводит информацию о сетях в консоль.
    """
    if not networks:
        print("Нет доступных сетей")
        return

    index = 1
    for ssid, network_list in networks.items():
        for network in network_list:
            bssids = "\n".join(f"BSSID: {bssid}" for bssid in network.get("bssid", []))
            signal_percentage = network.get("signal_strength", "")
            signal_dbm = network.get("signal_dbm", "")
            type_of_network = network.get("тип_сети", "")
            authentication = network.get("проверка_подлинности", "")
            encryption = network.get("шифрование", "")
            radio_type = network.get("тип_радио", "")
            channel = network.get("канал", "")

            print(f"Сеть #{index}:")
            print(f" SSID: {ssid}")
            print(bssids)
            print(f" Уровень сигнала: {signal_percentage}% ({signal_dbm} dBm)")
            print(f" Тип сети: {type_of_network}")
            print(f" Проверка подлинности: {authentication}")
            print(f" Шифрование: {encryption}")
            print(f" Тип радио: {radio_type}")
            print(f" Канал: {channel}")
            index += 1


# if __name__ == "__main__":
#     # Выполнение сканирования
#     result_lines = scan_wifi_net()
#     print(result_lines)

#     # Парсинг результатов сканирования
#     networks = parse_windows_scan_results(result_lines)

#     # Сохранение результатов в JSON-файл
#     with open('parsed_networks.json', 'w', encoding='utf-8') as f:
#         json.dump(networks, f, ensure_ascii=False, indent=4)

#     # Печать результатов
#     print_results(networks)
