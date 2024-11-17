import socket
import threading
import serial
import serial.tools.list_ports
import time

# Configuración del servidor
HOST = '0.0.0.0'  # Escucha en todas las interfaces de la máquina
PORT = 65432      # Puerto en el que el servidor escucha

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
    while True:
        data = conn.recv(1024)  # Recibir hasta 1024 bytes
        if not data:
            break  # Si no se reciben datos, finalizar la conexión
        
        # Decodificar el mensaje
        command = data.decode().strip()
        print("Recibido de {}: {}".format(addr, command))

        # Manejo de comandos
         
        if command == "Borrar":
            if arduino:
                arduino.write(b'CLEAR')  # Enviar comando "CLEAR" al Arduino
                print("Comando enviado al Arduino: Borrar")

        elif command == "Inicio":
            if arduino:
                arduino.write(b'START')  # Enviar comando "START" al Arduino
                print("Comando enviado al Arduino: Inicio")
        
        # Ejemplo para un comando adicional
        elif command == "ComandoExtra":
            if arduino:
                arduino.write(b'EXTRA')  # Enviar comando "EXTRA" al Arduino
                print("Comando enviado al Arduino: ComandoExtra")

        # Comandos de cama y compartimiento
        else:
            try:
                # Separar el mensaje en lugar y compartimiento
                lugar, compartimiento = command.split(',')
                lugar = int(lugar.strip())
                compartimiento = int(compartimiento.strip())
                
                # Enviar comando al Arduino según el número de cama
                if lugar == 101:
                    arduino.write(b'C1')  # Comando para la cama 101
                elif lugar == 102:
                    arduino.write(b'C2')  # Comando para la cama 102
                elif lugar == 103:
                    arduino.write(b'C3')  # Comando para la cama 102
                elif lugar == 104:
                    arduino.write(b'C4')  # Comando para la cama 102
                elif lugar == 201:
                    arduino.write(b'C5')  # Comando para la cama 102
                elif lugar == 202:
                    arduino.write(b'C6')  # Comando para la cama 102
                elif lugar == 203:
                    arduino.write(b'C7')  # Comando para la cama 102
                elif lugar == 204:
                    arduino.write(b'C8')  # Comando para la cama 102
                elif lugar == 301:
                    arduino.write(b'C9')  # Comando para la cama 102
                elif lugar == 302:
                    arduino.write(b'C10')  # Comando para la cama 102
                elif lugar == 303:
                    arduino.write(b'C11')  # Comando para la cama 102
                elif lugar == 304:
                    arduino.write(b'C12')  # Comando para la cama 102
                elif lugar == 401:
                    arduino.write(b'C13')  # Comando para la cama 102
                elif lugar == 402:
                    arduino.write(b'C14')  # Comando para la cama 102
                elif lugar == 403:
                    arduino.write(b'C15')  # Comando para la cama 102
                elif lugar == 404:
                    arduino.write(b'C16')  # Comando para la cama 404
                else:
                    print("Número de cama no reconocido.")

                # Enviar comando al Arduino según el compartimiento
                if compartimiento == 1:
                    arduino.write(b'P1')  # Comando para el compartimiento 1
                elif compartimiento == 2:
                    arduino.write(b'P2')  # Comando para el compartimiento 2
                elif compartimiento == 3:
                    arduino.write(b'P3')  # Comando para el compartimiento 3
                else:
                    print("Número de compartimiento no reconocido.")

                print("Comando enviado al Arduino: Cama {}, Compartimiento {}".format(lugar, compartimiento))
            
            except ValueError:
                print("Error: formato de mensaje inválido.")
    
    conn.close()
    print("Conexión cerrada con", addr)

# Función para iniciar el servidor y aceptar conexiones
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print("Servidor escuchando en {}:{}".format(HOST, PORT))
    
    while True:
        try:
            conn, addr = server_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.start()
        except KeyboardInterrupt:
            break  # Salir del bucle si se detecta una interrupción de teclado

    server_socket.close()
    print("Servidor apagado.")

# Función para monitorear la terminal y permitir apagado del servidor
def monitor_shutdown():
    while True:
        command = input("Escribe 'shutdown' para apagar el servidor: ")
        if command.strip().lower() == "shutdown":
            print("Apagando el servidor...")
            break

# Ejecutar el servidor y el monitoreo del apagado en hilos separados
server_thread = threading.Thread(target=start_server)
monitor_thread = threading.Thread(target=monitor_shutdown)

server_thread.start()
monitor_thread.start()

monitor_thread.join()  # Esperar a que el comando de apagado se ejecute
server_thread.join()   # Asegurarse de que el servidor termine
