import pexpect
import tempfile
import uuid
import subprocess
import re
import tomllib
import json
from pathlib import Path

class ClangRepl:
    """ Wrapper for clang-repl """

    def __init__(self):
        """ Prepare kernel settings and spawn """

        default_options = \
            {'defaults': 
                {
                    'repl': 'clang-repl',
                    'args': ['-std=c++23', '-ferror-limit=3', '-O1'],
                    'includes': ['iostream'],
                    'libs': [], 
                    'timeout': 10,
                    'debug': False
                }
            }

        cfg = Path.home() / ".clang-repl"
        if not cfg.is_file():
            user_options = {}
        else:
            with open(cfg, "rb") as f: user_options = tomllib.load(f)

        options = default_options | user_options

        self.clrepl = options["defaults"]["repl"]
        self.clrepl_args = []
        [self.clrepl_args.extend(("--Xcc", arg)) for arg in options["defaults"]["args"]]
        self.clrepl_includes = [fr"#include <{header}>" for header in options["defaults"]["includes"]]
        self.clrepl_libs = [fr"%lib {libname}" for libname in options["defaults"]["libs"]]                
        self.timeout = int(options["defaults"]["timeout"])
        self.debug = bool(options["defaults"]["debug"])

        # clang-repl session constants
        self.prompt = r"clang-repl> "
        self.continuation_prompt = r"clang-repl...   "
        self.prefix = r"cell-"
        self.suffix = r".repl"
        # pattern matching cell includes, example: #include "/tmp/cell-p1vr4ba2.repl"
        self.re_header_pattern = re.compile(fr"^#include\s\".*{self.prefix}.*{self.suffix}\".*$", flags=re.M)
        # pattern matching error header, example: "In file included from ..."
        self.re_error_header_pattern = re.compile(r"^In\sfile\sincluded\sfrom\s.*:.*$", flags=re.M)
        # pattern matching error prefix, example: "/tmp/cell-9e_ghjd6.repl:1:7: error: ..."
        self.re_error_msg_pattern = re.compile(fr"{self.prefix}.+\{self.suffix}:\d+:\d+:.*\serror:\s")
        # pattern matching lib loads, example: "%lib libomp.so"
        self.re_lib_pattern = re.compile(fr"^%lib\s.*$", flags=re.M)
        # pattern matching %lib errors, example: "error: libomp.s: cannot open ..."
        self.re_error_lib_pattern = re.compile(r"^error:\s.*:\s")
        # pattern matching undo, example: "%undo"
        self.re_undo_pattern = re.compile(fr"^%undo.*$", flags=re.M)
        # remove ansi colors from output
        self.re_rm_ansi = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

        self.child = None
        self.debug_defaults = []
        try:

            self.debug_defaults.append(f"default options: {json.dumps(default_options, sort_keys=True, indent=2)}")
            self.debug_defaults.append(f"user options: {json.dumps(user_options, sort_keys=True, indent=2)}")         
            self.debug_defaults.append(f"effective options: {json.dumps(options, sort_keys=True, indent=2)}")                     

            version_dump = subprocess.run(
                [self.clrepl, '--version'], check=True, capture_output=True, text=True).stdout
            self.debug_defaults.append(f"clang-repl found: {self.clrepl} {version_dump}")
            # pexpect: spawn new session
            self.child = pexpect.spawn(
                self.clrepl, self.clrepl_args, encoding='utf-8', echo=False, timeout=5)
            self.child.delaybeforesend = 0.05
            self.child.expect_exact(
                [self.prompt, pexpect.TIMEOUT, pexpect.EOF], timeout=2)

            # load defaults
                           
            for include in self.clrepl_includes:
                if not self.child.isalive(): break
                res, alive, timed_out, error, debug_str = self.raw_line(include)
                self.debug_defaults.append(debug_str)

            for lib in self.clrepl_libs:
                if not self.child.isalive(): break
                res, alive, timed_out, error, debug_str = self.raw_line(lib)
                self.debug_defaults.append(debug_str)

        except Exception as error: 
            self.debug_defaults.append(f"fatal: could not spawn clang-repl session ({self.clrepl})")
            self.debug_defaults.append(f"{error}")
  
    def line_repl(self, line, timeout):
        """ Forward single line to repl session, block, and process result """

        self.child.sendline(line)
        idx = self.child.expect_exact(
            [self.prompt, pexpect.TIMEOUT, pexpect.EOF], timeout=timeout)
        res = self.child.before

        # idx == 0 -> success (back to prompt after sending the line)
        # idx == 1 -> timeout (no prompt after timeout, might be stuck or still running)
        # idx == 2 -> EOF (repl session exited unexpectedly)
        if idx == 1: self.child.close(force=True)

        alive = True if idx == 0 else False
        timed_out = True if idx == 1 else False

        # remove ansi colors
        res_ascii = self.re_rm_ansi.sub('', res)

        # check for errors
        error_compile = True if self.re_error_msg_pattern.search(res_ascii) is not None else False
        error_lib = True if self.re_error_lib_pattern.search(res_ascii) is not None else False
        error = error_compile or error_lib

        debug_str = fr"""-- repl in ---------------------------
{line}
-- repl out begin --------------------
{res}
-- repl out end ----------------------
alive:     {alive}
timed_out: {timed_out}
error:     {error}
--------------------------------------
"""

        return res, alive, timed_out, error, debug_str


    def raw_line(self,line):
        return self.line_repl(line,self.timeout)

    def run(self,cell):
        """ Run content of a cell """

        firstline = cell.splitlines()[0]

        # trigger display of kernel status if errors occured during init or due to request via %status
        if self.child is None or firstline.startswith(r"%status"):
            res = "\n".join(self.debug_defaults)
            alive = self.child is not None and self.child.isalive()
            return res, alive

        # check for active session
        if not self.child.isalive():
            res = f"could not execute cell: clang-repl session is dead; you need to restart the kernel."
            alive = False
            return res.strip(), alive

        # trigger dynamic library load via %lib
        if firstline.startswith(r"%lib"):
            res, alive, timed_out, error, debug_str = self.raw_line(firstline)
            res = self.re_lib_pattern.sub('', res)
            res.strip()
            if self.debug:
                res = res + debug_str
            return res.strip(), alive and not timed_out

        # comment first line of cell if magic command(s) are present
        if firstline.startswith(r"%"):
            cell = cell.replace("%", "// %", 1)

            # use custom user timeout if present %timeout=[...]
            match = re.search(r'%timeout=([0-9]+)', firstline)
            if match and match.groups()[1]:
                timeout = int(match.groups()[1])
            else:
                timeout = self.timeout

            # apply "wrap and call" if %main is present
            if r"%main" in firstline:
                fn_name = fr"main{uuid.uuid4().hex[0:8]}"
                cell = f"""void {fn_name}() {{ {cell}
                }}; {fn_name}();
                """

        # regular cell
        with tempfile.NamedTemporaryFile(delete=False, mode="w", prefix="cell-", suffix=".repl") as source:
            source.write(cell)
            source.close()
            include = source.name

        line = fr'#include "{include}"'
        res, alive, timed_out, error, debug_str = self.line_repl(line, timeout=self.timeout)

        # strip "noise" from repl output
        res = self.re_header_pattern.sub('', res)
        res = self.re_error_header_pattern.sub('', res)
        res = self.re_error_header_pattern.sub('', res)
        res = res.strip()

        # run %undo after successfull execution
        if firstline.startswith(r"%undo") and alive and not timeout and not error:
            undo_res, undo_alive, undo_timed_out, undo_error, undo_debug_str = self.raw_line(r"%undo")

            undo_res = self.re_undo_pattern.sub('', undo_res)
            res += undo_res.strip()
            alive = alive and undo_alive
            timed_out = timed_out or undo_timed_out
            debug_str += undo_debug_str

        if self.debug:
            res = res + debug_str
        
        if timed_out:
            res += f"clang-repl session was killed (due to timeout={self.timeout}s); you need to restart the kernel."
        return res.strip(), alive and not timed_out
