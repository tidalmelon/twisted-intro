twisted-1的提升空间：
1. 客户端竟然有创建网络端口并接收数据这样枯燥的代码，twisted理应为我们实现这些例程性功能, 
   不必我们每写一个新程序都自己去实现。
2. 异常处理，如果从一个未提供诗歌服务的机器下载诗歌时，程序会崩溃。 
3. 不能复用，如果另一个模块需要通过我们的客户端下载诗歌呢？人家怎么知道你的诗歌下载完毕？ 
   我们不能简单的将一首诗歌下载好后再传给人家，而在之前让人处于等待状态。【在未来部分我们会解决这个问题】


reactor是核心。
实际上，twisted的其他部分(即除了reactor循环体)可以这样理解：他们都是辅助X更好的使用reactor。这里的
X可以提供web网页，处理一个数据库查询请求或其他更加具体的内容。


Transports：
一个twisted的Transport代表一个可以收发字节的单条连接。
处理具体的异步IO操作。
1. 对于我们的诗歌下载客户端而言就是一条TCP连接。
2. twisted也支持unix中管道
3. UDP等。

Protocols:
twisted的protocol抽象由interfaces模块中的[IProtocol](https://github.com/twisted/twisted/blob/trunk/src/twisted/internet/interfaces.py)定义。
也许你已经想到，Protocol对象实现协议内容。
因此我们的程序每建立一条连接（对于服务方就是每接受一条连接）。都需要一个协议实例。
**Protocol实例是存储协议状态与间断性（由于我们是通过异步IO方式以任意大小来
接收数据的）接收并累积数据的地方**

Protocol实例如何得知它为哪条连接服务呢？[IProtocol](https://github.com/twisted/twisted/blob/trunk/src/twisted/internet/interfaces.py)->makeConnection(Transport)回调。


[内置的简单的通用协议](https://github.com/twisted/twisted/blob/trunk/src/twisted/protocols/basic.py)：
NetstringReceiver：A protocol that sends and receives netstrings.
LineOnlyReceiver: A protocol that receives only lines
LineReceiver: A protocol that receives lines and/or raw data, depending on mode
当你需要写新Protocol时，最好看看twisted是否已经有现成的实现。

Protocol类实例都为一个具体的链接提供协议解析。
一个具体的twisted的Protocol的实现应该对应一个具体的网络协议的实现: FTP，IMAP，或其他自定义的协议->我们的诗歌下载协议

ProtocolFactory:
[接口定义](https://github.com/twisted/twisted/blob/trunk/src/twisted/internet/interfaces.py)
每个连接需要一个自己Protocol。
我们会将创建Protocol连接的工作交给twisted来完成。
twisted使用ProtocolFactory来制定协议。

我们在子类中调用基类中的实现。基类怎么会知道我们创建什么样的Protocol呢？
protocol = PoetryProtocol # tell base class what proto to build
基类Factory的实现buildProtocol过程是：
1. 安装设置在PoetryClientFacotry.protocol的Protocol类
2. 并在上述实例的self.factory属性上设置一个产生它的Factory引用。
正如我们提到的那样，位于Protocol实例的factory属性字段允许在都由同一个factory
产生的Protocol之间共享数据。
由于factory都是由用户代码来创建的（在用户控制中）因此这个属性也可以
Protocol对象将数据传递回一开始初始化请求的代码中。
工厂里有要生产的协议：PoetryProtocol（Class Type）
PoetryProtocl实例有工厂类的实例。
各个连接可以通过**factory共享数据**

Protocol创立后的第二步：通过makeConnection与Transport联系起来。
我们无需自己来实现这个函数，而是使用twisted的默认实现。
默认情况是：makeConnection将Transport的一个引用赋给(Protocol的）protocol.self.transport属性。
同时置protocol.self.connected=True

一旦初始化到这一步后，Protocol开始其真正的工作：将底层的数据流翻译成高层的协议规定格式的消息
处理接收到的数据的主要方法是dataReceived(self, data)

每次dataReveived被调用就意味着我们得到一个新字符串。由于与异步IO交互，我们不知道能接收
到多少数据，因此**将接收到的数据缓存下来直到完成一个完整的协议规定的格式**。

我们使用了Transport的getHost(peer)方法获取数据来自的服务器信息。我们这样做只是与
前面的客户端保持一致。相反我们的代码没有必要这样做。因为我们没有向服务器发送任何消息。
也没有必要知道服务器的任何信息了。

[make protoco](http://s8.sinaimg.cn/middle/704b6af749e993c8ccba7&690)

[make transport](http://s4.sinaimg.cn/middle/704b6af749e993f5e6453&690)

err log:
File: .../twisted/internet/tcp.py line 463, in doRead # Note the doRead callback return self.protocol.dataReceived(data)
有我们在1.0版本客户端的doRead回调函数
我们前面也提到过，Twisted在建立新抽象层进会使用已有的实现而不是另起炉灶
因此必然会有一个IReadDescriptor的实例在辛苦的工作，它是由Twisted代码而非我们自己的代码来实现 
如果你表示怀疑，那么就看看twisted.internet.tcp中的实现吧。如果你浏览代码会发现，由同一个类实现了IWriteDescriptor与ITransport。
因此 IreadDescriptor实际上就是变相的Transport类

版本2的客户端使用的抽象对于那些Twisted高手应该非常熟悉。如果仅仅是为在命令行上打印出下载的诗歌这个功能，那么我们已经完成了。但如果想使我们的代码能够复用，能够被内嵌在一些包含诗歌下载功能并可以做其它事情的大软件中，我们还有许多工作要做
