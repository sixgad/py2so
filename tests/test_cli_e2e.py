# -*- coding: utf-8 -*-
"""CLI 端到端测试：mock 平台与编译执行，验证 result 装配、清理与错误退出码。"""
import os

from py2so import cli, compiler

SO_TAG = ".cpython-314-x86_64-linux-gnu.so"
BUILD_LIB = os.path.join("build", "lib.linux-x86_64-3.14")


def make_project(root):
    files = [
        "main.py",
        "data.txt",
        os.path.join("pkg", "__init__.py"),
        os.path.join("pkg", "mod.py"),
        os.path.join("ignored", "ig.py"),
    ]
    for rel in files:
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("# placeholder\n", encoding="utf-8")


def install_fake_platform_and_compiler(monkeypatch):
    """Linux 平台假象 + 按真实模块命名规则生成假编译产物"""
    monkeypatch.setattr(cli.platform, "system", lambda: "Linux")

    def fake_pyencrypt(files):
        # 与真实逻辑一致：模块名 = 路径去 .py 后分隔符转点，产物落在 build/lib.*/模块路径.so
        for full in files:
            modname = full[:-3].replace(os.path.sep, ".")
            artifact = os.path.join(BUILD_LIB, modname.replace(".", os.path.sep)) + SO_TAG
            os.makedirs(os.path.dirname(artifact), exist_ok=True)
            with open(artifact, "wb") as fh:
                fh.write(b"\x7fELF fake")
        os.makedirs("tmp_build", exist_ok=True)

    monkeypatch.setattr(compiler, "pyencrypt", fake_pyencrypt)


def test_project_flow_end_to_end(tmp_path, monkeypatch, capsys):
    make_project(tmp_path / "proj")
    monkeypatch.chdir(tmp_path)
    install_fake_platform_and_compiler(monkeypatch)

    rc = cli.main(["-d", "proj", "-i", "ignored/", "-r"])
    assert rc == 0

    result = tmp_path / "result" / "proj"
    # 编译产物去掉架构/cpython 段后落到 result
    assert (result / "main.so").read_bytes() == b"\x7fELF fake"
    assert (result / "pkg" / "mod.so").exists()
    # 非编译文件原样拷贝
    assert (result / "pkg" / "__init__.py").exists()
    assert (result / "data.txt").exists()
    assert (result / "ignored" / "ig.py").exists()
    # 已编译文件的源码不出现在 result
    assert not (result / "main.py").exists()
    assert not (result / "pkg" / "mod.py").exists()
    # -r 清除中间目录
    assert not (tmp_path / "build").exists()
    assert not (tmp_path / "tmp_build").exists()

    out = capsys.readouterr().out
    assert "Encrypt Finished" in out
    assert ".py'" not in out  # 无调试性文件清单打印


def test_project_flow_without_remove_keeps_build_dirs(tmp_path, monkeypatch):
    make_project(tmp_path / "proj")
    monkeypatch.chdir(tmp_path)
    install_fake_platform_and_compiler(monkeypatch)

    rc = cli.main(["-d", "proj"])
    assert rc == 0
    assert (tmp_path / "build").exists()
    assert (tmp_path / "result" / "proj" / "main.so").exists()


def test_bad_file_arg_exits_2(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(cli.platform, "system", lambda: "Linux")
    rc = cli.main(["-f", "readme.txt"])
    assert rc == 2
    assert "right name" in capsys.readouterr().out


def test_no_args_exits_2(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(cli.platform, "system", lambda: "Linux")
    rc = cli.main([])
    assert rc == 2
    assert "no -f or -d param" in capsys.readouterr().out
