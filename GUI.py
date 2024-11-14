from tkinter import *
import customtkinter
import socket

# Configuración del socket
HOST = 'localhost'        # Dirección IP del servidor (ajustar según sea necesario)
PORT = 65432              # Puerto en el que el servidor escucha

# Configuración de la apariencia de la GUI
customtkinter.set_appearance_mode("dark")  # Opciones: system (default), light, dark
customtkinter.set_default_color_theme("dark-blue")  # Opciones de tema: blue (default), dark-blue, green

# Inicialización de la ventana principal
root = customtkinter.CTk()
root.title('CareBot - Interfaz de Usuario')
root.geometry('1000x700')  # Tamaño de la ventana

# Variable para almacenar las selecciones de compartimientos
selecciones = set()


# ======================================= FUNCIONES =============================================

def reseteo():
    """
    Envía una señal de "Borrar" al servidor para reiniciar la ruta en el sistema.
    Además, reinicia la interfaz a la pantalla inicial con los botones segmentados
    y el botón de enviar.
    """
    # Crear y configurar el socket de cliente
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        message = "Borrar"
        client_socket.sendall(message.encode())
        
    # Reiniciar la interfaz a la pantalla inicial
    selecciones.clear()
    compartimientos.configure(values=["1", "2", "3"])
    enviar.configure(text="Enviar", command=enviar_datos)
    enviar.pack(pady=20)  # Espacio debajo del botón de enviar


def enviar_datos():
    """
    Envía los datos seleccionados de cuarto, cama y compartimiento al servidor.
    Cuando se seleccionan tres compartimientos, cambia el botón "Enviar" a "Confirmar Ruta".
    """
    # Obtener valores seleccionados
    lugar = int(ComboCuartos.get()) * 100 + int(Combocamas.get())
    compartimiento = compartimientos.get()
    
    # Añadir el compartimiento seleccionado al conjunto
    selecciones.add(compartimiento)
    
    # Verificar si las 3 opciones han sido seleccionadas
    if len(selecciones) == 3:
        confirmacion()
    
    # Crear y configurar el socket de cliente
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        message = f"{lugar},{compartimiento}"
        client_socket.sendall(message.encode())
        
    # Borrar el compartimiento seleccionado de la lista de opciones
    compartimientos.delete(compartimiento)


def confirmacion():
    """
    Configura el botón "Enviar" como "Confirmar Ruta" para iniciar la ruta
    y añade el botón "Borrar Ruta" para resetear la selección.
    """
    enviar.configure(text="Confirmar Ruta", command=inicio_ruta)
    
    


def inicio_ruta():
    """
    Envía una señal de "Inicio" al servidor para iniciar la ruta.
    """
    # Crear y configurar el socket de cliente
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        message = "Inicio"
        client_socket.sendall(message.encode())


# ======================================= COMPONENTES DE LA GUI =============================================

# Crear el título en la interfaz
Titulo = customtkinter.CTkLabel(root, text="CareBot", font=("Nunito Bold", 40))
Titulo.pack(pady=30)  # Espacio alrededor del título

# Etiqueta y selector de cuarto
label_cuartos = customtkinter.CTkLabel(root, text="Cuarto:", font=("Nunito", 14))
label_cuartos.pack(pady=(10, 5))  # Espacio arriba y abajo
ComboCuartos = customtkinter.CTkComboBox(root, values=["1", "2", "3", "4"])
ComboCuartos.pack(pady=5)

# Etiqueta y selector de cama
label_camas = customtkinter.CTkLabel(root, text="Cama:", font=("Nunito", 14))
label_camas.pack(pady=(15, 2))  # Espacio arriba
Combocamas = customtkinter.CTkComboBox(root, values=["1", "2", "3", "4"])
Combocamas.pack(pady=5)

# Etiqueta y botón segmentado para compartimientos
label_compartimento = customtkinter.CTkLabel(root, text="Compartimiento:", font=("Nunito", 14))
label_compartimento.pack(pady=(15, 2))
compartimientos = customtkinter.CTkSegmentedButton(root, values=["1", "2", "3"],
                                                   width=25,
                                                   height=150,
                                                   font=("Nunito", 12),
                                                   corner_radius=30,
                                                   border_width=5)
compartimientos.pack(pady=5)

# Botón para enviar datos
enviar = customtkinter.CTkButton(root, text="Enviar", command=enviar_datos)
enviar.pack(pady=20)  # Espacio debajo del botón

# Crear y agregar el botón de reset para borrar la ruta
reset = customtkinter.CTkButton(root, text="Borrar Ruta", command=reseteo)
reset.pack(pady=20)  # Espacio debajo del botón de reset

# Ejecutar el bucle principal de la interfaz
root.mainloop()