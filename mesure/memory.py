import sys
import typing as tp
import psutil
import types
from collections import deque
import inspect
import linecache
from mesure.utils import scale_memory_units, colored, styled, syntax_highlight

MONITOR = sys.monitoring
EVENTS = MONITOR.events
TRACKED_EVENTS = (
    (EVENTS.LINE, "LINE"),
    (EVENTS.CALL, "CALL"),
)
EVENT_SET = sum(ev for ev, _ in TRACKED_EVENTS)
TOOL = 2

class CodeMap(dict[types.CodeType, dict[int, tuple[float, float, int]]]):
   
    def __init__(self) -> None:
         self._toplevel = []
         super().__init__()

    def add(self, code: types.CodeType):
        if code in self:
            return
        self[code] = {}

    def trace(self, code, lineno, prev_lineno):
        memory = psutil.Process().memory_info().rss
        codelines = self[code]

        if prev_lineno in codelines:
            prev_mem, prev_inc, prev_occ = codelines[prev_lineno]
            codelines[prev_lineno] = (memory, prev_inc + (memory - prev_mem), prev_occ)
        else:
            codelines[prev_lineno] = (memory, 0.0, 1)

        if lineno in codelines:
            mem, inc, occ = codelines[lineno]
            codelines[lineno] = (memory, inc, occ + 1)
        else:
            codelines[lineno] = (memory, 0.0, 1)


class LineProfiler:

    def __init__(self) -> None:
        self.code_map = CodeMap()
        self.prev_lineno = None
        self.prevlines = deque()

        MONITOR.register_callback(TOOL, EVENTS.LINE, self.line_handler)
        MONITOR.register_callback(TOOL, EVENTS.CALL, self.call_handler)
        
    def line_handler(self, code, lineno):
        if code in self.code_map:
            self.code_map.trace(code, lineno, self.prev_lineno)
            self.prevlines.append(lineno)
            self.prev_lineno = self.prevlines[-1]

    def call_handler(self, code: types.CodeType, instruction_offset, call, arg0):
        if code in self.code_map:
            pass

    def profile(self, func):
        MONITOR.use_tool_id(TOOL, "line_profiler")
        MONITOR.set_events(TOOL, EVENT_SET)
        self.func = func
        code = func.__code__
        self.code_map.add(code)

        self.prevlines.append(code.co_firstlineno)
        self.prev_lineno = code.co_firstlineno
        func()
        MONITOR.set_events(TOOL, 0)
        MONITOR.free_tool_id(TOOL)

    def show_results(self, unit: tp.Literal["MB", "KB", "GB", "auto"] = "auto"):

        results = self.code_map[self.func.__code__].items()
        sourcefile = inspect.getsourcefile(self.func)
        all_lines = linecache.getlines(sourcefile)
        all_lines = list(map(syntax_highlight, all_lines))

        out = "-"*80
        out += f"\n{styled(self.func.__name__, 'bold')} in {sourcefile}\n"
        out += "-"*80
        out += f"\nLine #{'Mem usage':>13}{'Increment':>14}{'Occurrences':>14}{'Line Contents':>16}\n"
        out += "="*80
        for lineno, info in sorted(results):
            usage, increment, occurrences = info
            usage, _unit = scale_memory_units(usage, unit)
            usage_str = colored(f"{usage:.2f} {_unit:2}", "white")
            increment, _unit = scale_memory_units(increment, unit) 
            inc_color = "red" if increment > 0 else "green" if increment < 0.0 else "white"
            inc_fmt = f"{increment:+.2f}" if increment != 0.0 else f"{increment:.2f}"
            inc_str = colored(f"{inc_fmt} {_unit:2}", inc_color)
            occ_str = colored(f"{occurrences}", "white")
            out += f"\n{lineno:>6}  {usage_str:>20}   {inc_str:>20}   {occ_str:>20}   {all_lines[lineno-1][:-1]}"

        print(out)


def some_function():
   a = [1] * (10 ** 6)
   b = [2] * (2 * 10 ** 7)
   for i in range(10):
       a.append(b.copy())
   del b
   ciao = "a string with for in it"
   # comment
   return a

if __name__ == "__main__":

    lp = LineProfiler()
    lp.profile(some_function)
    lp.show_results()