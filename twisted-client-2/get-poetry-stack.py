# This is the Twisted Get Poetry Now! client, version 2.0, with stacktrace.

# NOTE: This should not be used as the basis for production code.

import datetime, optparse, os, traceback

from twisted.internet.protocol import Protocol, ClientFactory


def parse_args():
    usage = """usage: %prog [options] [hostname]:port ...

This is the Get Poetry Now! client, Twisted version 2.0, with stacktrace.
Run it like this:

  python get-poetry-stack.py port1 port2 port3 ...

If you are in the base directory of the twisted-intro package,
you could run it like this:

  python twisted-client-2/get-poetry-stack.py 10001 10002 10003

But it's just going to print out a stacktrace as soon as it
gets the first bits of a poem.
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
            parser.error('Ports must be integers.')

        return host, int(port)

    return map(parse_address, addresses)


class PoetryProtocol(Protocol):

    poem = ''
    task_num = 0

    def dataReceived(self, data):
        # err log:
        # File: .../twisted/internet/tcp.py line 463, in doRead # Note the doRead callback return self.protocol.dataReceived(data)
        #  有我们在1.0版本客户端的doRead回调函数
        # 我们前面也提到过，Twisted在建立新抽象层进会使用已有的实现而不是另起炉灶
        # 因此必然会有一个IReadDescriptor的实例在辛苦的工作，它是由Twisted代码而非我们自己的代码来实现 
        # 如果你表示怀疑，那么就看看twisted.internet.tcp中的实现吧。如果你浏览代码会发现，由同一个类实现了IWriteDescriptor与ITransport。
        # 因此 IreadDescriptor实际上就是变相的Transport类
        traceback.print_stack()
        os._exit(0)

    def connectionLost(self, reason):
        self.poemReceived(self.poem)

    def poemReceived(self, poem):
        self.factory.poem_finished(self.task_num, poem)


class PoetryClientFactory(ClientFactory):

    task_num = 1

    protocol = PoetryProtocol # tell base class what proto to build

    def __init__(self, poetry_count):
        self.poetry_count = poetry_count
        self.poems = {} # task num -> poem

    def buildProtocol(self, address):
        proto = ClientFactory.buildProtocol(self, address)
        proto.task_num = self.task_num
        self.task_num += 1
        return proto

    def poem_finished(self, task_num=None, poem=None):
        if task_num is not None:
            self.poems[task_num] = poem

        self.poetry_count -= 1

        if self.poetry_count == 0:
            self.report()
            from twisted.internet import reactor
            reactor.stop()

    def report(self):
        for i in self.poems:
            print 'Task %d: %d bytes of poetry' % (i, len(self.poems[i]))

    def clientConnectionFailed(self, connector, reason):
        print 'Failed to connect to:', connector.getDestination()
        self.poem_finished()


def poetry_main():
    addresses = parse_args()

    start = datetime.datetime.now()

    factory = PoetryClientFactory(len(addresses))

    from twisted.internet import reactor

    for address in addresses:
        host, port = address
        reactor.connectTCP(host, port, factory)

    reactor.run()

    elapsed = datetime.datetime.now() - start

    print 'Got %d poems in %s' % (len(addresses), elapsed)


if __name__ == '__main__':
    poetry_main()
