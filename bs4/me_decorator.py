import time
import functools
def log(argu):
    def decorator(func):
        @functools.wraps(func) #改变decorator装饰之后的__name__  没用__name__=wrapper 引用后__name__ = now
        def wrapper(*args,**kwargs):
            print(kwargs)
            print('%s %s():' % (argu, func.__name__))
            return func(*args,**kwargs)
        return wrapper
    return decorator

@log('test_decorator')
def now(sss):

    return (time.time())
#now = log('test_decorator')(now)
#1.log('test_decorator') => return decorator
#2.decorator(now) => return wrapper

if __name__ == "__main__":
    nowTime = now('sd')
    print (now.__name__)
    print (nowTime)
