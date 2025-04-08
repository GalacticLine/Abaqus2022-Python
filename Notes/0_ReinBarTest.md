# 3维-可变形 钢筋单侧受拉模拟 （含基础脚本编写）

运行 GUI 后，可以发现工作目录下会自动生成一个名为 abaqus.rpy 的文件，该文件记录用户在 GUI 界面中的各种操作，转换成对应的 Python 代码，运行此代码可以复现用户之前所做的每一步操作，因此尽管没有了解过或者系统学习过二次开发的相关内容，依旧可以通过在 GUI 中完成模拟过程，然后提取 abaqus.py 的核心操作代码，扩展或续写出需要的 ABAQUS 脚本程序。

接下来，本文将从钢筋的拉伸模拟来讨论 ABAQUS 二次开发的一般流程。

---

## 通用

### 1. 脚本运行方式

#### 无 GUI 运行

1. 使用 Python IDE 直接运行 .py 文件，比如 Pycharm 中通过点击运行的方式执行脚本。

2. 使用 Python IDE 间接运行 .py 文件，此方法通过一个 .py 文件执行另一个 .py 文件。
    ``` python
    from abaqus import *
    
    execfile('./xx.py')
    ```
   
3. 终端启动，输入以下命令，并将 "*" 替换为对于的脚本名称。
   ``` commandline
   abaqus cae noGUI=*.py
   ```
   
#### GUI 运行

1. 打开 ABAQUS CAE, 点击 文件 > 运行脚本 执行 .py 文件。
   <p align = "center">    
   <img  src="Img/0/abaqus运行脚本.jpg" width="200" />
   </p>
   
2. 也可以使用终端输入脚本名称：
   ``` commandline
   abaqus cae script=*.py
   ```
   
3. 使用 ABAQUS 2022 自带的 PDE 运行。（PDE 是内置的 Python IDE, 在没有其他 IDE 时，可以直接使用它编辑或运行脚本）
   
   > 注: 在使用 GUI 运行脚本时候，如果脚本使用了相对路径导入了其他模块，则需要确保 ABAQUS 工作目录与项目的根目录一致，才能找模块。否则，可能触发类似如下的导入错误：![](Img/0/abaqus导入错误.jpg)

4. 对于 GUI 运行的脚本，可以使用如下代码将自动生成的 abaqus.rpy 文件中，获取位置信息的方式将从掩码改为坐标，自动生成的代码可读性更强，方便后续脚本的编辑。
   
   ``` python
   session.journalOptions.setValues(replayGeometry=COORDINATE, recoverGeometry=COORDINATE)
   ```


### 2. 编码

对于一个 ABAQUS 2022 脚本文件，采用 Python2 的代码风格，故通常需在首行进行如下编码声明：
``` python
# -*- coding: mbcs -*-
```
    
然而对于一个代码中任意一行出来中文的 ABAQUS 脚本而言，使用 mbcs 编码，中文字符将会出现乱码的情况，为解决此问题，建议使用如下编码声明：
``` python
# coding=cp936
```

CP936 是一种 Windows 中常用的字符编码，它是 GBK 编码的别名，也就是简体中文编码。

---

## 前处理

### 1. 导入库

``` python
from abaqus import *
from abaqusConstants import *
from caeModules import *
```

abaqus 储存基本的 abaqus 对象， abaqusConstants 包括了基本的常量，这两个库是前处理脚本的核心，caeModules 包括了网格、集等的处理方法。

``` python
import math
```

导入内置库 math, 并非必须，在本案例中仅用于计算钢筋截面面积。

### 2. 创建模型

在导入上述库后，我们可以使用 mdb 对象 (ModelDataBase 模型数据库) 访问或者创建模型。默认情况下，一个新的 mdb 有一个默认的模型，可以通过如下方式访问，也可以直接索引它的名字 'Model-1'

``` python
model = mdb.models[mdb.models.keys()[0]]
# model = mdb.models['Model-1']
```

如果需要新的模型，调用 mdb 的 Model 方法进行创建。

``` python
model = mdb.Model(name="Model-New")
```
  
### 3. 创建部件
   
假设钢筋的长度为100mm，创建钢筋部件的代码如下：

``` python
# 钢筋长
length = 100
x = length / 2
   
# 创建临时草图'__profile__'，草图大小略大于钢筋长度
skh = model.ConstrainedSketch(name='__profile__', sheetSize=1.2 * length)
   
# 绘制，默认绘制中心点位于 (0, 0)
skh.Line(point1=(-x, 0.0), point2=(x, 0.0))
   
# 生成部件，三维，可变形实体，线部件
part = model.Part(name='ReinBar', dimensionality=THREE_D, type=DEFORMABLE_BODY)
part.BaseWire(sketch=skh)
   
# 删除临时草图
del model.sketches[skh.name]
```
使用脚本可以创建命名开头带有下划线 “_” 的对象，而在 GUI 中手动创建则不允许，这使得前后带有下划线的对象不会与用户自己创建的对象在命名上出现冲突。

上述的代码，将生成一个3维可变形线部件，部件中心在 0,0 点，在生成部件后建议删除临时的草图。

### 4. 材料属性与截面

定义材料属性，钢筋采用HRB400级钢筋，包括通用属性（密度），弹性属性（弹性模量和泊松比），塑性属性。

``` python
# 钢材名称
material_name = 'HRB400'
# 密度 tone/mm^3
rho = 7.85e-09
# 弹性模量 N/mm^2
e = 2e5
poisson = 0.3
# 屈服强度  N/mm^2
yie = 400.0
# 极限强度  N/mm^2
limit = 540

# 材料
hrb400 = model.Material(name=material_name)
hrb400.Density(table=((rho,),))
hrb400.Elastic(table=((e, poisson),))
hrb400.Plastic(scaleStress=None, table=((yie, 0.0), (limit, 0.1)))
```
ABAQUS 中，并没有明确限定单位制，但不同单位之间有固定的对应原则，比如当以 mm 创建部件后，其他的单位均要与 mm 相对应。
塑性属性采用钢筋双折线模型，模型曲线如下所示：
<p align = "center">    
<img  src="Img/0/BilinearSteelModel.png" width="300" />
</p>


创建桁架截面，根据钢筋直径计算截面面积。

``` python
# 钢筋直径
d = 8
area = (d / 2) ** 2 * math.pi 
# 创建桁架截面
section_name = 'TrD%d' % d + material_name
model.TrussSection(name=section_name, material=hrb400.name, area=area)
# 截面指派到钢筋部件
set_all = part.Set(edges=part.edges, name='All')
part.SectionAssignment(region=set_all, sectionName=section_name, offsetType=MIDDLE_SURFACE, )
```

region 需要提供一个 Set (集合), 如果不希望创建集合，则可以使用 regionToolset.Region

``` python
region = regionToolset.Region(edges=part.edges)
part.SectionAssignment(region=region, sectionName=section_name, offsetType=MIDDLE_SURFACE, )
```

### 5. 装配
为进行后续操作，在完成部件、材料、截面指派等布置后，可以开始装配部件，model.rootAssembly 管理和装配相关的操作，使用 Instance 函数创建一个独立的部件实例对象，可以调用创建实例对象进行 translate (平移)、rotateAboutAxis (旋转)，也可直接通过调用 model.rootAssembly 的函数进行平移、旋转，此外，后者还支持阵列。

``` python
assem = model.rootAssembly
instance = assem.Instance(name=part.name + '-1', part=part, dependent=ON)
```

### 6. 分析步

分析步这里设置 1 步，初始增量步0.01，时间长度为 2，最大增量步不大于时间长度。

``` python
step1 = model.StaticStep(name='Step-1', previous='Initial', initialInc=0.01, timePeriod=2, maxInc=2)
```

### 7. 边界条件和荷载

模拟的受力情况为：在右侧完全固定的前提下，左侧受到 30kN 拉力。

``` python
# 边界条件
set_right = part.Set(vertices=part.vertices.getByBoundingBox(xMax=-x), name='Right')
model.DisplacementBC(name='BC-1',
                     createStepName=step1.name,
                     region=instance.sets['Right'],
                     u1=SET, u2=SET, u3=SET, ur1=SET, ur2=SET, ur3=SET)
# 荷载
load_force = 30000.0
set_left = part.Set(vertices=part.vertices.getByBoundingBox(xMin=x), name='Left')
model.ConcentratedForce(name='Load-CF',
                        createStepName=step1.name,
                        region=instance.sets['Left'],
                        cf1=load_force)
```
由部件创建的集合不能直接传给边界条件和荷载的 region, 因为我们实际上是给实例施加的荷载和边界条件，所以在调用 part.Set 创建集合后，边界和荷载施加对象来自装配后的实例。

部件 part 的属性中，vertices (顶点)、 faces (面)、 edges (边)、 cells (单元) 等均有按尺寸、位置或者临界条件获取对象的方式，如上述代码中的 vertices.getByBoundingBox(xMax=-x)，将会将小于等于-x的点筛选出来，而符合条件的仅有-x位置的点，故通过这种方式可以获得最右侧顶点，同时，和 findAt 不同，这个函数可以返回对象是序列。


### 8. 输出

``` python
model.FieldOutputRequest(name='F-Output-1',
                         createStepName=step1.name, variables=('S', 'E'), timeInterval=0.05,
                         position=NODES)
```

即使没有创建场输出、历程输出的代码，也会有默认的场输出 F-Output-1 和历程输出 H-Output-1，在这里直接创建 F-Output-1 会将默认的场输出替换。

这里将场输出位置改成了结点，是为了方便在后处理中提取到结点数据。

### 9. 网格

``` python
# 网格大小
mesh_size = 8.0

# 网格
part.seedPart(size=mesh_size, deviationFactor=0.1, minSizeFactor=0.1)
t3d2 = mesh.ElemType(elemCode=T3D2, elemLibrary=STANDARD)
part.setElementType(regions=regionToolset.Region(edges=part.edges), elemTypes=(t3d2,))
part.generateMesh()
```
设置网格大小和网格属性，桁架截面采用 T3D2 单元，元素类型要与截面类型相适配，不适配将触发元素缺失截面错误。

> 13 elements have missing property definitions. The elements have been identified in element set ErrElemMissingSection.

### 10. 作业

创建作业并提交。

``` python
job = mdb.Job(name='Job-1', model=model)
job.submit(consistencyChecking=OFF)
```

![](Img/0/钢筋模型.jpg)
<p align="center">钢筋模型示意图</p>

### 总结

完整的前处理建模过程代码见 [before.py](../PyScripts/ReinBarTest/before.py)，加入了一个 [base.py](../PyScripts/base.py) 模块，它将追溯第一次调用它的脚本文件所在目录，创建存放 cae、odb 的文件夹 (Results) 和用于存放 csv、图像的子文件夹 Data、Img, 通过这种方式来统一各种前后处理文件的生成路径。
``` python
from base import *
```

---

## 后处理

### 1. 导入库

在考虑了一些可能出现的绘图问题，将数据提取和绘图的代码区分开，放在不同的 py 文件，由 [after.py](../PyScripts/ReinBarTest/after.py) 提取钢筋的应力应变数据，保存 .csv 文件到 base 模块指定的目录中。

``` python
# coding=cp936
import csv
import numpy as np
from odbAccess import openOdb
from base import data_path
```

为打开 ODB 文件需要从 odbAccess 中导入 openOdb 函数。

### 2. 提取数据

``` python
# 打开odb
odb = openOdb(path)
node = odb.rootAssembly.instances['REINBAR-1'].nodeSets['LEFT']

# 应力、应变
s_max = np.array([])
e_max = np.array([])

# 提取数据
for step in odb.steps.values():  # 遍历分析步
    for frame in step.frames:  # 遍历分析步的所有帧
        s_out = frame.fieldOutputs['S']  # 当前帧的应力场输出
        e_out = frame.fieldOutputs['E']  # 当前帧的应变场输出
        s_max = np.append(s_max, s_out.getSubset(region=node).values[0].maxPrincipal)
        e_max = np.append(e_max, e_out.getSubset(region=node).values[0].maxPrincipal)
```
打开 ODB 后，通过遍历分析步和帧，获取每一帧的场数据，从全部的场数据中筛选出指定的结点的最大主拉、压应力数据。注意的是，因为前处理中指定了场输出的是结点数据，所以在后处理中可以用 getSubset 获取到某实例结点集的数据，如果场输出的是积分点的数据，则使用 getSubset 虽然能找到该点，但数据为空集。

### 3. 总结

**完整的后处理建模过程代码见 [after.py](../PyScripts/ReinBarTest/after.py)**

---

## 绘图
运行 [plot.py](../PyScripts/ReinBarTest/plot.py)  , 该文件中使用 pandas 获取 csv 文件数据，并绘制的钢筋应力应变曲线，如下图所示：


<p align = "center">    
<img  src="../PyScripts/ReinBarTest/Result/Img/ReinBar 钢筋应力-应变曲线.png" width="600" />
</p>

可以看到图像呈现双折线的特点，应力在400MPa以下钢筋处于弹性阶段，应力达到屈服强度时，应变也接近0.002左右，之后钢筋屈服，曲线斜率明显发生变化，直到达到极限强度540MPa.