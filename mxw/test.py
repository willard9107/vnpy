import sys


class Template:
    vars = []

    def __init__(self):
        self.vars = []
        self.vars.insert(0, "0")

    @classmethod
    def class_method_demo(cls):
        print(cls)

    def print_vars(self):
        print(self.vars)


class Strategy(Template):
    def __init__(self):
        super().__init__()
        print('strategy init')


def spamrun(fn):
    def sayspam(*args):
        print("spam,spam,spam")
        fn(*args)

    return sayspam


def spamrun1(fn):
    def sayspam1(*args):
        print("spam1,spam1,spam1")
        fn(*args)

    return sayspam1


@spamrun
@spamrun1
def useful(a, b):
    print(a * b)


def attrs(**kwds):
    def decorate(f):
        for k in kwds:
            setattr(f, k, kwds[k])
        print('***************')
        print(f)
        return f

    print(kwds)
    return decorate


# @attrs(versionadded="2.2",
#        author="Guido van Rossum")
# def mymethod(f):
#     print(getattr(mymethod, 'versionadded', 0))
#     print(getattr(mymethod, 'author', 0))
#     print(f)

# print('------0-------')
# print(mymethod)
# print('-------1------')
#
# if __name__ == "__main__":
#     mymethod(2)


# ttt = Template()
# ttt1 = Template()
# ttt2 = Template()
# print(Template.vars)
# ttt1.print_vars()
# ttt2.print_vars()

#
# class Sample:
#
#     def __init__(self):
#         print('__init__')
#
#     def __enter__(self):
#         print("in __enter__")
#         return "Foo"
#
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         print("in __exit__")
#
#
# def get_sample():
#     return Sample()
#
#
# with get_sample() as sample:
#     print("Sample: ", sample)

# # 传递外部类的实例
# class OuterClassA(object):
#
#     def __init__(self):
#         print('outter  init ....')
#         self.a = 0
#
#     def outer_func_1(self, text):
#         print(text)
#
#     class InnerClass(object):
#
#         def __init__(self):
#             print('inner  init ....')
#             self.out = OuterClassA()
#
#         def inner_func_1(self):
#             self.out.outer_func_1('balabala')
#             # pass

#
# outer = OuterClassA()
# outer.outer_func_1('abcdefg')
# print('1')
# inn = outer.InnerClass()
# print('2')
# inn.inner_func_1()
#
#
#
# print('3')
# inn1 = outer.InnerClass()
# print('4')
# inn1.inner_func_1()


if __name__ == '__main__':
    print(sys.argv)
