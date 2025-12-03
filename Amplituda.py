import serial
import time

PORT = 'COM5'
BAUDRATE = 9600
MONITOR = serial.Serial(PORT, BAUDRATE, timeout=2)

def voltGroupReader(groupNum, MONITOR, volCount):
    MONITOR.dtr = True
    time.sleep(0.1)
    MONITOR.dtr = False
    time.sleep(3)
    MONITOR.reset_input_buffer()

    while MONITOR.in_waiting == 0:
        time.sleep(0.001)
    first_line = MONITOR.readline()

    voltage_groups = []
    group_times = []

    for i in range(groupNum):
        startTime = time.perf_counter()
        voltageList = []
        collected = 0

        while collected < volCount:
                line = MONITOR.readline().decode('ascii', errors='ignore').strip()
                volStr = line[(line.find('V:') + 2):].split()[0]
                volFlt = float(volStr)
                voltageList.append(volFlt)
                collected += 1

        endTime = time.perf_counter()
        deltaTime = endTime - startTime
        freq = volCount / deltaTime

        voltage_groups.append(voltageList)
        group_times.append(freq)

    MONITOR.close()
    return voltage_groups, group_times

voltage_groups, frequencies = voltGroupReader(10, MONITOR,10)

print("Частоты групп:", frequencies)