from ipykernel.kernelapp import IPKernelApp
from . import ClangReplKernel

IPKernelApp.launch_instance(kernel_class=ClangReplKernel)
