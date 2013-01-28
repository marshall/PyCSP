# A higher level wrapper around the native libcsp bindings
import ctypes
import time
from libcsp import *

def buffer_init(count, size):
    return csp_buffer_init(count, size)

def init(my_node_address):
    return csp_init(my_node_address)

def route_start_task(task_stack_size, priority):
    return csp_route_start_task(task_stack_size, priority)

def ping(node, timeout, size, options):
    return csp_ping(node, timeout, size, options)

def service_handler(conn, packet):
    csp_service_handler(conn.conn, packet.packet)

class CspSocket(object):
    def __init__(self, options=CSP_SO_NONE, _sock=None):
        self.sock = _sock or csp_socket(options)

    def bind(self, port):
        return csp_bind(self.sock, port)

    def listen(self, max_clients):
        return csp_listen(self.sock, max_clients)

    def accept(self, timeout):
        conn = csp_accept(self.sock, ctypes.c_uint(timeout))
        return CspConnection(None, None, _conn=conn)

class CspPacket(object):
    def __init__(self, length=-1, data=None, _packet=None):
        length += csp_packet_t.CSP_BUFFER_PACKET_OVERHEAD
        self.packet = _packet or ctypes.cast(csp_buffer_get(length),
                                             ctypes.POINTER(csp_packet_t))
        if data:
            self.data = data

    @property
    def id(self):
        return self.packet.id.id

    @property
    def data(self):
        return ctypes.cast(self.packet.contents.data, ctypes.c_char_p).value

    @data.setter
    def data(self, value):
        self.packet.contents.data = ctypes.cast(ctypes.c_char_p(value),
                                                ctypes.POINTER(ctypes.c_uint8))
        self.packet.contents.length = len(value) if value else 0

    def erase(self):
        csp_buffer_free(self.packet)

    def __getitem__(self, item):
        return self.packet.contents.data[item]

    def __len__(self):
        return self.packet.contents.length

    def __str__(self):
        return ctypes.cast(self.packet.contents.data, ctypes.c_char_p).value

class CspConnection(object):
    def __init__(self, dest, port, timeout=-1, prio=CSP_PRIO_NORM,
                 options=CSP_O_NONE, _conn=None):
        self.conn = _conn or csp_connect(prio, dest, port, timeout, options)

    def close(self):
        return csp_close(self.conn)

    @property
    def dport(self):
        return csp_conn_dport(self.conn)

    @property
    def sport(self):
        return csp_conn_sport(self.conn)

    @property
    def dst(self):
        return csp_conn_dst(self.conn)

    @property
    def src(self):
        return csp_conn_src(self.conn)

    @property
    def flags(self):
        return csp_conn_flags(self.conn)

    def read(self, n):
        packet = csp_read(self.conn, n)
        if packet:
            return CspPacket(_packet=packet)
        else: return None

    def send(self, data, timeout):
        packet = data
        if not isinstance(data, CspPacket):
            packet = CspPacket(length=len(data), data=data)

        return csp_send(self.conn, packet.packet, timeout)
