import serial
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib

matplotlib.use('TkAgg')

ser = None
total_measurement_count = 0
program_running = True
start_time = None


def showVolts():
    global total_measurement_count, program_running, ser, start_time

    start_time = time.time()

    fig, ax = plt.subplots(figsize=(12, 6))
    fig.canvas.manager.set_window_title('Мониторинг напряжения NUCLEO-F401RE')

    times, voltages = [], []
    line, = ax.plot(times, voltages, 'bo-', markersize=5, linewidth=1, alpha=0.7)

    # ФИКСИРОВАННЫЕ ГРАНИЦЫ ОСЕЙ
    ax.set_xlim(0, 40)  # X: от 0 до 40
    ax.set_ylim(0, 3.4)  # Y: от 0 до 3.4
    ax.grid(True)
    ax.set_xlabel('Измерение #')
    ax.set_ylabel('Напряжение (V)')

    # Настраиваем шаги сетки - шаг по X = 1, по Y = 0.1
    ax.xaxis.set_major_locator(plt.MultipleLocator(1))  # шаг по X: 1
    ax.yaxis.set_major_locator(plt.MultipleLocator(0.1))  # шаг по Y: 0.1

    title_text = ax.set_title(f'Напряжение: --.-- В | Измерение #0')

    def read_data():
        try:
            line = ser.readline().decode('ascii', errors='ignore').strip()
            if not line or ',' not in line:
                return None

            # Разделяем строку на две части по запятой
            adc_str, volt_str = line.split(',')

            # Упрощенная обработка - просто удаляем нецифровые символы
            adc_str = ''.join(filter(str.isdigit, adc_str))
            volt_str = ''.join(filter(str.isdigit, volt_str))

            if not (adc_str and volt_str):
                return None

            try:
                adc_value = int(adc_str)
                millivolts = int(volt_str)
            except ValueError:
                return None

            voltage = millivolts / 1000.0
            return adc_value, voltage, line
        except:
            return None

    def update_plot(frame):
        global total_measurement_count, program_running

        if not program_running:
            return line, title_text

        data = read_data()
        if data is None:
            return line, title_text

        adc_value, voltage, raw_line = data
        total_measurement_count += 1

        # Вычисляем прошедшее время
        current_time = time.time()
        elapsed = current_time - start_time

        # Используем вашу логику с очисткой каждые 40 измерений
        freq = total_measurement_count % 41

        if freq == 0:
            times.clear()
            voltages.clear()
            # Также сбрасываем линию
            line.set_data([], [])
            # Сбрасываем границы оси X
            ax.set_xlim(0, 40)
            return line, title_text

        times.append(freq)
        voltages.append(voltage)

        line.set_data(times, voltages)
        title_text.set_text(f'Напряжение: {voltage:.3f} В | Измерение #{total_measurement_count} | ADC: {adc_value}')

        # Ваш формат вывода в консоль
        print(f"{elapsed:7.3f} сек: ADC={adc_value}, V={voltage:.3f}V")

        return line, title_text

    def on_close(event):
        global program_running
        program_running = False

    fig.canvas.mpl_connect('close_event', on_close)

    ani = FuncAnimation(fig=fig,
                        func=update_plot,
                        frames=None,
                        interval=25,
                        blit=True,
                        cache_frame_data=False,
                        repeat=False)

    plt.tight_layout()
    plt.show()


def main():
    global ser, program_running

    ser = serial.Serial('COM5', 115200, timeout=1)
    time.sleep(2)
    ser.reset_input_buffer()

    print("Буфер очищен, начинаем измерения...")

    try:
        choice = input("Ваш выбор (1/2): ").strip()

        if choice == '2':
            showVolts()
        else:
            print("Неверный выбор")

    except KeyboardInterrupt:
        print("\nПрограмма прервана")
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        program_running = False
        time.sleep(0.1)

        if ser and ser.is_open:
            ser.close()
            print("Порт закрыт")


if __name__ == "__main__":
    main()