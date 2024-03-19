# Check nested functions, lambda and list comprehension sections
# fmt: off

def f2():
    def inner_func(x, y=1):
        x2 = x + y
        return x2

    lamb = lambda x: x + 2
    print(inner_func(3))
    print(lamb(4))
    return [i for i in range(10)]
