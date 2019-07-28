#!/usr/bin/env python3

# MIT License

# Copyright (c) 2019 Jonathan Moore

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import re
import sys

RESET = "\x1b[0m"
BOLD = "\x1b[1m"
RED = "\x1b[31m"
GREEN = "\x1b[32m"

def _is_control(part):
    return re.match("^\x1b\\[[0-9]*m$", part) is not None

def _modes_in_line(parts, in_mode):
    modes = {}
    cur_mode = in_mode
    for part in parts:
        if part in (RESET, BOLD, RED, GREEN):
            cur_mode = part
        elif part.strip() != "":
            modes[cur_mode] = True
    return modes

def _non_control(parts):
    return filter(lambda p: not _is_control(p), parts)

def _leading(parts, in_mode, rg):
    cur_mode = in_mode
    state = None
    for part in parts:
        if _is_control(part):
            cur_mode = part
        elif part.strip() != "":
            return cur_mode == rg

def _final_mode(parts, in_mode):
    out = in_mode
    for part in parts:
        if _is_control(part): out = part
    return out
        
def compress_bold(out_parts):
    out = []
    i = 0
    bold = False
    while i < len(out_parts):
        if out_parts[i] == "**" and bold:
            j = i + 1
            while (j < len(out_parts) and out_parts[j] != "**"
                   and out_parts[j].strip() == ""):
                j += 1
            if j < len(out_parts) and out_parts[j] == "**":
                k = i + 1
                while k < j:
                    out.append(out_parts[k])
                    k += 1
                i = j + 1
                continue
            bold = False
        elif out_parts[i] == "**":
            bold = True

        out.append(out_parts[i])
        i += 1
    return out
        
def convert_f(f):
    mode = RESET
    in_diff = False
    for line in f:
        if line.endswith('\n'):
            line = line.replace("\n","")
        
        out_parts = []
        parts = re.split("(\x1b\\[[0-9]*m)", line)
        line_modes = _modes_in_line(parts, mode)

        if (list(line_modes.keys()) == [] and mode in (RED, GREEN)
            and RESET not in parts):
            if mode == RED:
                out_parts.append("-")
            else:
                out_parts.append("+")
            out_parts.append(''.join(_non_control(parts)))
            out_parts.append("\n")
            yield ''.join(out_parts)
            continue
        
        if list(line_modes.keys()) == [GREEN] or _leading(parts, mode, GREEN):
            if not in_diff:
                yield "```diff\n"
                in_diff = True
            out_parts.append("+")

            printable = ''.join(_non_control(parts))
            if printable.strip().startswith("+"):
                printable = printable.replace("+"," ",1)
            out_parts.append(printable)
            
            for part in parts:
                if part in (RESET, BOLD, RED, GREEN):
                    mode = part
            out_parts.append('\n')
            yield ''.join(out_parts)
            continue

        if list(line_modes.keys()) == [RED] or _leading(parts, mode, RED):
            if not in_diff:
                yield "```diff\n"
                in_diff = True
            out_parts.append("-")
 
            printable = ''.join(_non_control(parts))
            if printable.strip().startswith("-"):
                printable = printable.replace("-"," ",1)
            out_parts.append(printable)
            
            for part in parts:
                if part in (RESET, BOLD, RED, GREEN):
                    mode = part
            out_parts.append('\n')
            yield ''.join(out_parts)
            continue

        if in_diff:
            yield "```\n"
            in_diff = False

        in_mode = mode
        for part in parts:
            if part in (RESET, BOLD):
                mode = part

            if _is_control(part): continue

            stripped = part.strip()
            if stripped != part and mode == BOLD:
                out_parts.append(part[:part.find(stripped)])
                out_parts.append("**")
                out_parts.append(stripped)
                out_parts.append("**")
                out_parts.append(part[part.find(stripped)+len(stripped):])
            elif mode == BOLD:
                out_parts.append("**")
                out_parts.append(part)
                out_parts.append("**")
            else:
                out_parts.append(part)

        mode = _final_mode(parts, in_mode)

        out_parts = compress_bold(out_parts)
                
        out_parts.append('\n')
        yield ''.join(out_parts)

    if in_diff:
        yield "```\n"

def convert(lines):
    out = []
    for line in convert_f(lines):
        out.append(line)
    return out

def main():
    for line in convert_f(sys.stdin):
        sys.stdout.write(line)

if __name__ == "__main__":
    main()
