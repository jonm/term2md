# term2md

This is a text processing utility that will convert input containing
[ANSI escape sequences](https://en.wikipedia.org/wiki/ANSI_escape_code)
into nearly-equivalent Markdown.

This is not currently a universal converter, since Markdown cannot
express all of the formatting possible with the ANSI control
characters. However, it does a reasonable job of handling green, red,
and bold text.

`term2md` was written originally so that output from a tool designed
for terminal output could be added via continuous integration as
comments on pull requests.

## Installation

```
$ pip install term2md
```

In addition to installing the core Python module, it will also install
a `term2md` executable script for you.

