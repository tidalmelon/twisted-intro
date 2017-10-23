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
