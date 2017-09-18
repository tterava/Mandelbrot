# Mandelbrot
Mandelbrot set visualization with Python, C and CUDA.
![alt text](http://url/to/img.png)

# Dependencies:
CUDA Toolkit, Pygame, Numpy

# Usage:
The included CUDA-extension must be compiled with nvcc-compiler.
It creates a shared library containing the fast methods to iterate the values of the set
which can be directly called from native Python code.

Edit the Makefile and make sure your python path and GPU architecture are correct.
List of compute levels for each Nvidia GPU: https://developer.nvidia.com/cuda-gpus

Simple run "make" in terminal and the extension is compiled.
