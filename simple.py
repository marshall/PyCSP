import csp
import ctypes
import threading
import time

class SimpleServer(threading.Thread):
    PORT = 10
    def run(self):
        self.sock = csp.CspSocket()
        self.sock.bind(csp.CSP_ANY)
        self.sock.listen(10)
        self.running = True
        while self.running:
            self.iteration()

    def iteration(self):
        conn = self.sock.accept(1000)
        if not conn:
            return

        packet = conn.read(100)
        if packet:
            self.handle_packet(conn, packet)
        conn.close()

    def handle_packet(self, conn, packet):
        if conn.dport == self.PORT:
            print "Packet received on PORT: %s" % packet
            packet.erase()
        csp.service_handler(conn, packet)

class SimpleClient(threading.Thread):
    ADDRESS = 1
    def run(self):
        self.running = True
        while self.running:
            self.iteration()

    def iteration(self):
        time.sleep(0.3)
        result = csp.ping(self.ADDRESS, 100, 100, csp.CSP_O_NONE)
        print "Ping result %d [ms]" % result

        time.sleep(0.3)
        conn = csp.CspConnection(dest=self.ADDRESS, port=SimpleServer.PORT, timeout=1000)
        if not conn.send("Hello World", 1000):
            print "Send failed"

        conn.close()

def main():
    print "Initialising CSP"
    csp.buffer_init(2, 300)
    csp.init(SimpleClient.ADDRESS)
    csp.route_start_task(500, 1)

    print "Starting Server task"
    server = SimpleServer()
    server.start()

    print "Starting Client task"
    client = SimpleClient()
    client.start()

    try:
        server.join(10)
    except KeyboardInterrupt:
        server.running = client.running = False
        server.join()

if __name__ == "__main__":
    main()
