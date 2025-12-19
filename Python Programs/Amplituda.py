import serial
import time
import matplotlib.pyplot as plt
import numpy as np


def collect_packet(ser, packet_size=100):
    packet_data = []
    data_count = 0

    print(f"Сбор пакета из {packet_size} измерений...")

    ser.reset_input_buffer()
    time.sleep(0.1)

    packet_start_time = time.time()

    while data_count < packet_size:
        try:
            line = ser.readline().decode('ascii', errors='ignore').strip()
            if line and ',' in line:
                current_time = time.time()
                time_of_line = current_time - packet_start_time

                adc_str, volt_str = line.split(',')

                # Упрощенная обработка
                adc_str = ''.join(filter(str.isdigit, adc_str))
                volt_str = ''.join(filter(str.isdigit, volt_str))

                if adc_str and volt_str:
                    try:
                        adc_value = int(adc_str)
                        millivolts = int(volt_str)
                        voltage = millivolts / 1000.0#Разобраться

                        packet_data.append({
                            'No.': data_count + 1,
                            'voltage': voltage,
                            'time': time_of_line
                        })

                        data_count += 1

                        if data_count % 10 == 0:
                            print(f"  Собрано: {data_count}/{packet_size}")

                    except ValueError:
                        continue
        except Exception as e:
            print(f"Ошибка при чтении: {e}")
            continue

    packet_end_time = time.time()
    total_packet_time = packet_end_time - packet_start_time

    print(f"Пакет собран!")
    return packet_data, total_packet_time


def plot_packet(packet_data, packet_number):
    """Создает график для пакета данных с двумя подграфиками"""
    if not packet_data:
        print(f"Пакет {packet_number} пуст!")
        return

    # Создаем отдельное окно для каждого пакета
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    fig.suptitle(f'Пакет измерений #{packet_number}', fontsize=14, fontweight='bold')

    # Подготавливаем данные
    measurements = [d['No.'] for d in packet_data]
    voltages = [d['voltage'] for d in packet_data]
    elapsed_times = [d['time'] for d in packet_data]

    # График 1: Напряжение vs Номер измерения (как в старой версии)
    ax1.plot(measurements, voltages, 'bo-', markersize=3, linewidth=1, alpha=0.7)
    ax1.set_xlim(1, len(packet_data))
    ax1.set_ylim(0, 3.4)
    ax1.grid(True)

    ax1.set_xlabel('Номер измерения в пакете')
    ax1.set_ylabel('Напряжение (V)')
    ax1.set_title(f'Напряжение по порядку измерений (пакет #{packet_number})')
    ax1.xaxis.set_major_locator(plt.MultipleLocator(10))
    ax1.yaxis.set_major_locator(plt.MultipleLocator(0.1))

    # График 2: Напряжение vs Время (как в старой версии)
    ax2.plot(elapsed_times, voltages, 'ro-', markersize=3, linewidth=1, alpha=0.7)
    ax2.set_ylim(0, 3.4)
    ax2.grid(True)
    ax2.set_xlabel('Время (секунды)')
    ax2.set_ylabel('Напряжение (V)')
    ax2.set_title(f'Напряжение по времени (пакет #{packet_number})')

    ax2.yaxis.set_major_locator(plt.MultipleLocator(0.1))

    plt.tight_layout()
    plt.show(block=False)


def main():
    SER = serial.Serial('COM4', 115200, timeout=1)
    time.sleep(2)
    SER.reset_input_buffer()

    print("Буфер очищен, начинаем измерения...")

    all_packets = []

    try:
        for packet_num in range(3):

            packet_data, packet_time = collect_packet(SER, packet_size=100)

            if packet_data:
                all_packets.append(packet_data)

                voltages = [d['voltage'] for d in packet_data]
                times = [d['time'] for d in packet_data]

                frequency = len(packet_data) / packet_time if packet_time > 0 else 0

                avg_voltage = np.mean(voltages)
                min_voltage = np.min(voltages)
                max_voltage = np.max(voltages)

                print()
                print(f"Количество измерений: {len(packet_data)}")
                print(f"Общее время сбора: {packet_time:.3f} сек")
                print(f"Среднее напряжение: {avg_voltage:.3f} В")
                print(f"Мин. напряжение: {min_voltage:.3f} В")
                print(f"Макс. напряжение: {max_voltage:.3f} В")
                print(f"Частота измерений: {frequency:.1f} Гц")

                # Отображаем график
                plot_packet(packet_data, packet_num)

                # Пауза между пакетами
                if packet_num < 3:
                    pause_time = 1
                    time.sleep(pause_time)
                    SER.reset_input_buffer()
            else:
                print(f"Ошибка: не удалось собрать пакет")

    except KeyboardInterrupt:
        print("\nПрограмма прервана пользователем")
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        if SER and SER.is_open:
            SER.close()
            print("Порт закрыт")

if __name__ == "__main__":
    main()