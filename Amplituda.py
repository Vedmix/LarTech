import serial
import time
import matplotlib.pyplot as plt
import numpy as np


def collect_packet(ser, packet_size=100):
    """Собирает пакет из заданного количества измерений"""
    packet_data = []
    measurements_collected = 0

    print(f"Начинаем сбор пакета из {packet_size} измерений...")

    # Очищаем буфер перед началом сбора
    ser.reset_input_buffer()
    time.sleep(0.1)

    packet_start_time = time.time()

    while measurements_collected < packet_size:
        try:
            line = ser.readline().decode('ascii', errors='ignore').strip()
            if line and ',' in line:
                current_time = time.time()
                elapsed = current_time - packet_start_time

                adc_str, volt_str = line.split(',')

                # Упрощенная обработка
                adc_str = ''.join(filter(str.isdigit, adc_str))
                volt_str = ''.join(filter(str.isdigit, volt_str))

                if adc_str and volt_str:
                    try:
                        adc_value = int(adc_str)
                        millivolts = int(volt_str)
                        voltage = millivolts / 1000.0

                        packet_data.append({
                            'measurement_num': measurements_collected + 1,
                            'adc': adc_value,
                            'voltage': voltage,
                            'elapsed_time': elapsed
                        })

                        measurements_collected += 1

                        if measurements_collected % 20 == 0:
                            print(f"  Собрано: {measurements_collected}/{packet_size}")

                    except ValueError:
                        continue
        except Exception as e:
            print(f"Ошибка при чтении: {e}")
            continue

    packet_end_time = time.time()
    total_packet_time = packet_end_time - packet_start_time

    print(f"Пакет из {packet_size} измерений собран за {total_packet_time:.3f} сек!")
    return packet_data, total_packet_time


def plot_packet(packet_data, packet_number):
    """Создает график для пакета данных с двумя подграфиками"""
    if not packet_data:
        print(f"Пакет {packet_number} пуст!")
        return

    # Создаем отдельное окно для каждого пакета
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    fig.suptitle(f'Пакет измерений #{packet_number} ({len(packet_data)} измерений)', fontsize=14, fontweight='bold')

    # Подготавливаем данные
    measurements = [d['measurement_num'] for d in packet_data]
    voltages = [d['voltage'] for d in packet_data]
    elapsed_times = [d['elapsed_time'] for d in packet_data]

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

    # Статистика для первого графика
    avg_voltage = np.mean(voltages)
    min_voltage = np.min(voltages)
    max_voltage = np.max(voltages)
    ax1.text(0.02, 0.98, f'Среднее: {avg_voltage:.3f} В\nМин: {min_voltage:.3f} В\nМакс: {max_voltage:.3f} В',
             transform=ax1.transAxes, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    # График 2: Напряжение vs Время (как в старой версии)
    ax2.plot(elapsed_times, voltages, 'ro-', markersize=3, linewidth=1, alpha=0.7)
    ax2.set_ylim(0, 3.4)
    ax2.grid(True)
    ax2.set_xlabel('Время (секунды)')
    ax2.set_ylabel('Напряжение (V)')
    ax2.set_title(f'Напряжение по времени (пакет #{packet_number})')
    ax2.yaxis.set_major_locator(plt.MultipleLocator(0.1))

    # Статистика для второго графика
    total_time = elapsed_times[-1] if elapsed_times else 0
    frequency = len(packet_data) / total_time if total_time > 0 else 0
    ax2.text(0.02, 0.98, f'Общее время: {total_time:.3f} сек\nЧастота: {frequency:.1f} Гц',
             transform=ax2.transAxes, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))

    plt.tight_layout()
    plt.show(block=False)


def main():
    ser = serial.Serial('COM5', 115200, timeout=1)
    time.sleep(2)

    ser.reset_input_buffer()
    print("Буфер очищен, начинаем измерения...")
    print("Программа соберет 3 пакета по 100 измерений каждый")
    print("=" * 60)

    all_packets = []

    try:
        for packet_num in range(1, 4):
            print(f"\n{'=' * 40}")
            print(f"СБОР ПАКЕТА #{packet_num}")
            print('=' * 40)

            packet_data, packet_time = collect_packet(ser, packet_size=100)

            if packet_data:
                all_packets.append(packet_data)

                # Выводим статистику в консоль
                voltages = [d['voltage'] for d in packet_data]
                elapsed_times = [d['elapsed_time'] for d in packet_data]

                print(f"\n=== Статистика пакета #{packet_num} ===")
                print(f"Количество измерений: {len(packet_data)}")
                print(f"Общее время сбора: {packet_time:.3f} сек")

                total_time = elapsed_times[-1] if elapsed_times else 0
                frequency = len(packet_data) / total_time if total_time > 0 else 0
                print(f"Частота измерений: {frequency:.1f} Гц")

                avg_voltage = np.mean(voltages)
                min_voltage = np.min(voltages)
                max_voltage = np.max(voltages)
                print(f"Среднее напряжение: {avg_voltage:.3f} В")
                print(f"Мин. напряжение: {min_voltage:.3f} В")
                print(f"Макс. напряжение: {max_voltage:.3f} В")
                print("=" * 40 + "\n")

                # Отображаем график
                plot_packet(packet_data, packet_num)

                # Пауза между пакетами
                if packet_num < 3:
                    pause_time = 1
                    print(f"\nПауза {pause_time} секунд перед сбором следующего пакета...")
                    time.sleep(pause_time)
                    ser.reset_input_buffer()
            else:
                print(f"Ошибка: не удалось собрать пакет #{packet_num}")

        # Сводная статистика
        if all_packets:
            print("\n" + "=" * 60)
            print("СВОДНАЯ СТАТИСТИКА ПО ВСЕМ ПАКЕТАМ")
            print("=" * 60)

            for i, packet in enumerate(all_packets, 1):
                if packet:
                    voltages = [d['voltage'] for d in packet]
                    elapsed_times = [d['elapsed_time'] for d in packet]

                    avg_v = np.mean(voltages)
                    std_v = np.std(voltages)
                    total_time = elapsed_times[-1] if elapsed_times else 0
                    frequency = len(packet) / total_time if total_time > 0 else 0

                    print(f"Пакет #{i}: Частота={frequency:.1f} Гц, "
                          f"Среднее={avg_v:.3f} В, Станд.отклонение={std_v:.3f} В, "
                          f"Измерений={len(packet)}")

        # Ждем закрытия графиков
        print("\nВсе графики открыты. Закройте окна графиков для завершения программы.")
        plt.show(block=True)

    except KeyboardInterrupt:
        print("\nПрограмма прервана пользователем")
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        if ser and ser.is_open:
            ser.close()
            print("Порт закрыт")


if __name__ == "__main__":
    main()