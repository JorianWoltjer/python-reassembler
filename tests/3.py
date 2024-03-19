# Check correct keyword arguments and re-using variable names
def func(a, b, k1=1, k2=2):
    a += b
    t2 = k1 + k2
    return a + t2


print(func(3, 4))
