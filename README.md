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

# [第五部分： 由twisted扶持的诗歌客户端](https://github.com/tidalmelon/twisted-intro/blob/master/twisted-client-2/get-poetry.py)

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

![make protoco](https://github.com/tidalmelon/twisted-intro/blob/master/twisted-client-2/makeproto.png)

![make transport](https://github.com/tidalmelon/twisted-intro/blob/master/twisted-client-2/transport.png)


err log:
File: .../twisted/internet/tcp.py line 463, in doRead # Note the doRead callback return self.protocol.dataReceived(data)
有我们在1.0版本客户端的doRead回调函数
我们前面也提到过，Twisted在建立新抽象层进会使用已有的实现而不是另起炉灶
因此必然会有一个IReadDescriptor的实例在辛苦的工作，它是由Twisted代码而非我们自己的代码来实现 
如果你表示怀疑，那么就看看twisted.internet.tcp中的实现吧。如果你浏览代码会发现，由同一个类实现了IWriteDescriptor与ITransport。
因此 IreadDescriptor实际上就是变相的Transport类

版本2的客户端使用的抽象对于那些Twisted高手应该非常熟悉。如果仅仅是为在命令行上打印出下载的诗歌这个功能，那么我们已经完成了。但如果想使我们的代码能够复用，能够被内嵌在一些包含诗歌下载功能并可以做其它事情的大软件中，我们还有许多工作要做

# [第六部分： 更加抽象的利用twisted](https://github.com/tidalmelon/twisted-intro/blob/master/twisted-client-3/get-poetry.py)
打造可以复用的诗歌下载客户端
最新版本（2.0）客户端使用了Transports, Protocols, ProtocolFactory, 即整个twisted的网络框架。
2.0版本的只能在命令行里下载诗歌：
    1.PoetryClientFactory不仅要下载诗歌。
    2.还要在诗歌下载完后，关闭程序,但这是份外工作，
期望PoetryClientFactory的功能应该是：
    1. 生成PoetryProtocol的实例 
    2. 收集下载完毕的诗歌
同步API：
def get_poetry(host, port):
    return poem from host:port
使用回调解决问题。
异步API：
def get_poetry(host, port, callback):
       """
       download poem from host:port and invoke callback(poem) when the poem is complete
       """


![alt text](https://github.com/tidalmelon/twisted-intro/blob/master/twisted-client-3/reactor-poem-callback.png)

回调**链**, 
即交互式的编程方式不会在我们的代码处止步，我们的回调函数可能还会回调其他人实现的代码，即交互式不会止于我们的代码。
当你选择twisted实现你的工厂时，务必记住：
i am going to use twisted
**i am going to structure my program as a series of asynchronous callback chain invocations powered by a reactor loop!**
**我将要构造我的程序 <- 由一系列的异步回调链 <- 被reactor调用**

如果你的程序原来就是异步方式，那么使用twisted再好不过。
如果不是异步的，那么我们需要对原有代码做大的改写。

简单的将同步与异步程序混合在一起是不行的。

twisted 与 pyGTK pyQT这两个基于reactor的GUI实现了很好的交互性。


异常处理的问题：
如果我们让3.0到一个不存在的服务器上下载诗歌，那么不是像1.0版本那样立刻程序崩溃掉而是永远处于等待中。
clientConnectionFailed回调仍然会被调用，但其在ClientFactory基类中也没什么实现[这个函数是空的]（若子类没有重写基类，则使用基类）
get_poem回调永远不会激活，这样reactor也不会停止。

“”“
丫丫的：终于理解为啥叫twisted（扭曲的）
“”“

**问题的提出**
链接失败的信息会通过clientConnectionFailed函数传递给工厂。
1， 工厂需要设计成可复用的，因此如何处理这个错误是依赖于工厂所使用的场景的。【在一些应用中，丢失诗歌时糟糕的，但在另外一些场景，我们只是尽量，不行就从其他地方下载】
    换句话说：使用get_poetry的人需要知道何时会出现这些问题。而不仅仅是什么情况下会正常运行。
2， 在一个同步程序中，get_poetry可能会抛出一个异常并调用try/except来处理异常。
    但在异步程交互中，错误信息也必须异步的传递出去。
    **总之再取得get_poetry之前，我们是不会发现链接失败这种错误的**

实现1：
def get_poetry(host, port, callback):
    if poem:
        callback(poem)
    elif None:
        callback(None)
通过检查回调函数的参数来判断我们是否已经完成下载。
存在问题：
    1， None表示失败有些牵强
    2， None可能会是返回值，而不是错误状态
    3,  None携带的信息太少，不能告诉我们出了什么错误，堆栈信息
def get_poetry(host, port, callback):
    if poem:
        callback(poem)
    elif exception:
        callback(err)
使用exception已经很接近我们的异步程序了。

twisted含有一个抽象类，称作Failure。如果有异常的话，能捕获**Exception**和**跟踪栈**。
转：[twisted-failure/failure-examples.py](https://github.com/tidalmelon/twisted-intro/blob/master/twisted-failure/failure-examples.py)

def get_poetry(host, port, callback):
    if poem:
        callback(poem)
    elif Failure:
        callback(err)

又存在的问题：
**使用相同的回调函数处理正常的与不正常的结果是一件莫名其妙的事情。** 通常情况下我们处理失败信息，与处理成功信息要进行不同的操作。
同步编程中，我们经常使用try/except对失败与成功采用不同的路径。

因此：
def get_poetry(host, port, callback, errback):
    if poem:
        callback(poem)
    elif Failure:
        errback(err)


转-> [twisted-client-3/get-poetry-1.py](https://github.com/tidalmelon/twisted-intro/blob/master/twisted-client-3/get-poetry-1.py)


第六部分我们学到：
2， 我们为twisted程序写的API必须是异步的
3， 不能讲同步代码与异步代码混合起来使用
4， 我们可以在自己的代码中写异步函数，正如twisted所做的那样
5， 并且我们需要些**处理错误信息的回调函数**


使用twisted时，难道都需要加上两个额外的参数：callback，errcallback？ twisted引进了defferred。



# 第七部分： 小插曲,Deferred



```
同步模式：
try:
    poem = get_poetry(host, port)
except Exception, err:
    print sys.stderr, 'poem downlaod failed'
    print sys.stderr, 'i am terribly sorry'
    print sys.stderr, 'try again later?'
    sys.exit()
else:
    print poem
    sys.exit()

```
```
异步模式：
def got_poem(poem):
    print poem
    reactor.stop()

def poem_failed(err):
    print sys.stderr, 'poem downlaod failed'
    print sys.stderr, 'i am terribly sorry'
    print sys.stderr, 'try again later?'
    reactor.stop()

get_poetry(host, port, got_poem, poem_failed)
reactor.run()
    
```
区别：
1, 异常控制：同步 异常由python解释器控制。异步 异常我们自己控制：即PeotryClientFactory的clientConnectFailed函数
2, 关闭：python解释器自己关闭，而异步程序会一直运行下去
3, 在异步程序中处理错误是相当重要的，甚至有些严峻。
   在异步程序中处理错误信息比处理正常的信息重要的多。原因：错误会以多种方式出现，而正确的结果只有一种。

存在问题：
1， 同时调用了callback，errback , 或者激活callback27次。
2， 同步异步都有重复代码。 sys.exit() reactor.stop()

**重构同步代码**

```
同步模式：
try:
    poem = get_poetry(host, port)
except Exception, err:
    print sys.stderr, 'poem downlaod failed'
    print sys.stderr, 'i am terribly sorry'
    print sys.stderr, 'try again later?'
else:
    print poem

sys.exit()
```
我们能这样重构异步代码么？

异步编程的一些观点：
1， 激活errback是非常重要的。由于errback的功能与except块相同，因此用户需要确认他们存在。他们不是可选项，而是必选项。
2， 不在错误的时间点激活回调与在正确的时间点激活回调同等重要。典型的用法是：callback与errback是互斥的即只能运行其中一个。
3， 使用回调函数的代码重构起来困难些。

**为什么使用deferred抽象机制来管理回调**
![deferred](https://github.com/tidalmelon/twisted-intro/blob/master/twisted-deferred/callbackchains.png)

```
1, 
from twisted.internet.defer import Deferred

def got_poem(res):
    print 'Your poem is served:'
    print res

def poem_failed(err):
    print 'No poetry for you.'

d = Deferred()

# add a callback/errback pair to the chain
d.addCallbacks(got_poem, poem_failed)

# fire the chain with a normal result
d.callback('This poem is short.')

print "Finished"

#Your poem is served:
#This poem is short.
#Finished

```
需要注意几个问题：
1， 添加的是callback/errback对。
2,  添加到deferred的回调函数允许多个参数，但第一个只能是正确的结果或错误信息

```
2
from twisted.internet.defer import Deferred
from twisted.python.failure import Failure

def got_poem(res):
    print 'Your poem is served:'
    print res

def poem_failed(err):
    print 'No poetry for you.'

d = Deferred()

# add a callback/errback pair to the chain
d.addCallbacks(got_poem, poem_failed)

# fire the chain with an error result
d.errback(Failure(Exception('I have failed.')))

print "Finished"


#No poetry for you.
#Finished

```

**deferred 会将Exceptin转化为Failure**
**因此使用deferred时，我们可以正常的使用Exception**
```
3
from twisted.internet.defer import Deferred

def got_poem(res):
    print 'Your poem is served:'
    print res

def poem_failed(err):
    print err.__class__
    print err
    print 'No poetry for you.'

d = Deferred()

# add a callback/errback pair to the chain
d.addCallbacks(got_poem, poem_failed)

# fire the chain with an error result
d.errback(Exception('I have failed.'))

#<class 'twisted.python.failure.Failure'>
#[Failure instance: Traceback (failure with no frames): <type 'exceptions.Exception'>: I have failed.
#]
#No poetry for you.
```

**deferred不允许别人激活他两次：解决了一个回调会被激活多次，如果非要调用多次，将会异常报错**

```
4
from twisted.internet.defer import Deferred
def out(s): print s
d = Deferred()
d.addCallbacks(out, out)
d.callback('First result')
d.callback('Second result')
print 'Finished'


#First result
#Traceback (most recent call last):
#  File "defer-4.py", line 6, in <module>
#    d.callback('Second result')
#  File "/usr/local/lib/python2.7/site-packages/twisted/internet/defer.py", line 459, in callback
#    self._startRunCallbacks(result)
#  File "/usr/local/lib/python2.7/site-packages/twisted/internet/defer.py", line 560, in _startRunCallbacks
#    raise AlreadyCalledError
#twisted.internet.defer.AlreadyCalledError

```

```
5
from twisted.internet.defer import Deferred
def out(s): print s
d = Deferred()
d.addCallbacks(out, out)
d.callback('First result')
d.errback(Exception('First error'))
print 'Finished'


#First result
#Traceback (most recent call last):
#  File "defer-5.py", line 6, in <module>
#    d.errback(Exception('First error'))
#  File "/usr/local/lib/python2.7/site-packages/twisted/internet/defer.py", line 500, in errback
#    self._startRunCallbacks(fail)
#  File "/usr/local/lib/python2.7/site-packages/twisted/internet/defer.py", line 560, in _startRunCallbacks
#    raise AlreadyCalledError
#twisted.internet.defer.AlreadyCalledError

```


```
6
from twisted.internet.defer import Deferred
def out(s): print s
d = Deferred()
d.addCallbacks(out, out)
d.errback(Exception('First error'))
d.errback(Exception('Second error'))
print 'Finished'

#[Failure instance: Traceback (failure with no frames): <type 'exceptions.Exception'>: First error
#]
#Traceback (most recent call last):
#  File "defer-6.py", line 6, in <module>
#    d.errback(Exception('Second error'))
#  File "/usr/local/lib/python2.7/site-packages/twisted/internet/defer.py", line 500, in errback
#    self._startRunCallbacks(fail)
#  File "/usr/local/lib/python2.7/site-packages/twisted/internet/defer.py", line 560, in _startRunCallbacks
#    raise AlreadyCalledError
#twisted.internet.defer.AlreadyCalledError

```



```
7
from twisted.internet.defer import Deferred
def out(s): print s
d = Deferred()
d.addCallbacks(out, out)
d.errback(Exception('First error'))
d.callback('First result')
print 'Finished'


#[Failure instance: Traceback (failure with no frames): <type 'exceptions.Exception'>: First error
#]
#Traceback (most recent call last):
#  File "defer-7.py", line 6, in <module>
#    d.callback('First result')
#  File "/usr/local/lib/python2.7/site-packages/twisted/internet/defer.py", line 459, in callback
#    self._startRunCallbacks(result)
#  File "/usr/local/lib/python2.7/site-packages/twisted/internet/defer.py", line 560, in _startRunCallbacks
#    raise AlreadyCalledError
#twisted.internet.defer.AlreadyCalledError
```

**callwhenrunning函数可以接受一个额外的参数给回调函数**
**多数的twisted的API都以这样的方式注册回调函数**

```
8
import sys

from twisted.internet.defer import Deferred

def got_poem(poem):
    print poem
    from twisted.internet import reactor
    reactor.stop()

def poem_failed(err):
    print >>sys.stderr, 'poem download failed'
    print >>sys.stderr, 'I am terribly sorry'
    print >>sys.stderr, 'try again later?'
    from twisted.internet import reactor
    reactor.stop()

d = Deferred()

d.addCallbacks(got_poem, poem_failed)

from twisted.internet import reactor

reactor.callWhenRunning(d.callback, 'Another short poem.')

reactor.run()


#Another short poem.
```

**回调链的第二个回调**

```
9
import sys

from twisted.internet.defer import Deferred

def got_poem(poem):
    print poem

def poem_failed(err):
    print >>sys.stderr, 'poem download failed'
    print >>sys.stderr, 'I am terribly sorry'
    print >>sys.stderr, 'try again later?'

def poem_done(_):
    from twisted.internet import reactor
    reactor.stop()

d = Deferred()

d.addCallbacks(got_poem, poem_failed)
d.addBoth(poem_done)

from twisted.internet import reactor

reactor.callWhenRunning(d.callback, 'Another short poem.')

reactor.run()


#Another short poem.
```

总结 ：
回调编程隐藏的问题，以及deferred如何帮我们解决。
1， errback不能被忽略。 Deferred支持errback
2， 激活多次可能会导致很严重的问题。deferred只能被激活一次，类似于try/except
3,  含有回调的程序重构时相当困难。有了deferred，我们就**通过修改回调链**来重构程序

Deferred还有很多细节，但对于使用它来重构我们的客户端已经足够了。





![reactor-deferred-callback](https://github.com/tidalmelon/twisted-intro/blob/master/twisted-client-4/reactor-deferred-callback.png)  

callback链直到第二个回调poem_done激活前才将控制权还给reactor  

![3-4duibi](https://github.com/tidalmelon/twisted-intro/blob/master/twisted-client-4/3-4duibi.png)

Deferred被激活后是如何销毁其引用的：  
1, 这样做可以保证我们不激活一个deferred两次  
2， python的垃圾回收带来方便
```
if self.deferred is not None:
    d, self.deferred = self.deferred, None
    d.callback(poem)

```

**讨论**  
同步版本返回诗歌内容
异步版本返回deferred：**一个Deferred代表了一个“异步的结果” or “结果还没有返回”**  
异步函数返回一个deferred：
我是一个异步函数，不管你想要什么，可能现在马上都得不到。  
但当结果来到时，我会激活这个deferred的callback链并返回结果，  
或者当出错时，相应的激活errback链，并返回出错信息。  
**deferred是为适应异步模式的一中延迟函数返回的方式: 函数返回一个deferred意味着其是异步的，代表着将来的结果，也是对将来能返回结果的一种承诺**  
**同步函数也能返回deferred， 因此返回deferred只能说可能是异步的**

![aysn-asyn](https://github.com/tidalmelon/twisted-intro/blob/master/twisted-client-4/sync-async.png)

Deferred的好处：deferred的行为已经很好的定义与理解，因此实现自己的api时返回一个deferred更容易让其它的twisted程序员理解你的代码  
                如果没有deferred，可能每个人写的模块都使用不同的方式来处理回调->这增加了**相互理解**的工作量。

经常犯的一个错误：  
会给deferred增加一些它本身不能实现的功能。  
1， 在defferred上添加一个函数就会使其变成异步函数。--> 在twisted中回调函数中可以使用os.system  

**异步是由reactor完成的，deferred是一个很好的抽象概念, 但大部分工作是reactor做的**



通过使用deferred，我们在twisted中的reactor 启动过程中加入了一些自己的东西。但我们并没有改变异步编程 基础架构。回忆下回调编程的特点： 
1， 在一个时刻，只会有一个回调在运行。  
2， 当reactor代码运行时，那我们的代码则得不到运行。  
3,  反之亦然  
4， 如果我们的回调发生**阻塞**，那么整个程序就跟着阻塞了。  **在deferred上激活阻塞，那么整个程序亦然阻塞，deferred改变不了阻塞** [example](https://github.com/tidalmelon/twisted-intro/blob/master/twisted-deferred/defer-block.py)

总结： 
1， 函数通过返回一个Deferred，向使用者暗示“我是采用异步方式的”并且当结果到来时会使用一种特殊的机制（在此处添加你的callback与errback）来获得返回结果。  
2, 4.0版本客户端是第一个使用Deferred的Twisted版的客户端，其使用方法为在其异步函数中返回一个deferred来。可以使用一些Twisted的APIs来使客户端的实现更加清晰些，但我觉得它能够很好地体现出一个简单的Twisted程序是怎么写的了，至少对于客户端可以如此肯定


