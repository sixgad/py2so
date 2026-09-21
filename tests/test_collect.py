# -*- coding: utf-8 -*-
"""文件收集与 ignore 过滤的行为测试（不触碰真实编译）。"""
import os

import pytest

from py2so import cli, collect


def make_tree(root):
    files = [
        "main.py",
        "run.txt",
        os.path.join("pkg", "__init__.py"),
        os.path.join("pkg", "mod.py"),
        os.path.join("sub", "kept.py"),
        os.path.join("sub", "ignored_dir", "y.py"),
        os.path.join("sub", "ignored_dir", "deep", "x.py"),
        os.path.join("sub", "__pycache__", "stale.pyc"),
    ]
    for rel in files:
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("# placeholder\n", encoding="utf-8")


def relpaths(files, root):
    return sorted(os.path.relpath(f, root) for f in files)


def parse(argv):
    return cli.build_parser().parse_args(argv)


def test_ignore_directory_excludes_all_py(tmp_path):
    """回归: -i 目录忽略不应崩溃，且目录(含子目录)下 .py 全部排除。"""
    make_tree(tmp_path)
    opts = parse(["-d", str(tmp_path), "-i", "sub/ignored_dir/"])
    result = relpaths(collect.get_encfile_list(opts), str(tmp_path))
    assert result == sorted(["main.py", os.path.join("pkg", "mod.py"),
                             os.path.join("sub", "kept.py")])


def test_ignore_files(tmp_path):
    make_tree(tmp_path)
    opts = parse(["-d", str(tmp_path), "-i", "main.py," + os.path.join("pkg", "mod.py")])
    result = relpaths(collect.get_encfile_list(opts), str(tmp_path))
    assert result == sorted([
        os.path.join("sub", "ignored_dir", "deep", "x.py"),
        os.path.join("sub", "ignored_dir", "y.py"),
        os.path.join("sub", "kept.py"),
    ])


def test_init_py_excluded_from_compile(tmp_path):
    make_tree(tmp_path)
    opts = parse(["-d", str(tmp_path)])
    result = relpaths(collect.get_encfile_list(opts), str(tmp_path))
    assert os.path.join("pkg", "__init__.py") not in result
    assert os.path.join("pkg", "mod.py") in result


def test_directory_not_exist_raises(tmp_path):
    opts = parse(["-d", str(tmp_path / "nope")])
    with pytest.raises(collect.Py2soError):
        collect.get_encfile_list(opts)


def test_no_args_raises():
    opts = parse([])
    with pytest.raises(collect.Py2soError):
        collect.get_encfile_list(opts)


def test_single_file(tmp_path):
    target = tmp_path / "tool.py"
    target.write_text("# x\n", encoding="utf-8")
    opts = parse(["-f", str(target)])
    assert collect.get_encfile_list(opts) == [str(target)]


def test_single_file_wrong_extension_raises():
    opts = parse(["-f", "tool.txt"])
    with pytest.raises(collect.Py2soError):
        collect.get_encfile_list(opts)


def test_not_compile_files_keeps_non_py_and_pyc_excluded(tmp_path):
    make_tree(tmp_path)
    opts = parse(["-d", str(tmp_path), "-i", "sub/ignored_dir/"])
    will = collect.get_encfile_list(opts)
    others = collect.get_not_compile_files(opts, will)
    rel = relpaths(others, str(tmp_path))
    assert "run.txt" in rel
    assert os.path.join("pkg", "__init__.py") in rel
    assert os.path.join("sub", "ignored_dir", "y.py") in rel
    assert not any(f.endswith(".pyc") for f in rel)
    assert os.path.join("pkg", "mod.py") not in rel  # 已编译的不重复拷贝
