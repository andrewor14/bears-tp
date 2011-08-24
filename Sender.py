import sys
import socket
import random
import getopt

import Checksum

'''
This is a skeleton sender class. Replace as necessary to create a fantastic
transport protocol. The provided implementation does not provide any
reliability; it's just an example of how to read from a file and send a packet
in our format.
'''
class Sender():
    def __init__(self,dest,port,filename):
        self.dest = dest
        self.dport = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('',random.randint(10000,40000)))
        if filename == None:
            self.infile = sys.stdin
        else:
            self.infile = open(filename,"r")
        
    # Waits until packet is received to return.
    def receive(self):
        return self.sock.recv(4096)

    # Sends a packet to the destination address.
    def send(self, message):
        self.sock.sendto(message, (self.dest,self.dport))

    # Prepares a packet
    def make_packet(self,msg_type,seqno,msg):
        body = "%s|%d|%s|" % (msg_type,seqno,msg)
        checksum = Checksum.generate_checksum(body)
        packet = "%s%s" % (body,checksum)
        return packet

    # Handles a response from the receiver. 
    def handle_response(self,response_packet):
        if Checksum.validate_checksum(response_packet):
            print "recv: %s" % response_packet
        else:
            print "recv: %s <--- CHECKSUM FAILED" % response_packet

    # Main sending loop. 
    def start(self):
        seqno = 0
        msg = self.infile.read(500)
        msg_type = None
        while not msg_type == 'end':
            next_msg = self.infile.read(500)

            msg_type = 'data'
            if seqno == 0:
                msg_type = 'start'
            elif next_msg == "":
                msg_type = 'end'

            packet = self.make_packet(msg_type,seqno,msg)
            self.send(packet)
            print "sent: %s" % packet

            response = self.receive()
            self.handle_response(response)
           
            msg = next_msg
            seqno += 1

        self.infile.close()

'''
This will be run if you run this script from the command line. You should not
need to change any of this.
'''
if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv[1:], 
                               "f:p:d:", ["file=", "port=", "dest="])

    def usage():
        print "BEARS-TP Sender"
        print "-f FILE | --file=FILE The file to transfer; if empty reads from STDIN"
        print "-p PORT | --port=PORT The destination port, defaults to 33122"
        print "-d ADDRESS | --dest=ADDRESS The receiver address or hostname, defaults to localhost"
        print "-h | --help Print this usage message"

    port = 33122
    dest = "localhost"
    filename = None

    for o,a in opts:
        if o in ("-f", "--file="):
            filename = a
        elif o in ("-p", "--port="):
            port = int(a)
        elif o in ("-d", "--dest="):
            dest = a
        else:
            print usage()
            exit()

    s = Sender(dest,port,filename)
    s.start()
