

import socket
import threading


# Atiende a un cliente en particular.
# Cada cliente tiene su propia conexión, dirección y hilo.
def manejar_cliente(conn, addr, lista_clientes, lock_clientes):

    print(f"\n[NUEVA CONEXIÓN] {addr} conectado.")

    try:
        # El cliente puede enviar varios mensajes mientras siga conectado.
        while True:

            # Recibe hasta 1024 bytes y los convierte en texto.
            mensaje = conn.recv(1024).decode("utf-8")

            # Si no se recibe ningún dato, el cliente cerró la conexión.
            if not mensaje:
                break

            # Muestra en la terminal del servidor lo que envió el cliente.
            print(f"[{addr}] dice: {mensaje}")

            # CAMBIO 1: comando /adios
            # Si el cliente escribe /adios, enviamos una despedida
            # y terminamos el ciclo de atención de ese cliente.
            if mensaje.strip() == "/adios":

                respuesta = "Hasta luego. Te has desconectado del servidor."
                conn.sendall(respuesta.encode("utf-8"))

                break

            # CAMBIO 2: comando /users
            # Si el cliente escribe /users, obtenemos la lista
            # de direcciones de los clientes conectados.
            elif mensaje.strip() == "/users":

                # El bloqueo evita que varios hilos accedan
                # simultáneamente a la lista mientras se modifica.
                with lock_clientes:

                    usuarios = [
                        str(direccion)
                        for conexion, direccion in lista_clientes
                    ]

                # Si hay usuarios, construimos la respuesta.
                if usuarios:
                    respuesta = (
                        "Usuarios conectados:\n" + "\n".join(usuarios)
                    )
                else:
                    respuesta = "No hay usuarios conectados."

                # Enviamos la lista al cliente que solicitó /users.
                conn.sendall(respuesta.encode("utf-8"))

            # Si no es /adios ni /users, aplicamos el Echo.
            # Devolvemos al cliente el mensaje que envió.
            else:
                respuesta = f"Eco: {mensaje}"
                conn.sendall(respuesta.encode("utf-8"))

    # Si el cliente pierde la conexión inesperadamente,
    # evitamos que el hilo termine con un error sin controlar.
    except (ConnectionResetError, OSError):
        print(f"\n[AVISO] Se perdió la conexión con {addr}.")

    finally:
        # CAMBIO 3: limpieza de la conexión.
        # Se ejecuta al terminar la atención del cliente.
        conn.close()

        # Eliminamos de la lista al cliente que acaba de salir.
        with lock_clientes:
            lista_clientes[:] = [
                (conexion, direccion)
                for conexion, direccion in lista_clientes
                if conexion != conn
            ]

            # Calculamos cuántos clientes siguen conectados.
            cantidad = len(lista_clientes)

        # Informamos la desconexión y la cantidad actual.
        print(f"\n[DESCONEXIÓN] {addr} se ha ido.")
        print(f"[CLIENTES ACTIVOS] {cantidad}")


# Función que inicia y mantiene funcionando el servidor.
def iniciar_servidor():

    # Crea un socket IPv4 que utiliza TCP.
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Asocia el servidor a la computadora local y al puerto 5050.
    server.bind(("localhost", 5050))

    # Deja al servidor preparado para aceptar conexiones.
    server.listen()

    # Lista compartida: guarda (conexión, dirección) de cada cliente.
    clientes_activos = []

    # Bloqueo para coordinar el acceso a la lista compartida.
    lock_clientes = threading.Lock()

    print("[INICIO] Servidor escuchando en el puerto 5050...")

    try:
        # El servidor permanece esperando nuevas conexiones.
        while True:

            # Acepta una conexión y obtiene el socket del cliente
            # y su dirección IP/puerto.
            conn, addr = server.accept()

            # Registramos al nuevo cliente en la lista.
            with lock_clientes:
                clientes_activos.append((conn, addr))
                cantidad = len(clientes_activos)

            # Creamos un hilo independiente para atenderlo.
            hilo = threading.Thread(
                target=manejar_cliente,
                args=(
                    conn,
                    addr,
                    clientes_activos,
                    lock_clientes
                )
            )

            # Inicia la ejecución del hilo.
            hilo.start()

            print(f"[CLIENTES ACTIVOS] {cantidad}")

    # Permite detener el servidor con Ctrl + C.
    except KeyboardInterrupt:
        print("\n[CIERRE] Cerrando el servidor...")

    finally:
        # Cierra el socket que escucha nuevas conexiones.
        server.close()


# Ejecuta el servidor cuando se inicia directamente este archivo.
if __name__ == "__main__":
    iniciar_servidor()
