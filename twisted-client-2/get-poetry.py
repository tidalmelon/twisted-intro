# This is the Twisted Get Poetry Now! client, version 2.0.

# NOTE: This should not be used as the basis for production code.

import datetime, optparse

from twisted.internet.protocol import Protocol, ClientFactory


def parse_args():
    usage = """usage: %prog [options] [hostname]:port ...

This is the Get Poetry Now! client, Twisted version 2.0.
Run it like this:

  python get-poetry.py port1 port2 port3 ...

If you are in the base directory of the twisted-intro package,
you could run it like this:

  python twisted-client-2/get-poetry.py 10001 10002 10003

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
            parser.error('Ports must be integers.')

        return host, int(port)

    return map(parse_address, addresses)


class PoetryProtocol(Protocol):
    
    # 每建立一个Transport都需要一个协议实例。
    # Protocol实例是存储协议状态与间断性接收并累积数据的地方。
    poem = ''
    task_num = 0

    def dataReceived(self, data):
        self.poem += data
        msg = 'Task %d: got %d bytes of poetry from %s'
        print  msg % (self.task_num, len(data), self.transport.getPeer())

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
    	# 我们在子类中调用基类中的实现。基类怎么会知道我们创建什么样的Protocol呢？
    	# protocol = PoetryProtocol # tell base class what proto to build
	# 基类Factory的实现buildProtocol过程是：
	# 1. 安装设置在PoetryClientFacotry.protocol的Protocol类
	# 2. 并在上述实例的self.factory属性上设置一个产生它的Factory引用。
	# 正如我们提到的那样，位于Protocol实例的factory属性字段允许在都由同一个factory
	# 产生的Protocol之间共享数据。
	# 由于factory都是由用户代码来创建的（在用户控制中）因此这个属性也可以
	# Protocol对象将数据传递回一开始初始化请求的代码中。
	# 工厂里有要生产的协议：PoetryProtocol（Class Type）
	# PoetryProtocl实例有工厂类的实例。
	# 各个连接可以通过**factory共享数据**

	# Protocol创立后的第二步：通过makeConnection与Transport联系起来。
	# 我们无需自己来实现这个函数，而是使用twisted的默认实现。
	# 默认情况是：makeConnection将Transport的一个引用赋给(Protocol的）protocol.self.transport属性。
	# 同时置protocol.self.connected=True

	# 一旦初始化到这一步后，Protocol开始其真正的工作：将底层的数据流翻译成高层的协议规定格式的消息
	# 处理接收到的数据的主要方法是dataReceived(self, data)

	# 每次dataReveived被调用就意味着我们得到一个新字符串。由于与异步IO交互，我们不知道能接收
	# 到多少数据，因此**将接收到的数据缓存下来直到完成一个完整的协议规定的格式**。

	# 我们使用了Transport的getHost(peer)方法获取数据来自的服务器信息。我们这样做只是与
	# 前面的客户端保持一致。相反我们的代码没有必要这样做。因为我们没有向服务器发送任何消息。
	# 也没有必要知道服务器的任何信息了。
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

    # socket不会出现了
    for address in addresses:
        host, port = address
	# factory是针对诗歌下载客户端的PoetryClientFactory，将其传给reactor，可以让
	# twisted为我们创建一个PeotryProtocol实例。
        reactor.connectTCP(host, port, factory)

    reactor.run()

    elapsed = datetime.datetime.now() - start

    print 'Got %d poems in %s' % (len(addresses), elapsed)


if __name__ == '__main__':
    poetry_main()
