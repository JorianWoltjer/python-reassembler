#!/usr/bin/env python3
from ast import literal_eval
import dis
import opcode
import re

CO_VARIABLE_REFERENCES = {
    "co_consts": ["LOAD_CONST"],
    "co_names": ["STORE_NAME", "DELETE_NAME", "STORE_ATTR", "DELETE_ATTR", "LOAD_NAME", "LOAD_ATTR", "IMPORT_NAME", "IMPORT_FROM", "LOAD_GLOBAL", "LOAD_METHOD"],
    "co_varnames": ["STORE_FAST", "DELETE_FAST", "LOAD_FAST"],
    "co_cellvars": ["STORE_DEREF", "LOAD_CLOSURE"],
    "co_freevars": ["LOAD_DEREF"],
}
SECTION_PREFIX = "Disassembly of "


def parse_disassembly(lines):
    """Parse lines of disassembly into a list of workable tuples."""
    codes = []

    for line in lines:
        if len(line) == 0:
            continue  # Skip empty lines
        if line.startswith(SECTION_PREFIX):
            break  # Marks the end of this section

        parts = list(filter(lambda x: x not in [
                     "", ">>"], line[6:].split(" ")))
        _offset = int(parts[0])
        op_name = parts[1]
        arg = int(parts[2]) if len(parts) > 2 else None
        repr = ' '.join(parts[3:])[1:-1] if len(parts) > 3 else None

        codes.append((op_name, arg, repr))

    return codes


def get_code_base(name):
    """Get a fitting __code__ object for the given name."""
    name = re.search(r"<code object (\S+) at", name).group(1)

    if name == "<lambda>":
        return (lambda: None).__code__
    elif name == "<listcomp>":
        return (lambda: [None for _ in []]).__code__.co_consts[1]
    else:
        return (lambda: None).__code__.replace(co_name=name)


def get_consts(codes, sections={}):
    """Recursively get consts and resolve references to other sections."""
    consts = {}
    for code in codes:
        # Opcodes that use co_consts
        if code[0] == "LOAD_CONST":
            value = code[2]
            if value in sections:
                if type(sections[value]) == list:
                    # Recursive call to reassemble the sub-section
                    base = get_code_base(value)
                    sections[value] = reassemble(
                        sections[value], sections=sections, code_base=base
                    )

                value = sections[value]
            else:
                value = literal_eval(value)

            consts[code[1]] = value

    # Sort and fill gaps
    length = max(consts.keys(), default=-1) + 1
    consts = [consts[i] if i in consts else None for i in range(length)]
    return tuple(consts)


def get_co_any(codes, co_attr):
    """Find co_attr from codes."""
    vars = {}
    for code in codes:
        # Opcodes that use this co_attr
        if code[0] in CO_VARIABLE_REFERENCES[co_attr]:
            vars[code[1]] = code[2]

    # Sort and fill gaps
    length = max(vars.keys(), default=-1) + 1
    vars = [vars[i] if i in vars else None for i in range(length)]
    return tuple(vars)


def get_co_argcount(codes):
    """Count co_argcount from codes."""
    stored_first = set()
    load_first = set()
    for code in codes:
        if code[0] == "STORE_FAST" and code[1] not in load_first:
            stored_first.add(code[1])
        elif code[0] == "LOAD_FAST" and code[1] not in stored_first:
            load_first.add(code[1])

    return len(load_first)


def to_bytecode(codes):
    """Turn opcodes into bytecode."""
    bytecode = b""
    for code in codes:
        op_index = opcode.opname.index(code[0])
        arg = code[1] if code[1] is not None else 0

        bytecode += bytes([op_index, arg & 0xff])

    return bytecode


def reassemble(lines, sections={}, code_base=(lambda: None).__code__):
    """Recursively reassemble the code object from disassembly lines."""
    codes = parse_disassembly(lines)

    code = code_base.replace(
        co_consts=get_consts(codes, sections),
        co_names=get_co_any(codes, "co_names"),
        co_varnames=get_co_any(codes, "co_varnames"),
        co_cellvars=get_co_any(codes, "co_cellvars"),
        co_freevars=get_co_any(codes, "co_freevars"),
        co_argcount=get_co_argcount(codes),
        co_code=to_bytecode(codes),
    )

    return code


def full_reassemble(disassembly):
    """Parse sections from full disassembly and reassemble the main code object."""
    sections = {None: []}
    current_section = None

    for line in disassembly.splitlines():
        if line.startswith(SECTION_PREFIX):
            current_section = line[len(SECTION_PREFIX):-1]
            sections[current_section] = []
        else:
            sections[current_section].append(line)

    return reassemble(sections.pop(None), sections=sections)


def write_code_object(code, filename):
    """Write the code object to a .pyc file."""
    import importlib.util
    import marshal
    import sys

    with open(filename, "wb") as f:
        # Correct magic number that decompilers use
        f.write(importlib.util.MAGIC_NUMBER)
        f.write(b"\x00" * 8)
        if sys.version_info[1] >= 7:  # Extra 4 bytes in Python 3.7+
            f.write(b"\x00" * 4)

        f.write(marshal.dumps(code))

    print(f"[SUCCESS] Code object written to {filename!r}")


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Path to the input disassembly file")
    parser.add_argument("output", default="output.pyc", nargs="?",
                        help="Path to the output file")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="Suppress disassembly output")
    args = parser.parse_args()

    print(f"Opening {args.input!r} and reassembling the code object...")
    with open(args.input) as f:
        disassembly = f.read()

    main = full_reassemble(disassembly)

    if not args.quiet:
        dis.dis(main)
        print()

    write_code_object(main, args.output)
    print("Now use a decompiler like `uncompyle6`, `decompyle3`, or `pycdc` on the output to decompile it")


if __name__ == "__main__":
    main()
