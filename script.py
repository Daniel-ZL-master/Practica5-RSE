import serial
from datetime import datetime
import csv
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import collections
import numpy as np  # Necesario para calcular la desviación estándar fácilmente

# Configuración del puerto serie
SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 115200
TIMEOUT = 1

# Historial para el eje temporal compartido
t_data = collections.deque(maxlen=50)

# Historial para las Medias del Acelerómetro
mean_x_data = collections.deque(maxlen=50)
mean_y_data = collections.deque(maxlen=50)
mean_z_data = collections.deque(maxlen=50)

# Historial para las Desviaciones Estándar del Giroscopio
std_ax_data = collections.deque(maxlen=50)
std_ay_data = collections.deque(maxlen=50)
std_az_data = collections.deque(maxlen=50)

start_time = datetime.now()


def main():
    # 1. Inicializar puerto serie
    try:
        serial_port = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT)
        print(f"Puerto serie abierto: {serial_port.name}")
    except Exception as e:
        print(f"Error al abrir el puerto serie: {e}")
        return

    # 2. Inicializar archivo CSV
    log_filename = f"log_practica5_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(log_filename, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(
            ['Aceleracion X', 'Aceleracion Y', 'Aceleracion Z', 'Giroscopio X', 'Giroscopio Y', 'Giroscopio Z', 'Magnetometro X', 'Magnetometro Y', 'Magnetometro Z'])

    # 3. Configurar la figura con 2 subplots apilados (compartiendo el eje X)
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(10, 8))

    # Subplot 1: Acelerómetro (Medias)
    line_ax, = ax1.plot([], [], 'r-', marker='o', label='Media Accel X')
    line_ay, = ax1.plot([], [], 'g-', marker='s', label='Media Accel Y')
    line_az, = ax1.plot([], [], 'b-', marker='^', label='Media Accel Z')
    ax1.set_title('Acelerómetro: Medias cada 5 segundos')
    ax1.set_ylabel('Aceleración')
    ax1.legend(loc='upper left')
    ax1.grid(True)

    # Subplot 2: Giroscopio (Desviaciones Estándar)
    line_ax_std, = ax2.plot([], [], 'r--', marker='o', label='Std Accel X')
    line_ay_std, = ax2.plot([], [], 'g--', marker='s', label='Std Accel Y')
    line_az_std, = ax2.plot([], [], 'b--', marker='^', label='Std Accel Z')
    ax2.set_title('Acelerómetro: Desviación Estándar cada 5 segundos')
    ax2.set_xlabel('Tiempo (s)')
    ax2.set_ylabel('Std Aceleración')
    ax2.legend(loc='upper left')
    ax2.grid(True)

    # Ajustar el espaciado para que no se superpongan los textos
    fig.tight_layout()

    # 4. Función de actualización
    def update_data(frame):
        lines_to_write = []

        # Ventanas temporales para acumular datos de los 5 segundos
        window_ax = []
        window_ay = []
        window_az = []

        window_gx = []
        window_gy = []
        window_gz = []

        window_mx = []
        window_my = []
        window_mz = []

        while serial_port.in_waiting > 0:
            try:
                line = serial_port.readline().decode('utf-8').strip()
                if not line:
                    continue

                output_data = line.split(';')

                if len(output_data) == 9:
                    lines_to_write.append(output_data)

                    # Extraer datos y separar en listas
                    ax_x, ax_y, ax_z = map(float, output_data[0:3])
                    gx, gy, gz = map(float, output_data[3:6])
                    mx, my, mz = map(float, output_data[6:9])

                    window_ax.append(ax_x)
                    window_ay.append(ax_y)
                    window_az.append(ax_z)

                    window_gx.append(gx)
                    window_gy.append(gy)
                    window_gz.append(gz)

                    window_mx.append(mx)
                    window_my.append(my)
                    window_mz.append(mz)

            except ValueError:
                pass
            except Exception as e:
                print(f"Error procesando línea: {e}")

        # Escribir en CSV
        if lines_to_write:
            with open(log_filename, mode='a', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(lines_to_write)

        # Actualizar gráficas si se recibieron datos válidos
        if window_ax:
            # 4.1 Cálculos Acelerómetro (Media)
            avg_x = sum(window_ax) / len(window_ax)
            avg_y = sum(window_ay) / len(window_ay)
            avg_z = sum(window_az) / len(window_az)

            # 4.2 Cálculos Acelerómetro (Desviación Estándar con numpy)
            std_ax = np.std(window_ax)
            std_ay = np.std(window_ay)
            std_az = np.std(window_az)

            current_time = (datetime.now() - start_time).total_seconds()

            # 4.3 Añadir al historial
            t_data.append(current_time)

            mean_x_data.append(avg_x)
            mean_y_data.append(avg_y)
            mean_z_data.append(avg_z)

            std_ax_data.append(std_ax)
            std_ay_data.append(std_ay)
            std_az_data.append(std_az)

            # 4.4 Actualizar líneas
            line_ax.set_data(t_data, mean_x_data)
            line_ay.set_data(t_data, mean_y_data)
            line_az.set_data(t_data, mean_z_data)

            line_ax_std.set_data(t_data, std_ax_data)
            line_ay_std.set_data(t_data, std_ay_data)
            line_az_std.set_data(t_data, std_az_data)

            # 4.5 Reajustar límites de ambos ejes
            ax1.relim()
            ax1.autoscale_view()
            ax2.relim()
            ax2.autoscale_view()

        return line_ax, line_ay, line_az, line_ax_std, line_ay_std, line_az_std

    # 5. Iniciar la animación
    ani = animation.FuncAnimation(
        fig,
        update_data,
        interval=5000,
        blit=False,
        cache_frame_data=False
    )

    try:
        print("Mostrando gráficas. Cierra la ventana o presiona Ctrl+C en la terminal para salir.")
        plt.show()
    except KeyboardInterrupt:
        print("Interrupción detectada.")
    finally:
        print("Cerrando el puerto serie...")
        serial_port.close()


if __name__ == '__main__':
    main()