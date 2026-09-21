# AGENTS

## 概述

- py2so：在 Linux 下用 Cython 将 Python 代码编译为 `.so` 以保护源码，同时带来性能提升；结果输出到 `result/` 目录形成可直接部署的工程。
- 能力：单文件编译（`-f`）、整项目编译（`-d`）、按文件或目录排除（`-i`）、清理中间产物（`-r`）；0.3.0 起默认对产物做逆向硬化。
- 当前状态：0.3.0，21 项 pytest 全绿；wheel 可构建可安装；真实编译产物仅在 Linux 验证（本机开发环境为 Windows）。

## 技术栈

- Python `>=3.10`：`pyproject.toml` requires-python。
- Cython：运行时依赖（工具在运行期调用 `cythonize`，见 `src/py2so/compiler.py`）。
- setuptools：`build_ext` 调用链（禁止回 distutils，Python 3.12+ 已移除）。
- hatchling 构建后端、uv 依赖与环境管理（`pyproject.toml`、`uv.lock`）。
- pytest 测试框架（`pyproject.toml` dev 依赖组，`tests/`）。
- 具体依赖版本以 `uv.lock` 为准。

## 目录结构

- `src/py2so/`：主包（src 布局，console script 入口 `py2so`）。
  - `cli.py`：参数解析、平台保护、错误到退出码的映射。
  - `collect.py`：待编译 py 文件收集与 ignore 过滤，定义 `Py2soError`。
  - `compiler.py`：构建 Cython 扩展并编译，产物硬化参数在此。
  - `output.py`：中间目录清理与 `result/` 产物装配。
- `tests/`：行为测试；文件收集、编译参数、CLI 端到端三个接缝。
- `example/proj1/`：多模块项目示例；`example/proj2/`：单文件示例。

## 编码规范

- UTF-8 文件声明头 + 中文注释，遵循现有文件风格。
- 用户可定位的输入/环境错误统一抛 `collect.Py2soError`，由 `cli.main` 打印并返回退出码 2。
- 路径相等比较经 `os.path.normpath` + `normcase` 归一（`collect._normalize_rel`），容忍分隔符混杂。
- 测试只 mock 外部效应接缝（`setuptools.setup`、`Cython.Build.cythonize`、`platform.system`），不断言私有实现。

## 常用命令

- `uv sync`：安装依赖与包本身。
- `uv run pytest`：运行全部测试（Windows 本机可跑，编译被 mock）。
- `uv run py2so -h`：查看 CLI 帮助（任何平台可用）。
- `uv build`：构建 wheel/sdist 到 `dist/`。
- `uv lock`：依赖或项目版本号变化后刷新锁定。
- Linux 上冒烟：`pip install dist/py2so-0.3.0-py3-none-any.whl && py2so -d example/proj1/ -i run.py -r`，产物自查 `file result/…/*.so`（期望 stripped）。

## 禁止事项

- 不得引入 `distutils`：构建调用只走 setuptools。
- 不得解除 Windows 平台保护放开真实编译：仅支持 Linux 是有意设计（`cli.py`）。
- 不得随意更改 `-f/-d/-i/-r` 参数契约与 `result/` 产物布局：已有测试锁定两者。
- 不得为了方便调试回退产物硬化参数（strip / binding=False / docstring 剥离）：这是 0.3.0 的产品承诺。
- 测试不得依赖真实编译器、C 工具链或 Linux 环境。
- 不得提交 `nb/`（代理工作产物，已被忽略）、`dist/`、`.venv`。
- 本机无法验证的结论（Linux 编译行为）必须标注未验证，不得写成已证明。

## 项目陷阱

- Cython 3 的 docstring 剥离开关是模块全局 `Cython.Compiler.Options.docstrings`，不在 `compiler_directives` 表内；证据：`src/py2so/compiler.py` 的 `pyencrypt`。
- `os.path.join` 会被绝对的后续段整体重置，`gen_project` 对绝对路径项目采用"根/盘符转点目录段"的镜像规则规避自拷贝崩溃；证据：`src/py2so/output.py` 注释与 `tests/test_cli_e2e.py::test_absolute_directory_end_to_end`。
- ignore 条目比对必须走路径归一，否则 Windows 分隔符混杂时目录排除静默失效；证据：`collect._normalize_rel` 与 `tests/test_collect.py`。
- 平台保护在参数解析之后执行，以保证 `-h` 全平台可用——不要前移；证据：`src/py2so/cli.py` 的 `main` 顺序。
- `-i` 的根自指条目（`/`、`./` 等）会被守卫拒绝而非静默清空编译集；证据：`collect.collect_compile_files` 的 raise 与 `test_ignore_root_self_reference_raises`。
