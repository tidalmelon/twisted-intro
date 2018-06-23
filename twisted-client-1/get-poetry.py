# -*- coding: utf-8 -*-

import datetime, errno, optparse, socket

from twisted.internet import main


def parse_args():
    usage = """usage: %prog [options] [hostname]:port ...

This is the Get Poetry Now! client, Twisted version 1.0.
Run it like this:

  python get-poetry.py port1 port2 port3 ...

If you are in the base directory of the twisted-intro package,
you could run it like this:

  python twisted-client-1/get-poetry.py 10001 10002 10003

to grab poetry from servers on ports 10001, 10002, and 10003.

Of course, there need to be servers listening on those ports
for that to work.
"""

    parser = optparse.OptionParser(usage)
    _, addresses = parser.parse_args()

    if not addresses:
        print parser.format_help()
        parser.exit()

    def parse_address(addr):
        if ':' not in addr:
            host = '127.0.0.1'
            port = addr
        else:
            host, port = addr.split(':', 1)

        if not port.isdigit():
            parser.error('ports must be integers.')
        return host, int(port)

    return map(parse_address, addresses)

    
class PoetrySocket(object):

    poem = ''

    def __init__(self, task_num, address):
        self.task_num = task_num
        self.address = address
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(address)
        self.sock.setblocking(0)

        from twisted.internet import reactor
        reactor.addReader(self)

    def fileno(self):
        try:
            return self.sock.fileno()
        except socket.error:
            return -1

    def connectionLost(self, reason):
        self.sock.close()
        
        from twisted.internet import reactor
        reactor.removeReader(self)

        for reader in reactor.getReaders():
            if isinstance(reader, PoetrySocket):
                return

        reactor.stop()

    def doRead(self):
        bytes = ''

        while True:
            try:
                bytesread = self.sock.recv(1024)
            else:
                pass






































