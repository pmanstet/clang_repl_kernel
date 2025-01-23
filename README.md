# *clang-repl* based kernel for Jupyter notebooks

- This is a kernel enabling using C++ in a [*Jupyter Notebook*](https://jupyter-notebook.readthedocs.io)
- It bases on a minimalistic instrumentation of the interactive [*clang-repl*](https://clang.llvm.org/docs/ClangRepl.html) prompt using
	- this [showcase](https://github.com/jupyter/echo_kernel/) for [`ipykernel.kernelbase.kernel`](https://github.com/ipython/ipykernel/blob/main/ipykernel/kernelbase.py) as blueprint for the overall project structure, and
	- [`python-pexpect`](https://pexpect.readthedocs.io/) for instrumenting the `clang-repl>` prompt.

## Usage/details

- It is required that `clang-repl` is installed on the (backend) system
- On launch, the kernel starts an interactive `clang-repl` session. The default settings and initial includes/libs can be configured by placing a `.clang-repl` file in the users home directory ([example](.clang-repl)).
- The kernel performs the following steps for each source cell
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
git clone https://gitlab.tuwien.ac.at/paul.manstetten/clang_repl.git
cd clang_repl
python -m venv .venv
source .venv/bin/activate
python -m pip install -e . # editable install
jupyter kernelspec list # should now also list "clang_repl   .venv/share/jupyter/kernels/clang_repl"
jupyter notebook --kernel clang_repl demo.ipynb
jupyter console --kernel clang_repl
```

## pypi publishing

```shell
# test release
git clone https://gitlab.tuwien.ac.at/paul.manstetten/clang_repl_kernel.git
cd clang_repl_kernel
rm -rf .venv .testenv dist data_kernelspec
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade build twine
# note: bump version number (overriding is not supported on upload to pypi)
python -m build
# note: next step needs api token
python -m twine upload --repository testpypi --skip-existing dist/* 
deactivate
```

```shell
# test install of test release (no deps)
rm -rf .venv .testenv dist data_kernelspec
python -m venv .testenv
source .testenv/bin/activate 
python -m pip install --extra-index-url https://pypi.org/simple --index-url https://test.pypi.org/simple clang-repl
jupyter kernelspec list # should list clang_repl
jupyter console --kernel clang_repl # check if works (type: %status)
deactivate
```

```shell
# publish release
git clone https://gitlab.tuwien.ac.at/paul.manstetten/clang_repl_kernel.git
cd clang_repl_kernel
rm -rf .venv .testenv dist data_kernelspec
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade build twine
# note: bump version number (overriding is not supported on upload to pypi)
python -m build
# note: next step needs api token
python -m twine upload --repository pypi --skip-existing dist/* 
deactivate
```


### Related links:

- https://hex.tech/blog/jupyter-kernel-overview/
- https://jupyter-client.readthedocs.io/en/stable/wrapperkernels.html
- https://github.com/llvm/llvm-project/commits?author=vgvassilev (`clang-repl` related development)

