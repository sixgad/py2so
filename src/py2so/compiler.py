# -*- coding: utf-8 -*-
import os

from setuptools import Extension, setup
from Cython.Build import cythonize


def pyencrypt(files):
    extentions = []
    for full_filename in files:
        filename = full_filename[:-3].replace(os.path.sep, '.')
        extention = Extension(filename, [full_filename])
        extention.cython_c_in_temp = True
        extentions.append(extention)
    setup(
        script_args=["build_ext"],
        ext_modules=cythonize(extentions, quiet=False, language_level=3, nthreads=1, build_dir="tmp_build"),
    )
