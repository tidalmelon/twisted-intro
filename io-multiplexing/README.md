## linux 下IO多路复用形象化理解

### 空管

假设你是一个空管，你需要管理到你机场的所有的航线：进港，出港，停机坪等待，登机口接客。

简单方法：  

招一批空管员，然后没人顶一架飞机（多进程）: 从进港，接客，排位，出港，航线监控，直接交给下一个空港，全程监控。

问题：

进程太多，新空管员进不来。
进程之间如何协调。几十号人，成菜市场了。
进程之间的资源竞争。公用的东西，比如起飞显示屏，下一个小时的出港排期。最后时间都花在抢资源上来。


![make transport](https://github.com/tidalmelon/twisted-intro/blob/master/twisted-client-2/transport.png)

这个东西叫 flight process strip。 每一个块代表一个航班，不同的槽代表不同的状态，然后一个空管员可以管理一组这样的块（一组航班）

而他的工作就是“航班信息有更新的“时候，把对应的块放到不同的槽位上。


## io多路复用

如果你把每个航线当成一个sock（IO流），空管当成你的服务端sock管理代码。

第一种方法就是最传统的多进程并非模型。（每来一个新的IO流，会分配一个新的进程管理）

第二种方法就是IO多路复用。（单个线程通过跟踪记录每一个io流的状态，来同时管理多个IO流）

一根网线多个sock复用？ 其实不管你是多进程，还是io多路复用。都是一根网线。多个sock复用一根网线是内核+驱动层实现。


IO multiplexing : 单个线程通过跟踪记录每一个IO流的状态(空管塔里的Fight progress strip 槽)来同时管理多个IO流。


![make transport](https://github.com/tidalmelon/twisted-intro/blob/master/twisted-client-2/transport.png)

谁有数据就拔向谁


## 多路复用的实现历史

1983年  
select 被实现以后，很快暴露出很多问题。  
1， select 会修改传入的参数数组，这个对一个需要调用多次的函数，非常不友好。  
2， select 如果任何一个io出现了数据，select仅仅会返回，但不会告诉你哪个sock上有数据。只能自己去找。。。。。  
3, select只能监听1024个链接。参见linux FD_SETSIZE  
4, select 不是线程安全的，如果一个sock放入了select，另外一个线程收回。对不起select不支持。如果你丧心病狂的关掉这个sock，select的标准行为是....不可预测的  



1997年：
poll 去掉了1024链接的限制，于是要多少链接呢？ 主人你开心就好。  
poll 从设计上，不再修改传入数组，不过这个看你的平台了。所以行走江湖，小心为妙。  

但是poll依然不是线程安全的，这意味着不管服务器多强悍，你也只能一个线程里处理一组IO流，你当然可以拿多进程来配合。但多进程的各种问题又浮现。 

2002年。  

1, epoll是线程安全的
2, epoll现在不仅告诉你sock组里面有数据， 还会告诉你具体哪个sock有数据， 你不用自己去找了。  




![make transport](https://github.com/tidalmelon/twisted-intro/blob/master/twisted-client-2/transport.png)


横轴就是链接数的意思， 纵轴是每秒处理的请求， 可以发现epoll每秒处理请求的数量不会因为链接多而下降的。 poll /dev/poll 就很惨了。   

可是epoll有个致命缺点， 只支持linux， 比如bsd上面对应的是kqueue




## NGINX 异步，非堵塞， IO多路复用。  

每进来一个request，会有一个worker进程去处理。但不是全程的处理，处理到什么程度呢？  处理到可能发生阻塞的地方，比如向上游（后端）服务器转发request，并等待请求返回。   
那么，这个处理的worker不会这么傻等着，他会在发送完请求后，注册一个事件：“如果upstream返回了，告诉我一声，我再接着干”。于是他就休息去了。这就是异步。此时，如果再有request 进来，他就可以很快再按这种方式处理。这就是非阻塞和IO多路复用。而一旦上游服务器返回了，就会触发这个事件，worker才会来接手，这个request才会接着往下走。这就是异步回调。
