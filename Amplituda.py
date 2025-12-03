import serial
import time

PORT = 'COM5'
BAUDRATE = 9600

ser = serial.Serial(PORT, BAUDRATE, timeout=2)

ser.dtr = True
time.sleep(0.1)
ser.dtr = False
time.sleep(3)
ser.reset_input_buffer()

while ser.in_waiting == 0:
    time.sleep(0.001)
first_line = ser.readline()
voltage_groups = [[], [], []]
group_times = [0, 0, 0]

for group_num in range(3):
    group_samples = []
    group_start_time = time.perf_counter()

    collected = 0
    while collected < 100:
        if ser.in_waiting > 0:
            line = ser.readline().decode('ascii', errors='ignore').strip()

            if line and "ADC:" in line and "V:" in line:
                v_start = line.find('V:') + 2
                voltage_str = line[v_start:].split()[0]
                voltage = float(voltage_str)
                group_samples.append(voltage)
                collected += 1
        else:
            time.sleep(0.0001)

    group_end_time = time.perf_counter()
    group_times[group_num] = group_end_time - group_start_time
    voltage_groups[group_num] = group_samples

    freq = 100 / group_times[group_num]
    print(f"Группа {group_num + 1}: частота = {freq:.3f} Гц, значений = {len(group_samples)}")

ser.close()

# print(voltage_groups[0])
# print(voltage_groups[1])
# print(voltage_groups[2])