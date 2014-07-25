#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import time
from innovex.configuration import Configuration

def read():
    #log = open("/var/log/enviroview/oxigeno.log", "r")
    log = open("oxigeno.log", "r")
    cf = Configuration()
    print log.read(5), cf.key
    #while True:
    #    line = log.readline()
    #    if not line: break
    #    if "Calibra" in line and "exitosamente" in line:

if __name__ == '__main__':
    # Se establece la conexion
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("localhost", 8000))
    
    errors = {"unable to open serial port": 1, 
              "data whit errors": 2,
              "****": 3}


    #crear bluque para enviar cada 10 min hasta que reciba respuesta del server

    # Se envia "hola"
    s.send("hola")
    
    # Se recibe la respuesta y se escribe en pantalla
    datos = s.recv(1000)
    print datos
    
    
    s.close()