import sys
import os
import socket
import time
import threading
import logging
from contextlib import closing
from NaiveRPC import utils
from concurrent.futures import ThreadPoolExecutor

ThreadLock=threading.RLock()


class Server(object):
    """
    Base server.
    """

    def __init__(self, host, port, ipv6=False,authenticator=None,backlog=1):
        hostname = host
        portname = port
        self.logger = logging.getLogger("%s/%s" % (hostname, portname))
        self.clients=set()
        self.active=False
        self.backlog=backlog
        self._closed = False
        self.authenticator = authenticator
        if ipv6:
            family = socket.AF_INET6
        else:
            family = socket.AF_INET
        self.listener = socket.socket(family, socket.SOCK_STREAM)
        address = socket.getaddrinfo(hostname, portname, family=family, type=socket.SOCK_STREAM, proto=socket.IPPROTO_TCP)[0][-1]
        self.listener.bind(address)
        sockname = self.listener.getsockname()
        self.host, self.port = sockname[0], sockname[1]

    def close(self):
        """Closes (terminates) the server and all of its clients."""
        if self._closed:
            return
        self._closed = True
        self.active = False
        try:
            #why shut down
            self.listener.shutdown(socket.SHUT_RDWR)
        except (EnvironmentError, socket.error):
            pass
        self.listener.close()
        for c in set(self.clients):
            try:
                c.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            c.close()
        self.clients.clear()
        self.logger.info('[SERVER] {}:{} [CL] Closed'.format(self.host,self.port))
        print('[SERVER] {}:{} [CL] Closed'.format(self.host,self.port))
        

class OneTimeServer(Server):
    pass


class ThreadServer(Server):
    def __init__(self, host, port, ipv6=False,authenticator=None,backlog=5, FunctionPool=None, password=None):
        super().__init__(host=host,port=port,ipv6=ipv6,backlog=backlog)
        self.active_threads={
            'connections':{}
        }
        self.FunctionPool=FunctionPool
        self.authenticated=False
        self.password=password

    def start(self):
        """Starts the server (blocking)."""
        if self.active:
            return
        self.listener.listen(self.backlog)
        self.active = True

        self.logger.info('[SERVER] {}:{} [ST] Started'.format(self.host,self.port))
        print('[SERVER] {}:{} [ST] Started'.format(self.host,self.port))

        try:
            while self.active:
                conn, address=self.listener.accept()
                client_ip,client_port=str(address[0]), str(address[1])
                try:
                    new_thread=threading.Thread(target=utils.ThreadServer_Process,
                        args=(
                        conn,
                        client_ip,
                        client_port,
                        self.active_threads,
                        self.FunctionPool,
                        self.authenticated,
                        self.password
                        ),
                        daemon=False
                    )
                    ThreadLock.acquire()
                    self.active_threads['connections'][client_port] = {
                        'thread': new_thread,
                        'ip': client_ip,
                        'state': 0
                    }
                    ThreadLock.release()
                    new_thread.start()

                    ThreadLock.acquire()
                    for c in self.active_threads['connections'].keys():
                        if self.active_threads['connections'][c]['thread'].is_alive():
                            print("[CLIENT] {i}:{p} [CN] Connected".format(i=client_ip, p=client_port))
                            self.logger.info("[CLIENT] {i}:{p} [CN] Connected".format(i=client_ip, p=client_port))
                    ThreadLock.release()

                except Exception as e:
                    print("WARN: Could not serve new thread for client {i}.".format(i=client_ip))
                    self.logger.warning("[CLIENT] Could not serve new thread for client {i}".format(i=client_ip))
                    print(e)
        except EOFError:
            pass  # server closed by another thread
        except KeyboardInterrupt:
            print("KeyBoard Interrupt")
            self.logger.warn("[SERVER] {}:{} Keyboard interrupt!".format(self.host,self.port))
        finally:
            self.logger.info("[SERVER] {}:{} Server terminated".format(self.host,self.port))
            self.close()


class ThreadPoolServer(Server):
    def __init__(self, host, port, ipv6=False,authenticator=None,backlog=5, FunctionPool=None, password=None):
        super().__init__(host=host,port=port,ipv6=ipv6,backlog=backlog)
        #max_workers is None or not given, it will default to the number of processors on the machine,
        # here set it equal to the value of backlog
        self.pool=ThreadPoolExecutor(max_workers=backlog)
        self.FunctionPool=FunctionPool
        self.authenticated=False
        self.password=password

        
    def start(self):
        if self.active:
            return
        #backlog parameter specifies the number of pending connections the queue will hold.
        self.listener.listen(self.backlog)
        self.active = True
        self.logger.info('[SERVER] {}:{} [ST] Started'.format(self.host,self.port))
        print('[SERVER] {}:{} [ST] Started'.format(self.host,self.port))
        try:
            while self.active:
                conn, address=self.listener.accept()
                self.pool.submit(utils.ThreadPool_Process,conn,address, self.FunctionPool, self.authenticated, self.password)
                client_ip,client_port=str(address[0]), str(address[1])
                print("[CLIENT] {i}:{p} [CN] Connected".format(i=client_ip, p=client_port))
                self.logger.info("[CLIENT] {i}:{p} [CN] Connected".format(i=client_ip, p=client_port))

        except Exception as e:
            print(e)  # server closed by another thread
        except KeyboardInterrupt:
            print("[SERVER] {}:{} KeyBoard Interrupt!".format(self.host,self.port))
            self.logger.warn("[SERVER] {}:{} Keyboard interrupt!".format(self.host,self.port))
        finally:
            print("[SERVER] {}:{} Server terminated.".format(self.host,self.port))
            self.logger.info("[SERVER] {}:{} Server terminated.".format(self.host,self.port))
            self.close()
