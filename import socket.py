import socket


HOST = 'localhost'  # Reemplaza 'X.X' con la dirección IP de la Raspberry Pi en la red

PORT = 65432          # Puerto en el que el servidor escucha

# Creación del socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


client_socket.connect((HOST, PORT))

# Enviar datos al servidor
message = "APAGAR"
client_socket.sendall(message.encode())

# Opcionalmente, recibir respuesta del servidor
# response = client_socket.recv(1024)
# print("Respuesta del servidor:", response.decode())

client_socket.close()  # Cerrar el socket después de enviar