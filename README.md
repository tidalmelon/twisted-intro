# twisted 入门教程

1. [英文原文](http://krondo.com/?page_id=1327)
2. [中文翻译 part-1](http://blog.sina.com.cn/s/blog_704b6af70100py9n.html)
3. [中文翻译 part-2](https://github.com/luocheng/twisted-intro-cn)

---

# [第二部分：异步编程初探与reactor模式](https://github.com/tidalmelon/twisted-intro/tree/master/async-client)

## 异步模式与同步模式的对比
1. 异步模式客户端一次性与全部服务器完成链接，而不像同步模式那样一次只链接一个
2. 用来通信的socket方法是非阻塞模式的，这个是通过setblocking(0)来实现的。
3. select模块中的select方法是用来识别其监视的socket是否有完成数据接收的，如果没有它就处于阻塞模式
4. 当从服务器中读取数据时，会尽量多的从socket读取数据，直到它阻塞为止，然后读下一个socket接收数据（如果有数据接收的话）
   这意味着我们需要跟踪记录从不同服务器传送过来诗歌的接收情况（因为，一首诗的接收并不是连续完成的，所以需要保证每个任务的可连续性，就得有冗余的信息来完成这一工作。

## 核心内容：
1. 适用select函数等待所有socket，直到至少一个socket有数据到来
2. 对每个有数据需要读取的socket，从中读取数据。但仅仅是读取有效数据，不能为了等待还没有来到的数据而发生阻塞。
3. 重复前两步，直到所有的socket被关闭

如果在服务器端口固定的条件下，同步模式的客户端并不需要循环体，只需要顺序罗列三个get_poetry就可以了。但是我们的异步模式客户端需要一个循环体
 来保证我们能够同时监视所有的socket端，这样我们就能在一次循环体中处理尽可能多的数据。
 这个利用循环体来等待事件发生，然后处理发生的事件的模型非常常见，而被设计成为一个模式。
 reactor模式(反应堆） 也称为事件循环。
 因为交互式系统都需要进行I/O操作，因此这种循环也有时被称作select loop，这是由于select调用被用来等待io操作。
 select 并不是唯一的等待io操作的函数，它仅仅是一个比较古老的函数而已。现在有一些新的API可以完成select的工作而且新能更优。不考虑性能因素，他们完成的工作一样。
 监视一系列sockets fd 并阻塞程序，直到至少有一个准备好时进行IO操作。

 严格意义上来说，我们的异步模式客户端中的循环体并不是reactor模式，因为这个循环体并没有独立于业务处理（接收诗歌）之外。他们被混合在一起。
 一个真正reactor模式的实现是需要实现循环独立抽象出来并具有如下功能：
1. 监视一系列与你io操作相关的fd
2. 不停的向你汇报那些准备好io操作的fd

 一个优秀的的rector模式实现需要做到：
1. 处理所有不同系统会出现的IO事件
2. 提供优雅的抽象来帮助你在使用reactor时少花些心思去考虑它的存在。
3. 提供你可以在抽象层外（reactor实现）使用的公共协议实现。

好了， 我们上面所说的其实就是twisted：健壮，跨平台实现了reactor模式，并包含很多附加功能。

# [第三部分：初次认识Twisted](https://github.com/tidalmelon/twisted-intro/tree/master/basic-twisted)

1. reactor并不会因为回调函数中出现失败（虽然它会报告异常）而停止运行。
2. reactor循环并不会消耗任何CPU的资源。

### linux 几种IO多路复用简略
1. select: 有fd上限
2.  poll:  本质上与select无区别， 无fd上限
3.  epoll：
>> 1, 事件注册，性能最高
>> 2, 有连接上限，但很大，1G内存可以打开10万fd。2G=20万fd
>> 3, 支持水平触发，边缘触发（它只告诉进程哪些fd处于需态, 类似于事件?）

reactor是单例模式的，即在一个程序中只有一个reactor。

>twisted.internet.pollreactor
>twisted.internet.epollreactor

0. reactor 异常处理的有点 python basic-twisted/exception.py
1. 任何一个回调函数异常，不会被带到reactor循环中

# [第四部分：由twisted支持的诗歌客户端](https://github.com/tidalmelon/twisted-intro/blob/master/twisted-client-1/get-poetry.py)

传递一个实现接口的对象，这样我们就可以通过一个对象传递一组相关的回调函数
回调函数之间还可以通过对象共享数据
1. fileno() connectionLost() ---> IFileDescriptor
2. logPrefix()----> ILooggingContext
3. addReader() -----> IReactorFDSet
4. addReader(reader) ----> IreadDescriptor(IFileDescriptor(ILooggingContext))
   IreadDescriptor:**一个可以读取字节的文件描述符**
5. doRead ---> IreadDescriptor

这里没有使用继承，而是直接给出了方法实现---duck typing
接口类永远不会被实例化或作为基类来继承实现(这是真的么？)

removeReader和getReaders
还有与我们客户端使用的Readers的APIs类同的Writers的APIs
读和写有各自的APIs是因为select函数需要分开这两种事件（读或写可以进行的文件描述符）
可以等待即能读也能写的文件描述符 (类似grpc基于http协议既然也实现了读写流-？？？不解)

# 第五部分： 由twisted支持的诗歌客户端

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

# to do: http://blog.sina.com.cn/s/blog_704b6af70100q2ac.html

