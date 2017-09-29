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
5. doRead ---> IreadDescriptor

这里没有使用继承，而是直接给出了方法实现---duck typing
接口类永远不会被实例化或作为基类来继承实现(这是真的么？)

removeReader和getReaders
还有与我们客户端使用的Readers的APIs类同的Writers的APIs
读和写有各自的APIs是因为select函数需要分开这两种事件（读或写可以进行的文件描述符）
可以等待即能读也能写的文件描述符 (类似grpc基于http协议既然也实现了读写流-？？？不解)

