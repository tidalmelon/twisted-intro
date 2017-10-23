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
