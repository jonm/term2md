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
    return filter(lambda p: p not in (RESET, BOLD, RED, GREEN), parts)

def _leading(parts, in_mode, rg):
    modes = _modes_in_line(parts, in_mode)
    if len(modes) != 2 or rg not in modes or RESET not in modes:
        return False

    cur_mode = in_mode
    state = None
    for part in parts:
        if part in (rg, RESET):
            cur_mode = part
        elif part.strip() != "":
            if state == None and cur_mode == rg:
                state = rg
            elif state == rg and cur_mode == rg:
                pass
            elif state == rg and cur_mode == RESET:
                state = RESET
            elif state == RESET and cur_mode == RESET:
                pass
            else:
                return False
    return True

def convert(lines):
    out = []
    mode = RESET
    in_diff = False
    for line in lines:
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
            out.append(''.join(out_parts))
            continue
        
        if list(line_modes.keys()) == [GREEN] or _leading(parts, mode, GREEN):
            if not in_diff:
                out.append("```diff\n")
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
            out.append(''.join(out_parts))
            continue

        if list(line_modes.keys()) == [RED] or _leading(parts, mode, RED):
            if not in_diff:
                out.append("```diff\n")
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
            out.append(''.join(out_parts))
            continue

        if in_diff:
            out.append("```\n")
            in_diff = False
        
        if mode == BOLD:
            out_parts.append("**")
        for part in parts:
            if part in (RESET, BOLD, RED, GREEN):
                if (mode, part) == (RESET, BOLD):
                    out_parts.append("**")
                elif (mode, part) == (BOLD, RESET):
                    out_parts.append("**")
                mode = part
                continue

            out_parts.append(part)
        if mode == BOLD:
            out_parts.append("**")
        out_parts.append('\n')
        out.append(''.join(out_parts))

    if in_diff:
        out.append("```\n")
        
    return out

def main():
    lines = sys.stdin.readlines()
    out_lines = convert(lines)
    for ol in out_lines: sys.stdout.write(ol)

if __name__ == "__main__":
    main()
