# *clang-repl* based kernel for Jupyter notebooks

## Overview

- This is a kernel enabling using C++ in a [*Jupyter Notebook*](https://jupyter-notebook.readthedocs.io)
- It bases on a minimalistic instrumentation of the interactive [*clang-repl*](https://clang.llvm.org/docs/ClangRepl.html) prompt using
	- this [showcase](https://github.com/jupyter/echo_kernel/) for [`ipykernel.kernelbase.kernel`](https://github.com/ipython/ipykernel/blob/main/ipykernel/kernelbase.py) as blueprint for the overall project structure, and
	- [`python-pexpect`](https://pexpect.readthedocs.io/) for instrumenting the `clang-repl>` prompt.

## Motivation

- The motivation is to enable notebook-based learning material for C++.
- The focus is not on language interoperability between C++ and Python.
- Exploring the latest capabilities of `clang-repl` using different C++ language standards/settings in a convenient way.
- Existing projects providing a form of interactive C++ in notebooks do currently not support C++20/C++23 and use fixed/patched LLVM versions.

## Details

- It is required that `clang-repl` is installed on the (backend) system
- On launch, the kernel starts an interactive `clang-repl` session. 
- The default settings and initial includes/libs can be configured by placing a `.clang-repl` file in the users home directory, the defaults (if not `.clang-repl` file is present) are listed below
	```shell
	[defaults]
	repl = "clang-repl"
	args = ["-std=c++20", "-ferror-limit=3", "-O1"]
	includes = ["vector", "iostream"]
	libs = []
	timeout = 10
	debug = false
	```
- The kernel performs the following steps for each source cell
	0. Check if the `clang-repl` session is alive
	1. Inspect first line of the cell if starting with these *magic commands*
		- `%status`: print kernel status
		- `%lib`: forward first line of cell directly to `clang-repl`	
	2. Comment the first line (by prepending `//`) if it starts with `%`
	3. Transform the cell content if the first line contains a `%main`: the cell content is wrapped and run via a unique global function, e.g. `void mainUUID(){ ... }; mainUUID();`
    4. The (transformed) cell content is forwarded to `clang-repl` by always using a single line command realized via a indirection of, e.g. this form: `#include /tmp/cell-e3tp24ne.repl`
	5. The result of the interactive session (i.e. incremental compile + execute) is awaited (using a timeout) and printed as output of the cell.
	6. If the cell additionally contained a `%undo` in the first line (and the incremental compile + execute was successful) the cell is "undone" via sending a subsequent `%undo` directly to `clang-repl`

## Installation

```shell
python -m venv .venv
source .venv/bin/activate
python -m pip install clang-repl 

# demo notebook
jupyter notebook demo.ipynb

# new empty notebook
echo '{ "cells": [], "nbformat": 4, "nbformat_minor": 4,  "metadata": {} }' > empty.ipynb
jupyter notebook --MultiKernelManager.default_kernel_name=clang_repl empty.ipynb
```

## Installation (for development)
```shell
git clone https://github.com/pmanstet/clang_repl_kernel.git
cd clang_repl_kernel
# optional: use a fixed python version 
# pyenv install 3.11.10
# ~/.pyenv/versions/3.11.10/bin/python -m venv .venv 
python -m venv .venv 
source .venv/bin/activate
python -m pip install -e .
jupyter kernelspec list 

# interactive console
jupyter console --kernel clang_repl --debug

# demo notebook
jupyter notebook demo.ipynb
```
