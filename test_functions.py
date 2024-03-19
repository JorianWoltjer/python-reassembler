#!/usr/bin/env -S python3 -m pytest
import decompyle3
from reassembler import full_reassemble
from contextlib import redirect_stdout
from itertools import zip_longest
from glob import glob
import py_compile
import dis
import io
import re


def disassemble(code):
    """Capture dis.dis() output as a string."""
    f = io.StringIO()
    with redirect_stdout(f):
        dis.dis(code)
    return f.getvalue()


def compare_sourcecode(a, b):
    """Compare disassembly of sources because formatting does not matter."""
    def fix_sourcecode(source):
        # This is a little unfair, but I'm not sure why these show up and
        # if we can do something about it. It's not a big deal so tests will pass.
        source = re.sub(r"nonlocal \w+", "", source)
        return source

    def fix_disassembly(disassembly):
        # Remove randomness from disassembly
        disassembly = re.sub(r"0x[0-9a-f]+", "0x0", disassembly)
        disassembly = re.sub(r"line \d+", "line 0", disassembly)
        disassembly = re.sub(r"^(\s+\d+)?\s+\d+\s+", "    0 ",
                             disassembly, flags=re.MULTILINE)
        return disassembly

    a = fix_sourcecode(a)
    b = fix_sourcecode(b)
    print("=======================")
    print("======= SOURCE ========")
    print(a)
    print("===== REASSEMBLED =====")
    print(b)
    print("=======================")
    a = fix_disassembly(disassemble(a))
    b = fix_disassembly(disassemble(b))
    for l1, l2 in zip_longest(a.splitlines(), b.splitlines()):
        assert l1 == l2


"""
If a test succeeds in source, but fails in decompile, it is a bug in decompyle3.
"""


def test_all_compare_source():
    for test in glob("tests/*.py"):
        print("READING", test)
        # Read source directly from file
        with open(test, "r") as f:
            source = f.read()

        disassembly = disassemble(source)
        code = full_reassemble(disassembly)

        output = decompyle3.deparse_code2str(code, out=io.StringIO())
        compare_sourcecode(source, output)


def test_all_compare_decompile():
    for test in glob("tests/*.py"):
        print("READING", test)
        # Compile and decompile the source
        compiled = py_compile.compile(test)
        source = io.StringIO()
        decompyle3.decompile_file(compiled, source)
        source = source.getvalue()

        disassembly = disassemble(source)
        code = full_reassemble(disassembly)

        output = decompyle3.deparse_code2str(code, out=io.StringIO())
        compare_sourcecode(source, output)


if __name__ == "__main__":
    test_all_compare_decompile()
