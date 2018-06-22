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
