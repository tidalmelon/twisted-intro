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
