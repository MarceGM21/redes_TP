

import socket

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    cliente.connect(("localhost", 5050))
    print("Conectado al servidor.")
    print("Escribí /users para ver los conectados.")
    print("Escribí /adios para desconectarte.")

    while True:
        mensaje = input("\nMarcelo: ")

        # Enviar mensaje al servidor
        cliente.sendall(mensaje.encode("utf-8"))

        # Recibir respuesta
        respuesta = cliente.recv(4096).decode("utf-8")
        print("\nServidor:", respuesta)

        # Terminar el cliente después de /adios
        if mensaje.strip() == "/adios":
            break

except ConnectionRefusedError:
    print("No se pudo conectar. ¿Está iniciado el servidor?")

except (ConnectionResetError, OSError):
    print("La conexión con el servidor se cerró.")

finally:
    cliente.close()
    print("Cliente cerrado.")
