import marshal
import dis

with open("output.pyc", "rb") as f:
    code = f.read()[16:]

    code = marshal.loads(code)
    dis.dis(code)
