## pypi publishing

```shell
# test release
git clone https://github.com/pmanstet/clang_repl_kernel.git
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
git clone https://github.com/pmanstet/clang_repl_kernel.git
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
