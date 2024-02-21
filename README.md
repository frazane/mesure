# Mesure

A library for micro benchmarking and profiling of simple programs. It uses the new API for low impact monitoring  (`sys.monitoring`, see PEP 669) introduced in python 3.12 and `psutil` for sampling resource usage. Everything is printed (no fancy dashboards) and `plotext` is used for plots in the terminal.

## Features

### Line-by-line memory profiling
Inspired by https://github.com/pythonprofilers/memory_profiler


```python
--------------------------------------------------------------------------------
some_function in /users/fzanetta/pyprojects/mesure/mesure/memory.py
--------------------------------------------------------------------------------
Line #    Mem usage     Increment   Occurrences   Line Contents
================================================================================
   106     16.29 MB       0.00 B              1   def some_function():
   107     24.19 MB      +7.90 MB             1      a = [1] * (10 ** 6)
   108    184.14 MB    +159.95 MB             1      b = [2] * (2 * 10 ** 7)
   109      1.78 GB       0.00 B             11      for i in range(10):
   110      1.78 GB      +1.60 GB            10          a.append(b.copy())
   111      1.62 GB    -159.94 MB             1      del b
   112      1.62 GB       0.00 B              1      ciao = "a string with for in it"
   114      1.62 GB       0.00 B              1      return a
```

### Program CPU and memory usage


### Pretty timeit 

