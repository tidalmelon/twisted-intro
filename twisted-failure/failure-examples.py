# This code illustrates a few aspects of Failures.
# Generally, Twisted makes Failures for us.

from twisted.python.failure import Failure

class RhymeSchemeViolation(Exception): pass


print 'Just making an exception:'
print

e = RhymeSchemeViolation()

failure = Failure(e)

# Note this failure doesn't include any traceback info
print failure

print
print

print 'Catching an exception:'
print

def analyze_poem(poem):
    raise RhymeSchemeViolation()

try:
    analyze_poem("""\
Roses are red.
Violets are violet.
That's why they're called Violets.
Duh.
""")
except:
    failure = Failure()


# This failure saved both the exception and the traceback
print failure

# 第一个仅有异常，无堆栈信息
# 第二个有异常，和跟踪栈信息。

#Just making an exception:
#
#[Failure instance: Traceback (failure with no frames): <class '__main__.RhymeSchemeViolation'>: 
#]
#
#
#Catching an exception:
#
#[Failure instance: Traceback: <class '__main__.RhymeSchemeViolation'>: 
#--- <exception caught here> ---
#failure-examples.py:34:<module>
#failure-examples.py:26:analyze_poem
#]
