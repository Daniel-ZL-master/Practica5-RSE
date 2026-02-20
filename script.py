# This is a sample Python script.

# Press Mayús+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import serial
from datetime import datetime
import csv
import time
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation


def main():
    #SERIAL PORT
    serial_port = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
    print(f"Serial port open: {serial_port}")

    #CSV LOG
    log_filename = f"log_practica5_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(log_filename, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Aceleracion X', 'Aceleracion Y', 'Aceleracion Z', 'Giroscopio X', 'Giroscopio Y', 'Giroscopio Z'])

    try:
        while True:
            ani = animation.FuncAnimation(
                fig,
                update_data,
                frames=200,
                init_func=init,
                interval=20,
                blit=True,
                repeat=True
            )
            input_buffer_size = serial_port.inWaiting()
            if input_buffer_size > 0:
                line = serial_port.read(input_buffer_size).decode('utf-8').strip()
                output_data = line.split(';')
                with open(log_filename, mode='a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(output_data)
                print(line)
    except KeyboardInterrupt:
        print("Closing port")
        serial_port.close()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()