import socket
import time

if __name__ == '__main__':
    # Se establece la conexion
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("localhost", 8000))
    
    # Se envia "hola"
    s.send("hola")
    
    # Se recibe la respuesta y se escribe en pantalla
    datos = s.recv(1000)
    print datos
    
    # Espera de 2 segundos
    time.sleep(2)
    
    # Se envia "adios"
    s.send("adios")
    
    # Se espera respuesta, se escribe en pantalla y se cierra la
    # conexion
    datos = s.recv(1000)
    print datos
    s.close()