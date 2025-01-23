from ipykernel.kernelbase import Kernel

from .clrepl import ClangRepl, __version__


class ClangReplKernel(Kernel):
    implementation = 'ClangRepl'
    implementation_version = __version__
    language = 'c++'
    language_info = {
        'codemirror_mode': 'text/x-c++src',
        'file_extension': '.cpp',
        'mimetype': 'text/x-c++src',
        'name': 'c++'
    }
    banner = "ClangRepl"

    def __init__(self, **kwargs):
        Kernel.__init__(self, **kwargs)
        self.repl = ClangRepl()

    def do_execute(self, code, silent, store_history=True, user_expressions=None,
                   allow_stdin=False):

        if not silent:
            res, alive = self.repl.run(code)
            if alive:
                stream_content = {'name': 'stdout', 'text': None if not res else res}
            else:
                stream_content = {'name': 'stderr', 'text': None if not res else res}
                
            self.send_response(self.iopub_socket, 'stream', stream_content)

        return {'status': 'ok',
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {},
               }
