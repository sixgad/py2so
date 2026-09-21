# -*- coding: utf-8 -*-
import os


class Py2soError(Exception):
    """用户可直接定位的输入或环境错误"""


def getfiles_inpath(dir_path,
                    includeSubfolder=True,
                    path_type=0,
                    ext_names="*"):
    '''
        获得指定目录下的所有文件，
        :param dir_path: 指定的目录路径
        :param includeSubfolder: 是否包含子文件夹里的文件，默认 True
        :param path_type: 返回的文件路径形式
            0 绝对路径，默认值
            1 相对路径
            2 文件名
        :param ext_names: "*" | string | list
            可以指定文件扩展名类型，支持以列表形式指定多个扩展名。默认为 "*"，即所有扩展名。
            举例：".txt" 或 [".jpg",".png"]

        :return: 以 yield 方式返回结果
    '''

    if isinstance(ext_names, str):
        ext_names = None if ext_names == "*" else [ext_names.lower()]
    elif isinstance(ext_names, list):
        ext_names = [ext.lower() for ext in ext_names]

    def keep_file_byextname(file_name):
        if ext_names is None:
            return True
        if file_name[0] == '.':
            file_ext = file_name
        else:
            file_ext = os.path.splitext(file_name)[1]
        return file_ext.lower() in ext_names

    if includeSubfolder:
        len_of_inpath = len(dir_path)
        for root, dirs, files in os.walk(dir_path):
            for file_name in files:
                if not keep_file_byextname(file_name):
                    continue
                if path_type == 0:
                    yield os.path.join(root, file_name)
                elif path_type == 1:
                    yield os.path.join(
                        root[len_of_inpath:].lstrip(os.path.sep), file_name)
                else:
                    yield file_name
    else:
        for file_name in os.listdir(dir_path):
            filepath = os.path.join(dir_path, file_name)
            if os.path.isfile(filepath):
                if not keep_file_byextname(file_name):
                    continue
                if path_type == 0:
                    yield filepath
                else:
                    yield file_name


def make_dir(dirpath):
    '''
    创建目录
        支持多级目录，若目录已存在自动忽略
    '''

    dirpath = dirpath.strip().rstrip(os.path.sep)

    if dirpath:
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)


def _normalize_rel(path):
    return os.path.normcase(os.path.normpath(path))


def collect_compile_files(directory, ignore=""):
    """获取项目目录下待编译的 py 文件相对路径（已排序）。

    排除 __init__.py 与 ignore 项；ignore 为逗号分隔的相对路径，
    以路径分隔符结尾的项视为目录，递归排除其下所有文件。
    """

    pyfiles = [pyfile for pyfile in getfiles_inpath(dir_path=directory,
                                                    includeSubfolder=True,
                                                    path_type=1,
                                                    ext_names=".py")
               if not pyfile.endswith('__init__.py')]

    exclude_files = set()
    for path_assign in (ignore or "").split(","):
        path_assign = path_assign.strip()
        if not path_assign:
            continue
        if path_assign[-1:] in ['/', '\\']:  # 末尾是路径分隔符则视为目录
            assign_dir = path_assign.strip('/\\')
            if not assign_dir or os.path.normpath(assign_dir) == '.':
                raise Py2soError(
                    "Invalid ignore entry '%s': a directory entry must name a path below the project" % path_assign)
            tmp_dir = os.path.join(directory, assign_dir)
            for file in getfiles_inpath(dir_path=tmp_dir,
                                        includeSubfolder=True,
                                        path_type=1):
                exclude_files.add(os.path.join(assign_dir, file))
        else:
            exclude_files.add(path_assign)

    exclude_norm = {_normalize_rel(p) for p in exclude_files}
    return sorted(p for p in pyfiles if _normalize_rel(p) not in exclude_norm)


def get_encfile_list(opts):
    """按命令行参数返回待编译文件的完整路径列表"""

    if opts.directory:
        if not os.path.exists(opts.directory):
            raise Py2soError("No such Directory, please check or use the Absolute Path")
        return [os.path.join(opts.directory, rel)
                for rel in collect_compile_files(opts.directory, opts.ignore)]

    elif opts.file:
        if opts.file.endswith(".py"):
            return [opts.file]
        raise Py2soError("Make sure you give the right name of py file")

    else:
        raise Py2soError("no -f or -d param")


def get_not_compile_files(opts, will_compile_files):
    """获取非编译文件（完整路径），排除 pyc 与已编译项"""

    if not opts.directory:
        return []
    files = getfiles_inpath(dir_path=opts.directory,
                            includeSubfolder=True,
                            path_type=1,
                            ext_names='*')
    files = [os.path.join(opts.directory, file) for file in files if not file.endswith('.pyc')]
    not_compile_files = list(set(files) - set(will_compile_files))
    return not_compile_files
