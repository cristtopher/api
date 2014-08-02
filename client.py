#!/usr/bin/env python
# -*- coding: utf-8 -*-

# sudo apt-get install gtk2-engines-pixbuf

import sys
from datetime import *
import datetime
import pynotify
import gtk
from dateutil import rrule
import socket
import time
import serial
import glob
import shutil
import os
from innovex.configuration import Configuration


# Chek local problems.

def notify(title, msg, icon=None):
    if not pynotify.is_initted():
        pynotify.init(title)
        gtk_icon = {'ok':gtk.STOCK_YES, 'info':gtk.STOCK_DIALOG_INFO,
                'error':gtk.STOCK_DIALOG_ERROR, 'warm':gtk.STOCK_DIALOG_WARNING,
                'ask':gtk.STOCK_DIALOG_QUESTION, 'sync':gtk.STOCK_JUMP_TO}
    try:
        note = pynotify.Notification(title, msg)
        helper = gtk.Button()
        gtk_icon = helper.render_icon(gtk_icon[icon], gtk.ICON_SIZE_BUTTON)
        note.set_icon_from_pixbuf(gtk_icon)
    except KeyError:
        note = pynotify.Notification(title, msg, icon)
    note.show()


def estation(today):
    #verano=21/9 al 20/3 -> 7 dias
    #invierno=21/3 al 20/9 -> 15 dias
    #today.year ver si imprimer bien el año y colocar abajo
    if time.strptime('21/03/2014', '%d/%m/%Y') <= \
        time.strptime(today.strftime("%d/%m/%Y"), '%d/%m/%Y') <= \
        time.strptime('20/09/2014', '%d/%m/%Y'):
        return 15
    else:
        return 7


def get_ftdi():
    return glob.glob('/dev/serial/by-id/*')


def set_ftdi_port(cfg):
    if get_ftdi() != []:
        for name in get_ftdi():
            if name.startswith('/dev/serial/by-id/usb-FTDI'):
                port = name
        if not cfg.serialport is port:
            os.system('sudo aduser innovex dialout')
        else:
            cfg.serialport = port # Set real port with id of FTDI.
    else:
        print 'Antena receptora no detectada.'


def check_comunication(cfg):
    serial_port = serial.Serial(cfg.serialport,
    baudrate=cfg.baudrate, timeout=0.3)
    if serial_port.isOpen():
        while 1:
            try:
                data = serial_port.read(serial_port.inWaiting())
                if not l:
                    continue
                print data
            except(IOError):
                print "Error whit serial comucation"
        serial_port.close()
    else:
        check_serial_port(cfg)
        check_comunication(cfg) # Recursivity


def repare_db(cfg):
    db = cfg.get('Database', 'dbname')
    d = date.today()
    if os.path.isfile(db):
        shutil.move(db, db + '.%s%s%s' % (d.day, d.month, d.year))
        os.system('create_tables')
    if os.path.isfile(db + '.%s%s%s' % (d.day, d.month, d.year)):
        print "Base de datos reparada"
        # que pasa ahora, ¿deberia enviar al server este mensaje? y que mas?


def check_vpn():
    pass


# Chek local problems without autoresolve.

def read_log(cfg):
    try:
        flag = 0
        log = open("/var/log/enviroview/oxigeno.log", "r")
        #log = open("oxigeno.log", "r") # log with many data
        
        # Check for calibration
        needCalibra=0
        today = datetime.datetime.now()
        while True:
            line = log.readline()
            if not line: break
            if "Calibra" in line and "exitosamente" in line:
                list = line.split()
                month = {"Jan":1, "Feb":2, "Mar":3, "Apr":4, "May":5, "Jun":6, "Jul":7,
                        "Aug":8, "Sep":9, "Oct":10, "Nov":11, "Dec":12}
                calibra = list[1] + "/" + str(month[list[2]]) + "/" + list[3]
                if time.strptime(calibra, '%d/%m/%Y') <= time.strptime((today - \
                    datetime.timedelta(days=estation(today))).strftime("%d/%m/%Y"), 
                    '%d/%m/%Y'):
                    needCalibra=needCalibra+1
                else:
                    needCalibra=0
            else:
                notify("Advertencia", "Sin registros de calibraciones", "warm")
        if needCalibra > 0:
            notify("Advertencia", "Hace más de %i días que los sensores innovex no han sido calibrados, favor de calibrar lo antes posible" % (estation(today)) , "warm")
            return (cfg.key, "Need Calibration")
        else:
            pass

        # Check for problems
        errors = ["Unable to open serial port",
                  "Received data with errors",
                  "attempt to write a readonly database"]
        file_lines = log.readlines()
        log.close () 
        last_line = file_lines[len(file_lines)-1]
        for i in range(len(errors)):
            if errors[i] in last_line:
                flag = i + 1
        if flag is 1:
            set_ftdi_port(cfg)
            #break
            sys.exit()
        #log.read() #posiciona el cursor de lectura al final del fichero, al ''
        #print log.readline()

        #print log.read(5), cf.key
        #while True:
        #    line = log.readline()
        #    if not line: break
        #    if "Calibra" in line and "exitosamente" in line:
        #    time.sleep(60)
        #return cf.key
        if flag is 0:
            return (None, None)
        else:
            return (cfg.key, str(flag))
    except(IOError):
            print 'El archivo /etc/innovex.cfg no se encuentra.'

if __name__ == '__main__':
    if not os.path.exists('~/.api'):
        os.mkdir('~/.api')
    server = '192.168.23.9'
    port = 8000
    try:
        fp = open('/etc/innovex.cfg')
        cfg = Configuration(fp)
        if os.system("ping -c 1 -p %i %s" % port, server) == 0:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Comuncation establecida
            s.connect((server, port))
            s.send(read_log(cfg)) # Send tuple message.
            datos = s.recv(1024) # Reponse from server.
            print datos
            s.close()
        # resolver problemas locales abajo
        if not os.geteuid() is 0:
            print 'Ejecutar con sudo!'
            sys.exit(1)
        else:
            #Cheking conectivity whit *wise
            set_ftdi_port(cfg)
            check_comunication(cfg)
            check_vpn(cfg)
    except(IOError):
        sys.exit() # without cfg
