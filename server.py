import socket
import threading
import serial
import serial.tools.list_ports
import time

# Configuración del servidor
HEADER = 64
PORT = 65432
HOST = '0.0.0.0'  # Escucha en todas las interfaces de la máquina
ADDR = (HOST, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"  # Mensaje para cerrar la conexión

# Función para encontrar y listar los puertos seriales disponibles
def find_serial_ports():
    ports = serial.tools.list_ports.comports()
    available_ports = [port.device for port in ports]
    return available_ports

# Configuración del puerto serial (automáticamente selecciona el primer puerto disponible)
def setup_serial_connection():
    ports = find_serial_ports()
    if ports:
        selected_port = ports[0]  # Selecciona el primer puerto disponible
        print("Conectando al puerto:", selected_port)
        try:
            arduino = serial.Serial(selected_port, 9600)
            time.sleep(2)  # Esperar a que el puerto serial esté listo
            print("Conexión establecida con el Arduino en", selected_port)
            return arduino
        except serial.SerialException as e:
            print("Error al conectar al puerto:", e)
            return None
    else:
        print("No se encontraron puertos seriales disponibles.")
        return None

# Inicializar la comunicación serial
arduino = setup_serial_connection()

# Función para manejar cada cliente en un hilo separado
def handle_client(conn, addr):
    print("Conectado a:", addr)
    connected = True
    while connected:
        try:
            # Recibir el tamaño del mensaje primero
            msg_length = conn.recv(HEADER).decode(FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                data = conn.recv(msg_length).decode(FORMAT)

                if data == DISCONNECT_MESSAGE:
                    connected = False
                    print(f"Cliente {addr} desconectado.")
                    break

                command = data.strip()
                print("Recibido de {}: {}".format(addr, command))

                # Enviar comandos al Arduino según el mensaje recibido
                if arduino:
                    if command == "ENCENDER":
                        arduino.write(b'H')  # Enviar 'H' al Arduino para encender el LED
                        print("Comando enviado al Arduino: ENCENDER")
                    elif command == "APAGAR":
                        arduino.write(b'L')  # Enviar 'L' al Arduino para apagar el LED
                        print("Comando enviado al Arduino: APAGAR")
                    else:
                        print("Comando no reconocido.")
            else:
                break

        except Exception as e:
            print(f"Error en la conexión con {addr}: {e}")
            break

    conn.close()
    print("Conexión cerrada con", addr)

# Función para iniciar el servidor y aceptar conexiones
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(ADDR)
    server_socket.listen()
    print("Servidor escuchando en {}:{}".format(HOST, PORT))

    while True:
        try:
            conn, addr = server_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.start()
        except KeyboardInterrupt:
            break

    server_socket.close()
    print("Servidor apagado.")

# Ejecutar el servidor
start_server()
