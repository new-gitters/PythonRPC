import socket 
import sys 
from NaiveRPC import utils

class Client(object):
    def __init__(self,ipv6=False):
        if ipv6:
            family = socket.AF_INET6
        else:
            family = socket.AF_INET

        self.sock = socket.socket(family, socket.SOCK_STREAM)

    def connect(self,host=None, port=None):
        self.server_address = (host, port)
        self.sock.connect(self.server_address)

    def close(self):
        self.sock.close()

    def request(self, data):
        try:
            data = "[RE]" + data  # for request
            utils.sendJson(self.sock,data)
            data=utils.receiveJson(self.sock)
            print(data)
        finally:
            pass

    def execute(self, data, silent=False):
        try:
            data = "[EX]" + data  # for execute
            utils.sendJson(self.sock,data)
            data=utils.receiveJson(self.sock)
            if not silent:
                print(data)
            return data
        finally:
            pass
    
    def authenticate(self, data):
        try:
            data = "[PW]" + data  # for password
            utils.sendJson(self.sock,data)
            data=utils.receiveJson(self.sock)
            print(data)
        finally:
            pass

    #some grammar sugars
    def print(self):
        return self.request("print")

    def print_all(self):
        return self.request("print_all")