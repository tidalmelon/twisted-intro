1, reactor并不会因为回调函数中出现失败（虽然它会报告异常）而停止运行。
2, reactor循环并不会消耗任何CPU的资源。

# linux
# select: 有fd上限
# poll:  本质上与select无区别， 无fd上限
# epoll：1, 事件注册，性能最高
#        2, 有连接上限，但很大，1G内存可以打开10万fd。2G=20万fd
#        3, 支持水平触发，边缘触发（它只告诉进程哪些fd处于需态, 类似于事件?）
#twisted.internet.pollreactor
#twisted.internet.epollreactor
