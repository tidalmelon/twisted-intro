from twisted.internet.defer import Deferred

def callback(res):
    raise Exception('oops')

d = Deferred()

d.addCallback(callback)

d.callback('Here is your result.')

print "Finished"


import time

time.sleep(10)
print 'sleep 10s'

#[root]# python defer-unhandled.py 
#Finished
#sleep 10s
#Unhandled error in Deferred:


