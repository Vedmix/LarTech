import serial
import time
import matplotlib.pyplot as plt

ser = serial.Serial('COM5', 115200, timeout=1)
ser.reset_input_buffer()

plt.ion()
fig, ax = plt.subplots(figsize=(12, 6))

times, voltages = [], []
line, = ax.plot(times, voltages, 'bo-', markersize=5, linewidth=1, alpha=0.7)

# ФИКСИРОВАННЫЙ МАСШТАБ
ax.set_xlim(0, 40)
ax.set_xticks(range(0, 41, 1))

# Диапазон и метки должны соответствовать
ax.set_ylim(3.285, 3.305)
ax.set_yticks([3.285, 3.290, 3.295, 3.300, 3.305])

ax.grid(True)

measurement_count = 0

try:
    while True:
        data = ser.readline().decode('ascii', errors='ignore').strip()
        if data and ',' in data:
            volt_str = data.split(',')[1]
            voltage = float(volt_str) / 1000.0
            measurement_count += 1
            freq = measurement_count % 41

            if freq == 0:
                times.clear()
                voltages.clear()

            times.append(freq)
            voltages.append(voltage)

            line.set_data(times, voltages)

            plt.pause(0.001)

except KeyboardInterrupt:
    pass

finally:
    ser.close()
    plt.ioff()
    plt.show()


ser = serial.Serial('COM5', 115200, timeout=1)
time.sleep(2)

ser.reset_input_buffer()
print("Буфер очищен, начинаем измерения...")

start_time = time.time()

try:
    while True:
        line = ser.readline().decode('ascii', errors='ignore').strip()
        if line and ',' in line:
            current_time = time.time()
            elapsed = current_time - start_time

            adc_str, volt_str = line.split(',')
            print(f"{elapsed:7.3f} сек: ADC={adc_str}, V={int(volt_str) / 1000:.3f}V")

except KeyboardInterrupt:
    ser.close()