  

import socket
import threading
import serial
import serial.tools.list_ports
import time

# ================================ CONFIGURACIÓN DEL SERVIDOR ====================================

HEADER = 64  # Tamaño fijo del encabezado para mensajes
PORT = 65432  # Puerto donde el servidor escucha
HOST = '0.0.0.0'  # Escucha en todas las interfaces de la máquina
ADDR = (HOST, PORT)  # Dirección completa del servidor
FORMAT = 'utf-8'  # Codificación de los mensajes
DISCONNECT_MESSAGE = "!DISCONNECT"  # Mensaje para desconectar clientes

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

connected_clients = []  # Lista para almacenar conexiones activas de clientes

# =============================== FUNCIONES DEL SERVIDOR ========================================


# =============               CONEXION SERIAL               =============

def find_serial_ports():
    """
    Encuentra y lista los puertos seriales disponibles en la máquina.
    :return: Lista de nombres de los puertos seriales disponibles.
    """
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def setup_serial_connection():
    """
    Configura una conexión serial con el primer puerto disponible.
    :return: Objeto de conexión serial si tiene éxito, None en caso contrario.
    """
    ports = find_serial_ports()
    if ports:
        selected_port = ports[0]
        print("Conectando al puerto:", selected_port)
        try:
            arduino = serial.Serial(selected_port, 9600)
            time.sleep(2)  # Esperar a que el puerto esté listo
            print("Conexión establecida con el Arduino en", selected_port)
            return arduino
        except serial.SerialException as e:
            print("Error al conectar al puerto:", e)
            return None
    else:
        print("No se encontraron puertos seriales disponibles.")
        return None


# Inicialización de la conexión serial
arduino = setup_serial_connection()
# Crear un candado global para proteger la comunicación serial
serial_lock = threading.Lock()

# Crear un evento para controlar la lectura desde el Arduino
read_event = threading.Event()
read_event.set()  # Permitir lectura al inicio

def read_from_arduino():
    if not arduino:
        print("Conexión serial no establecida. No se puede leer del Arduino.")
        return

    while True:
        try:
            # Esperar hasta que se permita leer
            read_event.wait()

            if arduino.in_waiting > 0:
                with serial_lock:  # Bloquear mientras se lee
                    line = arduino.readline().decode(FORMAT).strip()
                print("Arduino dice:", line)
                broadcast_message(line)
        except Exception as e:
            print("Error al leer desde el Arduino:", e)
            break



# =============               CONEXION MQTT                   =============

def handle_client(conn, addr):
    print(f"Conectado a: {addr}")
    connected_clients.append(conn)
    connected = True
    while connected:
        try:
            data = conn.recv(1024).decode(FORMAT)
            if data:
                if data == DISCONNECT_MESSAGE:
                    connected = False
                    print(f"Cliente {addr} desconectado.")
                    break

                command = data.strip()
                print(f"Recibido de {addr}: {command}")

                # Enviar comandos al Arduino según el mensaje recibido
                if arduino:
                    # Detener temporalmente la lectura del Arduino
                    read_event.clear()

                    with serial_lock:  # Bloquear mientras se escribe
                        if command == "Borrar":
                            arduino.write(b'CLEAR')  # Enviar comando "CLEAR" al Arduino
                        elif command == "Inicio":
                            arduino.write(b'START')  # Enviar comando "START" al Arduino
                        elif command.startswith("ComandoExtra"):
                            arduino.write(b'EXTRA')  # Enviar comando "EXTRA" al Arduino
                        else:
                            # Suponer que es un mensaje de formato "lugar,compartimiento"
                            try:
                                lugar, compartimiento = command.split(',')
                                lugar = int(lugar.strip())
                                compartimiento = int(compartimiento.strip())
                                    
                                if lugar == 1:
                                    arduino.write(b'1')
                                elif lugar == 2:
                                    arduino.write(b'2')
                                elif lugar == 3:
                                    arduino.write(b'3')
                                elif lugar == 4:
                                    arduino.write(b'4')

                                if compartimiento == 1:
                                    arduino.write(b'1')
                                elif compartimiento == 2:
                                    arduino.write(b'2')
                                elif compartimiento == 3:
                                    arduino.write(b'3')
                            except ValueError:
                                print("Error: formato de mensaje inválido.")
                    # Reanudar la lectura después de enviar el comando
                    read_event.set()
        except Exception as e:
            print(f"Error en la conexión con {addr}: {e}")
            break                    

    connected_clients.remove(conn)
    conn.close()
    print("Conexión cerrada con", addr)            


           
         



def broadcast_message(message):
    """
    Envía un mensaje a todos los clientes conectados.
    :param message: Mensaje a enviar.
    """
    for client in connected_clients:
        try:
            client.sendall(message.encode(FORMAT))
        except Exception as e:
            print(f"Error al enviar mensaje a un cliente: {e}")
            connected_clients.remove(client)


# =============               Encender servidor                  =============


# Función para iniciar el servidor y aceptar conexiones
def start_server():
    """
    Inicia el servidor para aceptar conexiones entrantes.
    """
    server.listen()
    print(f"Servidor escuchando en {ADDR}...")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"Conexiones activas: {threading.active_count() - 1}")




print("Iniciando servidor...")
arduino_thread = threading.Thread(target=read_from_arduino, daemon=True)
arduino_thread.start()

start_server()

