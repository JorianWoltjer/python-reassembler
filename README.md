Python re-assembler
============================

###### Re-assemble Python disassembly text to bytecode

 ---

This project serves a pretty unique use case, where you **have** output of the [`dis.dis()`](https://docs.python.org/3/library/dis.html#dis.dis) module in the form of disassembled bytecode:

```
  0 LOAD_GLOBAL              0 (print)
  2 LOAD_CONST               1 ('Hello,')
  4 LOAD_CONST               2 ('world!')
  6 CALL_FUNCTION            2
  8 POP_TOP
 10 LOAD_CONST               0 (None)
 12 RETURN_VALUE
```

Using this tool, the above can be parsed and turned back into raw bytecode. This allows decompilers like [`uncompyle6`](https://github.com/rocky/python-uncompyle6/releases), [`decompyle3`](https://github.com/rocky/python-decompile3/blob/master/decompyle3/main.py) and [`pycdc`](https://github.com/zrax/pycdc) to work with the bytes. 

```Shell
$ python-reassembler debug/example.txt -q
Opening 'example.txt' and reassembling the code object...
[SUCCESS] Code object written to 'output.pyc'
Now use a decompiler like `uncompyle6`, `decompyle3`, or `pycdc` on the output to decompile it

$ decompyle3 output.pyc
# decompyle3 version 3.9.1
print("Hello,", "world!")
# okay decompiling output.pyc
```

The inspiration for this tool came from a [PicoCTF 2024](https://picoctf.org/competitions/2024-spring.html) challenge named 'weirdSnake', where players received a text file containing disassembled Python bytecode. The easiest solution there would be to manually try and understand the code and became quite easy with some educated guesses. But this made me wonder, would it be possible to turn this back into clean readable source code?  
The answer: Yes! You can solve the challenge by re-assembling the input file at [debug/4.txt](debug/4.txt), and decompiling it with `decompyle3`:

```Shell
$ python-reassembler debug/4.txt
[SUCCESS] Code object written to 'output.pyc'
$ decompyle3 output.pyc | tee output.py
# decompyle3 version 3.9.1
input_list = [
 4,54,41,0,112,32,25,49,33,3,0,0,57,32,108,23,48,4,9,70,7,110,36,8,108,7,49,10,4,86,43,102,126,92,0,16,58,41,89,78]
key_str = "J"
key_str = "_" + key_str
key_str = key_str + "o"
key_str = key_str + "3"
key_str = "t" + key_str
key_list = [ord(char) for char in key_str]
while len(key_list) < len(input_list):
    key_list.extend(key_list)

result = [a ^ b for a, b in zip(input_list, key_list)]
result_text = "".join(map(chr, result))
# okay decompiling output.pyc
$ python -i output.py
>>> result_text
'picoCTF{...}'
```

## Installation

```Bash
git clone https://github.com/JorianWoltjer/python-reassembler.git && cd python-reassembler
python3 -m pip install -e .
```

Then use the `python-reassembler` binary on any file to re-assemble it.

## Testing

To ensure correctness of the output this tool generates, several tests are included in the [`tests/`](tests/) folder. Using [pytest](https://docs.pytest.org/en/latest/index.html) these can be ran. 

First, it compares **real source code** against re-assembled and decompiled output to make sure the result is the same. Then it also compares **compiled and decompiled code** against the re-assembled and decompiled output, to make sure any issues aren't just bugs in the `decompyle3` decompiler.

If you find any input that does not re-assemble correctly, please write a new `.py` file into the [`tests/`](tests/) folder that fails to be re-assembled, and create an [Issue](https://github.com/JorianWoltjer/python-reassembler/issues) showing the input, and/or a [Pull Request](https://github.com/JorianWoltjer/python-reassembler/pulls) that fixes it!

## Resources

* Disassembler format: https://github.com/python/cpython/blob/3.12/Lib/dis.py#L304
* Opcode list with examples and description: https://unpyc.sourceforge.net/Opcodes.html + Each Python version showing opcodes in source code: https://github.com/python/cpython/blob/3.12/Lib/opcode.py
* Write `__code__` object to `.pyc` file: https://book.jorianwoltjer.com/languages/python#decompiling-co_code-bytecode
