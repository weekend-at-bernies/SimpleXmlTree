PYTHON GOTCHAS

class Foo(object):
    def __init__(self, attr1, attr2):
        self.attr1 = attr1
        self.attr2 = attr2



foo = Foo(1, 2)
# Think you can do this? WRONG!
foo.attr3 = 3
# Can't even do this (prolly the same thing): 
setattr(foo, attr3, 3)


foo1 = Foo(1, 2)
foo2 = Foo(1, 2)

foo1 == foo2   ??
foo1 is foo2   ??


over-riding __eq__:


def __eq__(self, obj):
    return isinstance(obj, Foo) and <self and obj equivalency test>

Which does this alter:
foo1 == foo2 ?
foo1 is foo2 ?

