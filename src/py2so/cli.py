# -*- coding: utf-8 -*-
import sys
import platform
import argparse

from . import collect
from . import compiler
from . import output


def build_parser():
    parser = argparse.ArgumentParser(description="py2so use help")
    # 不允许同时设置-f -d
    exptypegroup = parser.add_mutually_exclusive_group()
    exptypegroup.add_argument("-f", "--file", help="Python文件 (如果使用-f, 将编译单个Python文件)", default="")
    exptypegroup.add_argument("-d", "--directory", help="Python项目路径 (如果使用-d参数, 将编译整个Python项目)", default="")

    parser.add_argument("-i", "--ignore", help="""标记你不想编译的文件或文件夹路径
                          注意: 文件夹需要以路径分隔符号（`/`或`\\`，依据系统而定）结尾，并且需要和-d参数一起使用
                          例: -i main.py,mod/__init__.py,exclude_dir/""")

    parser.add_argument("-r", "--remove", help="清除所有中间文件，只保留加密结果文件，默认False", action="store_true", default=False)
    return parser


def main(argv=None):
    opts = build_parser().parse_args(argv)
    if platform.system() == "Windows":
        print("只支持linux，windows下可以使用pyinstaller打包exe")
        return 1

    # 获取所有待编译py文件
    try:
        will_compile_files = collect.get_encfile_list(opts)
    except collect.Py2soError as err:
        print(err)
        return 2
    # 清空上一次运行生成的临时文件
    output.clear_builds()
    # 编译py为so或pyd
    compiler.pyencrypt(will_compile_files)
    # 将编译好的工程输出到result文件夹
    output.gen_project(opts, will_compile_files)
    return 0


if __name__ == "__main__":
    sys.exit(main())
