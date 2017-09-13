'''
Created on Jul 31, 2017

@author: tommi
'''
from distutils.core import setup, Extension

setup(
    ext_modules=[Extension("setcalc", ["setcalc.c"])],
)