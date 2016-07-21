import socket, os, threading
from math import ceil

DST_IP = "127.0.0.1"
DST_PORT = 9090
CNK_Size = 100000


class PyWDT():
    def __init__():
        pass
    def send(tgtIP, tgtPort):
        s = socket.socket()
        s.connect((tgtIP, tgtPort))
        to_send = ""
        while True:
            to_send = input().encode('utf-8')
            s.send(to_send)

    def sendFile(tgtIP, tgtPort, fileName):
        # må først sende metadata, slik at mottaker kan sette opp lyttere
        fileSize = os.stat(fileName).st_size
        numParts = ceil(fileSize / CNK_Size)
        s = socket.socket()
        s.connect((tgtIP, tgtPort))
        print(str(numParts))
        s.send(str(numParts).encode('utf-8'))
        r = ""
        while not "Ready" in r:
            r = s.recv(1024).decode()
        file = open(fileName, 'rb')
        senders = []
        for offset in range(0, numParts):
            part = file.read(CNK_Size)
            sender = Sender(tgtIP, tgtPort, part, offset + 1)
            sender.start()
            senders.append(sender)
        file.close()
        for t in senders:
            t.join()
        print("Sending done")
    def recieve(lPort):
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("", lPort))
        s.listen()
        r = ""
        rs, ra = s.accept()
        while True:
            r = rs.recv(4096).decode()
            print(r)
    def recieveFile(outFile):
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("", DST_PORT))
        s.listen()
        r = ""
        rs, ra = s.accept()
        r = rs.recv(1024).decode()
        print(r)
        numParts = int(r)
        recievers = []
        for o in range(0, numParts):
            reciever = Reciever(DST_PORT, o + 1)
            reciever.start()
            recievers.append(reciever)
        rs.send("Ready".encode('utf-8'))
        rs.close()
        print("Ready sent")
        counter = 0
        while False in [t.done for t in recievers]:
            counter += 1
        with open(outFile, "wb") as of:
            for t in recievers:
                of.write(t.part)
        print("Done, counter whent to: " + str(counter))

class Sender(threading.Thread):
    def __init__(self, tgtIP, tgtPort, part, offset):
        threading.Thread.__init__(self)
        self.tgtIP = tgtIP
        self.tgtPort = tgtPort
        self.part = part
        self.offset = offset
    def run(self):
        soc = socket.socket()
        soc.connect((self.tgtIP, self.tgtPort + self.offset))
        soc.send(self.part)
        soc.close()
class Reciever(threading.Thread):
    def __init__(self, bPort, offset):
        threading.Thread.__init__(self)
        self.bPort = bPort
        self.offset = offset
        self.part = ""
        self.done = False
    def run(self):
        soc = socket.socket()
        soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        soc.bind(("", self.bPort + self.offset))
        soc.listen(1)
        rs, ra = soc.accept()
        self.part = rs.recv(CNK_Size)
        rs.close()
        soc.close()
        self.done = True
