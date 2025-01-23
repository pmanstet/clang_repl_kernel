import os
import sys
import json
from tempfile import TemporaryDirectory
from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from jupyter_client.kernelspec import KernelSpecManager

kernel_json = {
    "argv": ["python", "-m", "clang_repl", "-f", "{connection_file}"],
    "display_name": "clang_repl",
    "language": "c++",
}

class CustomHook(BuildHookInterface):
    def initialize(self, version, build_data):
        here = os.path.abspath(os.path.dirname(__file__))
        sys.path.insert(0, here)
        prefix = os.path.join(here, 'data_kernelspec')

        with TemporaryDirectory() as td:
            os.chmod(td, 0o755) # Starts off as 700, not user readable
            with open(os.path.join(td, 'kernel.json'), 'w') as f:
                json.dump(kernel_json, f, sort_keys=True)
            KernelSpecManager().install_kernel_spec(td, 'clang_repl', user=False, prefix=prefix)

