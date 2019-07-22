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

import pytest

from term2md.term2md import *

def test_empty():
    assert convert([]) == []

def test_single_plaintext():
    assert convert(["a plain text line\n"]) == ["a plain text line\n"]

def test_multiple_plaintext():
    input = ["first line\n", "second line\n"]
    assert convert(input) == input

def test_full_line_bold():
    input = ["\x1b[1ma bold choice\x1b[0m\n"]
    assert convert(input) == ["**a bold choice**\n"]

def test_inline_bold():
    input = ["a \x1b[1mbold\x1b[0m choice\n"]
    assert convert(input) == ["a **bold** choice\n"]

def test_adjacent_bold():
    input = ["a \x1b[1mbig, \x1b[1mbold\x1b[0m choice\n"]
    assert convert(input) == ["a **big, bold** choice\n"]

def test_bold_between_lines():
    input = ["a \x1b[1mbig,\n", "bold\x1b[0m choice\n"]
    assert convert(input) == ["a **big,**\n", "**bold** choice\n"]

def test_ignore_spurious_resets():
    assert convert(["\x1b[0m\n"]) == (["\n"])

def test_only_green():
    input = ["\x1b[32msome green text\x1b[0m\n"]
    assert convert(input) == ["```diff\n", "+some green text\n", "```\n"]

def test_only_red():
    input = ["\x1b[31msome red text\x1b[0m\n"]
    assert convert(input) == ["```diff\n", "-some red text\n", "```\n"]

def test_consecutive_green():
    input = ["\x1b[32msome green text\x1b[0m\n",
             "\x1b[32mand more of it\x1b[0m\n"]
    assert convert(input) == ["```diff\n", "+some green text\n",
                              "+and more of it\n", "```\n"]

def test_consecutive_red():
    input = ["\x1b[31msome red text\x1b[0m\n",
             "\x1b[31mand more of it\x1b[0m\n"]
    assert convert(input) == ["```diff\n", "-some red text\n",
                              "-and more of it\n", "```\n"]

def test_mixed_red_and_green():
    input = ["\x1b[31msome red text\x1b[0m\n",
             "\x1b[32mand some green\x1b[0m\n"]
    assert convert(input) == ["```diff\n", "-some red text\n",
                              "+and some green\n", "```\n"]

def test_running_green():
    input = ["\x1b[32msome green text\n",
             "and more of it\x1b[0m\n"]
    assert convert(input) == ["```diff\n", "+some green text\n",
                              "+and more of it\n", "```\n"]
    
def test_green_then_nondiff():
    input = ["\x1b[32msome green text\x1b[0m\n",
             "and some normal\n"]
    assert convert(input) == ["```diff\n", "+some green text\n",
                              "```\n", "and some normal\n"]

def test_green_text_with_leading_plus():
    input = ["\x1b[32m + some green text\x1b[0m\n"]
    assert convert(input) == ["```diff\n", "+   some green text\n", "```\n"]

def test_red_text_with_leading_minus():
    input = ["\x1b[31m - some red text\x1b[0m\n"]
    assert convert(input) == ["```diff\n", "-   some red text\n", "```\n"]

def test_green_running_across_blank_line():
    input = ["\x1b[32msome green text\n","\n","more green text\x1b[0m\n"]
    assert convert(input) == ["```diff\n", "+some green text\n",
                              "+\n", "+more green text\n", "```\n"]

def test_red_running_across_blank_line():
    input = ["\x1b[31msome red text\n","\n","more red text\x1b[0m\n"]
    assert convert(input) == ["```diff\n", "-some red text\n",
                              "-\n", "-more red text\n", "```\n"]

def test_line_with_only_resets_closes_diff():
    input = ["\x1b[31msome red text\n","\x1b[0m\n"]
    assert convert(input) == ["```diff\n",
                              "-some red text\n",
                              "```\n",
                              "\n"]

def test_leading_green_can_be_green():
    input = [" \x1b[32m+\x1b[0m plain\n"]
    assert convert(input) == ["```diff\n",
                              "+   plain\n",
                              "```\n"]

def test_leading_red_can_be_red():
    input = [" \x1b[31m-\x1b[0m plain\n"]
    assert convert(input) == ["```diff\n",
                              "-   plain\n",
                              "```\n"]

def test_strip_unsupported_sequences():
    assert convert(["\x1b[90mstuff\n"]) == ["stuff\n"]

def test_correctly_print_bold_leading_whitespace():
    assert convert(["\x1b[1m foo\n"]) == [" **foo**\n"]

def test_compress_no_bold():
    assert compress_bold(["foo"]) == ["foo"]

def test_compress_sequential_bold():
    assert compress_bold(["**","foo","**","**"," bar","**"]) == \
        ["**","foo"," bar","**"]

def test_compress_bold_across_whitespace():
    assert compress_bold(["**","foo","**"," ","**","bar","**"]) == \
        ["**","foo"," ","bar","**"]
    
