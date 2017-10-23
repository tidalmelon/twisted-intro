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
