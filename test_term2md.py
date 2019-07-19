#!/usr/bin/env python3

import pytest

from term2md import *

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
    
def test_should_fail():
    assert True    

