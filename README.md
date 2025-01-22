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
git clone https://gitlab.tuwien.ac.at/paul.manstetten/clang_repl_kernel.git
cd clang_repl_kernel
python -m venv .venv
source .venv/bin/activate
pip install jupyter-console
# pip install ipykernel notebook nbclassic jupyter_server_ydoc jupyter-console
# python -m ipykernel install --user --name=.venv # unsure if needed
python -m pip install -e . # editable install
jupyter kernelspec list # should now also list "clang_repl   .venv/share/jupyter/kernels/clang_repl"
jupyter notebook --kernel clang_repl demo.ipynb
jupyter console --kernel clang_repl
```

### Related links:

- https://hex.tech/blog/jupyter-kernel-overview/
- https://jupyter-client.readthedocs.io/en/stable/wrapperkernels.html
- https://github.com/llvm/llvm-project/commits?author=vgvassilev (`clang-repl` related development)