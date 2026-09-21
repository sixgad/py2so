# -*- coding: utf-8 -*-
import os

from setuptools import Extension, setup
from Cython.Build import cythonize
from Cython.Compiler import Options as CythonOptions

# 产物硬化参数：剥离符号与调试信息、关闭函数签名嵌入、不编入 docstring
COMPILE_ARGS = ["-O3", "-g0"]
LINK_ARGS = ["-s"]
DIRECTIVES = {"binding": False}


def pyencrypt(files):
    # Cython 3 的 docstring 剥离开关是编译期读取的模块全局量，不在 directive 表中
    CythonOptions.docstrings = False
    extentions = []
    for full_filename in files:
        filename = full_filename[:-3].replace(os.path.sep, '.')
        extention = Extension(filename, [full_filename],
                              extra_compile_args=COMPILE_ARGS,
                              extra_link_args=LINK_ARGS)
        extention.cython_c_in_temp = True
        extentions.append(extention)
    setup(
        script_args=["build_ext"],
        ext_modules=cythonize(extentions, quiet=False, language_level=3, nthreads=1,
                              build_dir="tmp_build", compiler_directives=DIRECTIVES),
    )
