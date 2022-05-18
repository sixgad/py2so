# py2so
linux下将python代码编译为so文件，实现了“加密”保护源代码的需求，同时带来了性能提升。

**安装**

> git clone git@github.com:sixgad/py2so.git
>
> pip install -r requirements.txt

**查看帮助**

> python py2so.py -h

```shell
py2so use help

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  Python文件 (如果使用-f, 将编译单个Python文件)
  -d DIRECTORY, --directory DIRECTORY  Python项目路径 (如果使用-d参数, 将编译整个Python项目)
  -i IGNORE, --ignore IGNORE  标记你不想编译的文件或文件夹路径 注意: 文件夹需要以路径分隔符号（\`/\`或\`\\\`，依据系统而定）结尾，并且需要和-d参数一起使用 例: -i main.py,mod/__init__.py,exclude_dir/
  -r, --remove          清除所有中间文件，只保留加密结果文件，默认False
```

**举例**

编译单个文件，结果默认生成在result文件夹

> python py2so.py -f example/proj2/tool.py -r

编译整个python项目，忽略主文件run.py

> python py2so.py -d example/proj1/ -i run.py -r



具体应用，见博客：https://paker.net.cn/article?id=34
