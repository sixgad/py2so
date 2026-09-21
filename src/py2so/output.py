# -*- coding: utf-8 -*-
import os
import shutil

from .collect import getfiles_inpath, make_dir, get_not_compile_files


def clear_builds():
    if os.path.isdir("build"):
        shutil.rmtree("build")
    if os.path.isdir("tmp_build"):
        shutil.rmtree("tmp_build")
    if os.path.isdir("result"):
        shutil.rmtree("result")


def clear_tmps():
    if os.path.isdir("build"):
        shutil.rmtree("build")
    if os.path.isdir("tmp_build"):
        shutil.rmtree("tmp_build")


def gen_project(opts, will_compile_files):
    make_dir('result')
    for file in getfiles_inpath('build', True, 1, ['.so', '.pyd']):
        src_path = os.path.join('build', file)
        mid_path = os.path.sep.join(file.split(os.path.sep)[1:-1])
        file_name_parts = os.path.basename(src_path).split('.')
        file_name = '.'.join([file_name_parts[0]] + file_name_parts[-1:])
        dest_path = os.path.join('result', mid_path, file_name)
        make_dir(os.path.dirname(dest_path))
        shutil.copy(src_path, dest_path)
    # 非编译文件拷贝至生成库路径
    not_compile_files = get_not_compile_files(opts, will_compile_files)
    for not_compile_file in not_compile_files:
        dest_path = os.path.join('result', not_compile_file)
        filepath, filename = os.path.split(dest_path)
        make_dir(filepath)
        shutil.copyfile(not_compile_file, dest_path)

    if opts.remove:
        clear_tmps()
    print("\npy2so Encrypt Finished")
