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
