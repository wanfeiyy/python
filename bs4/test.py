def a(*args,**kw):
    print (kw.get('a',None))
    tr = kw.get('c',None) or 'dddddd'
    print (tr)
    return kw.items()
for k,v in a(a='cc',b='dd'):
    print (k,v)