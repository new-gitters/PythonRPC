import threading
import sys
import json
import socket
import logging
import inspect
from types import FunctionType

from .crypto import encrypt, decrypt

ThreadLock = threading.RLock()

# password for communication
# used by send/receiveJson
COM_PASSWORD = "RutgersUniversity"

# password for sever's password
# used by thread server and threadpool server
PASS_PASSWORD = "ComputerScience"

def receiveJson(socket):

    # read the length of the data, letter by letter until we reach EOL
    length_str = ''
    char = socket.recv(1).decode('utf_8')

    if not char:  #If the socket is closed, return None
        return None

    while char != '\n':
        length_str += char
        char = socket.recv(1).decode('utf_8')
    total = int(length_str)
    # use a memoryview to receive the data chunk by chunk efficiently
    view = memoryview(bytearray(total))
    next_offset = 0
    while total - next_offset > 0:
        recv_size = socket.recv_into(view[next_offset:], total - next_offset)
        next_offset += recv_size
    try:
        deserialized = json.loads(view.tobytes())
    except (TypeError, ValueError):
        raise Exception('Data received was not in JSON format')
    plain_text = decrypt(deserialized, COM_PASSWORD)
    return plain_text.decode("utf-8")


def sendJson(socket, data):
    try:
        data = encrypt(data, COM_PASSWORD)
        serialized = json.dumps(data)
    except (TypeError, ValueError):
        raise Exception('You can only send JSON-serializable data')
    # send the length of the serialized data first
    socket.send(bytes('%d\n' % len(serialized),'UTF-8'))
    # send the serialized data
    socket.sendall(bytes(serialized,'UTF-8'))


class ThreadPool_Process():
    def __init__(self,conn,address, FunctionPool, authenticated, password):
        self.logger=logging.getLogger()
        self.conn = conn
        self.address = address
        self.FunctionPool = FunctionPool
        self.socket_state = True
        self.password=encrypt(password, PASS_PASSWORD)
        self.authenticated=authenticated
        self.ip = self.address[0]
        self.port = self.address[1]
        self.run()
        
    def run(self):
        while self.socket_state:
            raw_data=receiveJson(self.conn)
            if raw_data==None:
                self.socket_state=False
                break
            
            header = raw_data[:4]  # [RE]/[EX] header, and maybe more
            data = raw_data[4:]

            if header == "[PW]":
                if str(data) == decrypt(self.password, PASS_PASSWORD).decode("utf-8"):
                    self.authenticated = True
                    print("[CLIENT] {}:{} [AT] Authenticated".format(self.ip, self.port))
                    self.logger.info("[CLIENT] {}:{} [AT] Authenticated".format(self.ip, self.port))
                    sendJson(self.conn, "Authenticated")
                else:
                    self.authenticate = False
                    print("[CLIENT] {}:{} [AF] Authentication failure".format(self.ip, self.port))
                    self.logger.warning("[CLIENT] {}:{} [AF] Authentication failure".format(self.ip, self.port))
                    sendJson(self.conn, "Authentication Failure")
            elif self.authenticated:
                msg = self.process(header, data)
                sendJson(self.conn, str(msg))
            else:
                msg = "Please authenticate first"
                sendJson(self.conn, msg)
                self.close_socket
        
        self.close_socket()

    # The general method
    def process(self, header, data):
        if header == "[RE]":  # request
            if data == "print":
                print("[CLIENT] {}:{} [RE] print".format(self.ip, self.port))
                self.logger.info("[CLIENT] {}:{} [RE] print".format(self.ip, self.port))
                return self.FunctionPool.examine(detailed=False, return_msg=True)
            elif data == "print_all":
                print("[CLIENT] {}:{} [RE] print_all".format(self.ip, self.port))
                self.logger.info("[CLIENT] {}:{} [RE] print_all".format(self.ip, self.port))
                return self.FunctionPool.examine(detailed=True, return_msg=True)
            else:
                print("[CLIENT] {}:{} [RE] format problem".format(self.ip, self.port))
                self.logger.info("[CLIENT] {}:{} [RE] format problem".format(self.ip, self.port))
                help_msg = "[RE] print, print_all, pleae check your input format"
                return help_msg
        elif header == "[EX]":  # execute
            print("[CLIENT] {}:{} [EX] {}".format(self.ip, self.port, data))
            self.logger.info("[CLIENT] {}:{} [EX] {}".format(self.ip, self.port, data))
            return self.execute_function(data)
        else:
            help_msg = "[RE] request, [EX] execute, please check your input format"
            return help_msg

    def execute_function(self, request):
        print(request)

        # This is not a function call
        if (not '(' in request) or (request[-1] != ')'):
            return "Please check your execution command."

        request = request[:-1] + ",)" # important, make it a tuple
        function_name = request.split("(")[0]

        print(request)
        print(function_name)

        if request.split("(")[1][:-1] == ',':
            args = ""
        else:
            args = eval(request.split("(")[1][:-1])
        
        return self.FunctionPool.call(function_name, *args)

    def close_socket(self):
        try:
            self.conn.shutdown(socket.SHUT_RDWR)
        
        except Exception:
            pass
        self.conn.close()


class ThreadServer_Process(object):
    def __init__(self,conn, ip, port, active_threads, FunctionPool, authenticated, password):
        self.logger=logging.getLogger()
        self.conn=conn
        self.ip=ip  # client_ip
        self.port=port  # client_port
        self.active_threads=active_threads  #pass the dictionary to the thread,
        self.service_name = "{u}:{p}".format(u=ip, p=port)
        self.lock=ThreadLock
        self.socket_state=True
        self.FunctionPool=FunctionPool
        self.authenticated=authenticated
        self.password=encrypt(password, PASS_PASSWORD)
        self.run()

    def LOCK(self):
        if self.lock.acquire():
            return True
        else:
            return False

    def UNLOCK(self):
        self.lock.release()

    def run(self):
        while self.socket_state:
            raw_data=receiveJson(self.conn)
            if raw_data==None:
                self.socket_state=False
                break
        
            header = raw_data[:4]  # [RE]/[EX]/[PW] header, and maybe more
            data = raw_data[4:]

            if header == "[PW]":
                if str(data) == decrypt(self.password, PASS_PASSWORD).decode("utf-8"):
                    self.authenticated = True
                    print("[CLIENT] {}:{} [AT] Authenticated".format(self.ip, self.port))
                    self.logger.info("[CLIENT] {}:{} [AT] Authenticated".format(self.ip, self.port))
                    sendJson(self.conn, "Authenticated")
                else:
                    self.authenticate = False
                    print("[CLIENT] {}:{} [AF] Authentication failure".format(self.ip, self.port))
                    self.logger.warning("[CLIENT] {}:{} [AF] Authentication failure".format(self.ip, self.port))
                    sendJson(self.conn, "Authentication failure")
            elif self.authenticated:
                msg = self.process(header, data)
                sendJson(self.conn, str(msg))
            else:
                msg = "Please authenticate first"
                sendJson(self.conn, msg)
                self.close_socket
        
        self.close_socket()

    # The general method
    def process(self, header, data):
        if header == "[RE]":  # request
            if data == "print":
                print("[CLIENT] {}:{} [RE] print".format(self.ip, self.port))
                self.logger.info("[CLIENT] {}:{} [RE] print".format(self.ip, self.port))
                return self.FunctionPool.examine(detailed=False, return_msg=True)
            elif data == "print_all":
                print("[CLIENT] {}:{} [RE] print all".format(self.ip, self.port))
                self.logger.info("[CLIENT] {}:{} [RE] print all".format(self.ip, self.port))
                return self.FunctionPool.examine(detailed=True, return_msg=True)
            else:
                print("[CLIENT] {}:{} [RE] format problem".format(self.ip, self.port))
                self.logger.info("[CLIENT] {}:{} [RE] format problem".format(self.ip, self.port))
                help_msg = "[RE] print, print_all, pleae check your input format"
                return help_msg
        elif header == "[EX]":  # execute
            print("[CLIENT] {}:{} [EX] {}".format(self.ip, self.port, data))
            self.logger.info("[CLIENT] {}:{} [EX] {}".format(self.ip, self.port, data))
            return self.execute_function(data)
        else:
            help_msg = "[RE] request, [EX] execute, please check your input format"
            return help_msg

    def execute_function(self, request):

        # This is not a function call
        if (not '(' in request) or (request[-1] != ')'):
            return "Please check your execution command."
            
        request = request[:-1] + ",)" # important, make it a tuple
        function_name = request.split("(")[0]

        if request.split("(")[1][:-1] == ',':
            args = ""
        else:
            args = eval(request.split("(")[1][:-1])
        
        return self.FunctionPool.call(function_name, *args)

    def close_socket(self):
        try:
            self.conn.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass

        self.conn.close()
