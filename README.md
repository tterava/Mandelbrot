# Mandelbrot
Mandelbrot set visualization with Python, C and CUDA.

[Winner of Siraj Raval's weekly coding challenge](https://youtu.be/5YxzWnbqaJI?t=12m6s)

![Picture](https://i.imgur.com/8T1Pzki.png)

# Dependencies:
CUDA Toolkit, Pygame, Numpy

# Installation:
The included CUDA-extension must be compiled with nvcc-compiler.
It creates a shared library containing the fast methods to iterate the values of the set
which can be directly called from native Python code.

## Linux (tested with Ubuntu 16.04 and Python 3.5):
Edit the Makefile and make sure your python path and GPU architecture are correct.
List of compute levels for each Nvidia GPU: https://developer.nvidia.com/cuda-gpus

Run "make" in terminal and the extension is compiled.
Finally run "python3 mandelbrot.py" to launch the program.

## Windows:
Getting nvcc compile the Python extension isn't nearly as easy as on Linux. You probably have to compile the CUDA parts separately into a linked library and then import those into the Python C-extension. Compiling the Python C-extension requires Visual Studio 2015.

# Usage:
Click with your mouse where you want to zoom and use numpad +/- to set the iterations to a comfortable level.
At some point the precision of 64-bit floating point variables won't be enough to dive any deeper and you end up with mosaic pattern.

# Performance:
The speed of the iterations seems to correlate very well with the raw double precision processing power. If your GPU can process them faster than your CPU, then the CUDA implementation will be faster after increasing the iteration level to the point where memory transfers aren't a bottleneck anymore.
