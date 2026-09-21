# -*- coding: utf-8 -*-
"""编译执行模块的单元测试：mock 掉 setuptools/Cython，验证扩展构建与安静输出。"""
import os

from py2so import compiler


def make_fakes(monkeypatch, captured):
    def fake_cythonize(exts, **kwargs):
        captured["exts"] = exts
        captured["cython_kwargs"] = kwargs
        captured["docstrings_at_call"] = compiler.CythonOptions.docstrings
        return exts

    def fake_setup(**kwargs):
        captured["setup_kwargs"] = kwargs

    monkeypatch.setattr(compiler, "cythonize", fake_cythonize)
    monkeypatch.setattr(compiler, "setup", fake_setup)


def test_pyencrypt_builds_extensions_and_stays_quiet(monkeypatch, capsys):
    captured = {}
    make_fakes(monkeypatch, captured)

    compiler.pyencrypt([os.path.join("proj", "pkg", "mod.py"),
                        os.path.join("proj", "main.py")])

    names = [ext.name for ext in captured["setup_kwargs"]["ext_modules"]]
    assert names == ["proj.pkg.mod", "proj.main"]
    assert captured["setup_kwargs"]["script_args"] == ["build_ext"]
    assert captured["cython_kwargs"]["language_level"] == 3
    assert captured["cython_kwargs"]["build_dir"] == "tmp_build"
    # 验收4: 运行期不再打印待编译文件清单等调试信息
    assert capsys.readouterr().out == ""


def test_pyencrypt_applies_hardening(monkeypatch):
    """硬化：strip/-O3 -g0、binding=False、编译期 docstrings 全局为 False"""
    captured = {}
    make_fakes(monkeypatch, captured)
    # 注册原值以便测试后恢复；pyencrypt 会无条件覆写该全局
    monkeypatch.setattr(compiler.CythonOptions, "docstrings", True, raising=False)

    compiler.pyencrypt([os.path.join("proj", "main.py")])

    ext = captured["setup_kwargs"]["ext_modules"][0]
    assert ext.extra_compile_args == ["-O3", "-g0"]
    assert ext.extra_link_args == ["-s"]
    assert captured["cython_kwargs"]["compiler_directives"] == {"binding": False}
    assert captured["docstrings_at_call"] is False
