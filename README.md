# Abaqus2022 Python 二次开发学习笔记

[English](./README_EN.md) | [中文](./README.md)

### 前言

笔记主要记录我在 Abaqus 中使用 Python 进行二次开发的学习历程，包括基础操作、脚本编写技巧以及实际应用中的问题与解决方案的总结。

需要说明的是，由于个人经验有限，部分内容可能存在不足或疏漏，还请读者结合官方文档和其他专业资料进行参考。
通过这些记录，希望能够帮助到同样在学习 Abaqus Python 二次开发的同行，也欢迎拉取进行修改和补充。


### Abaqus 介绍

功能强大有限元分析软件，以非线性求解能力、大规模计算性能和复杂工程问题的处理能力闻名于世，广泛应用于机械、土木、航空航天、汽车等工程领域。

可进行多物理场耦合分析，包括：
- 结构分析：静态/动态分析、接触碰撞、断裂疲劳等
- 多场耦合分析：流固耦合、热力耦合、压电分析等
- 系统级仿真：复杂问题和大规模模拟

二次开发方面：
- 提供 Fortran 用户子程序（UMAT/UEL等）
- 提供 Python 脚本接口

### 代码运行说明

本项目中：
- ABAQUS 版本： Abaqus 2022 6.22-1
- ABAQUS(2022) Python 解释器：Python 2.7.15
- Python 二次开发环境：Python 3.12


兼容性说明：Abaqus(2022) 在运行脚本时，使用内置的 SMAPython.exe ，该解释器只支持 python2 语法的脚本，如果不考虑解决脚本运行环境和二次开发环境之间的冲突，则需要采用兼容 Python2 的语法编写脚本。

### 目录结构

```plaintext
├── 项目根目录
│   ├── Notes/  # 相关的笔记
│   ├── PyScripts/  # 脚本集合
│   │   ├── Library/  # 通用库，包括一些材料、部件的实现
│   │   ├── ReinBarTest/  # xxTest 为xx模型的前后处理
│   │   ├── SimplyBeamsTest/
│   │   └── ...
│   └── README.md
```

### 所使用的第三方库
1. [abqpy](https://github.com/haiiliin/abqpy)

    为方便用 Python 编写脚本，包括一般函数、对象的调用可以获得明确的提示，abaqus 二次开发中可以安装这个库，该库要求 Python 版本大于 3.8 同时 Abaqus 版本大于 2016.
    
    可以使用如下命令安装:
    
    > pip install -U abqpy==2022.*

    将 " * " 替换为你安装的abaqus内部版本

2. [numpy](https://github.com/numpy/numpy)

   非常强大的科学运算库，用于处理多维数组和矩阵。
3. [matplotlib](https://github.com/matplotlib/matplotlib)

   科学绘图库，提供 MATLAB 风格的交互和面向对象的灵活绘图接口。
4. [pandas](https://github.com/pandas-dev/pandas)

   python 数据分析库，可以读取处理 csv、excel 数据。   

### 示例
1. [3维-可变形 钢筋单侧受拉模拟](./Notes/0_ReinBarTest.md)
2. [3维-可变形 钢筋混凝土简支梁模拟三种加载方式模拟](./Notes/1_SimplyBeamsTest.md)
