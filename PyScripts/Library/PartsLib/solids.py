# coding=cp936
from abaqus import *
from abaqusConstants import *


class Cube:
    def __init__(self,
                 model_name,
                 name='Cube',
                 length=100.0,
                 width=100.0,
                 height=100.0,
                 section_name='',
                 need_surf_top=False,
                 need_surf_bottom=False,
                 need_repoint=False):
        """
        3维-可变形 矩形实体部件
        :param model_name: 模型

        :param name: 部件名
        :param length: 长
        :param width: 宽
        :param height: 高
        :param section_name: 截面名
        :param need_surf_top: 是否设置顶面 "Top"
        :param need_surf_bottom: 是否设置底面 "Bottom"
        :param need_repoint: 是否在底面设置参考点
        """

        def create():
            # 检查
            model = mdb.models[model_name]
            if name in model.parts.keys():
                return model.parts[name]

            # 绘制
            x = length / 2
            y = width / 2
            sketch = model.ConstrainedSketch(name='__profile__', sheetSize=1.2 * max(length, width))
            sketch.rectangle(point1=(-x, -y), point2=(x, y))

            # 创建
            part = model.Part(name, dimensionality=THREE_D, type=DEFORMABLE_BODY)
            part.BaseSolidExtrude(sketch=sketch, depth=height)
            del model.sketches[sketch.name]

            # 截面指派
            if section_name in model.sections.keys():
                region = part.Set(name='All', cells=part.cells)
                part.SectionAssignment(region=region, sectionName=section_name)
                self.set_all = region

            # 创建表面
            if need_surf_top:
                self.surf_top = part.Surface(name='Top', side1Faces=part.faces.getByBoundingBox(zMin=height))

            if need_surf_bottom:
                self.surf_bottom = part.Surface(name='Bottom', side1Faces=part.faces.getByBoundingBox(zMax=0))

            if need_repoint:
                self.rp0 = part.ReferencePoint(point=(0.0, 0.0, 0.0))

            print('Python: 创建部件 ' + name)
            return part

        self.part = create()


class SimplyBeam(Cube):
    def __init__(self,
                 model_name,
                 name='Beam',
                 length=2000.0,
                 width=200.0,
                 height=300.0,
                 section_name='',
                 need_surf_top=False,
                 need_surf_bottom=False,
                 need_repoint=False,
                 pad_width=0.0,
                 load_mode=0):
        """
        3维-可变形 简支梁实体部件
        :param name: 名称
        :param length: 长
        :param width: 宽
        :param height: 高
        :param section_name: 截面名
        :param need_surf_top: 是否设置顶面 "Top"
        :param need_surf_bottom: 是否设置底面 "Bottom"
        :param need_repoint: 是否在底面设置参考点
        :param pad_width: 垫块宽度，默认 0.0 不设置垫块，当设置垫块后，创建表面 "ToPads"
        :param load_mode: 按加载模式分割模型，并创建加载相关表面 "ToLoad"，( 0 均布加载，1 单点跨中加载，2 三分点加载 )
        """

        def create():
            # 检查
            model = mdb.models[model_name]
            if name in model.parts.keys():
                return model.parts[name]

            Cube.__init__(self, model_name, name, length, width, height, section_name, need_surf_top, need_surf_bottom,
                          need_repoint)
            part = self.part

            y = width / 2

            # 跨中分割
            dp0 = part.DatumPointByCoordinate(coords=(0, y, height))
            part.PartitionCellByPlanePointNormal(point=part.datums[dp0.id],
                                                 normal=part.edges.findAt((1e-2, y, 0)),
                                                 cells=part.cells)
            # 跨中点
            part.PartitionEdgeByParam(edges=part.edges.findAt((0, 1e-2, 0)), parameter=0.5)
            self.mid_point = part.Set(vertices=
                                      part.vertices.getByBoundingBox(xMin=0, yMin=0, zMin=0, zMax=0, xMax=0, yMax=0),
                                      name='MidPoint')

            # 支座分割
            if pad_width != 0:
                x = length / 2 - pad_width
                dp0 = part.DatumPointByCoordinate(coords=(x, y, height))
                dp1 = part.DatumPointByCoordinate(coords=(-x, y, height))

                part.PartitionCellByPlanePointNormal(point=part.datums[dp0.id],
                                                     normal=part.edges.findAt((1e-2, y, 0)),
                                                     cells=part.cells)
                part.PartitionCellByPlanePointNormal(point=part.datums[dp1.id],
                                                     normal=part.edges.findAt((1e-2, y, 0)),
                                                     cells=part.cells)

                part.Surface(side1Faces=
                             part.faces.getByBoundingBox(xMin=x, zMax=0) +
                             part.faces.getByBoundingBox(xMax=-x, zMax=0), name='ToPads')

            # 均布加载
            surf_load_name = 'ToLoad'
            if load_mode == 0:
                part.Surface(side1Faces=part.faces.getByBoundingBox(zMin=height), name=surf_load_name)

            # 跨中单点加载
            if load_mode == 1:
                x = pad_width / 2

                dp0 = part.DatumPointByCoordinate(coords=(x, y, height))
                dp1 = part.DatumPointByCoordinate(coords=(-x, y, height))

                part.PartitionCellByPlanePointNormal(point=part.datums[dp0.id],
                                                     normal=part.edges.findAt((1e-2, y, 0)),
                                                     cells=part.cells)
                part.PartitionCellByPlanePointNormal(point=part.datums[dp1.id],
                                                     normal=part.edges.findAt((1e-2, y, 0)),
                                                     cells=part.cells)
                part.Surface(side1Faces=
                             part.faces.getByBoundingBox(xMax=x, xMin=-x, zMin=height),
                             name=surf_load_name)

            # 三分点加载
            if load_mode == 2:
                x0 = length / 6 + pad_width / 2
                x1 = length / 6 - pad_width / 2

                dp0 = part.DatumPointByCoordinate(coords=(x0, y, height))
                dp1 = part.DatumPointByCoordinate(coords=(x1, y, height))
                dp2 = part.DatumPointByCoordinate(coords=(-x1, y, height))
                dp3 = part.DatumPointByCoordinate(coords=(-x0, y, height))

                part.PartitionCellByPlanePointNormal(point=part.datums[dp0.id],
                                                     normal=part.edges.findAt((1e-2, y, 0)),
                                                     cells=part.cells)
                part.PartitionCellByPlanePointNormal(point=part.datums[dp1.id],
                                                     normal=part.edges.findAt((1e-2, y, 0)),
                                                     cells=part.cells)
                part.PartitionCellByPlanePointNormal(point=part.datums[dp2.id],
                                                     normal=part.edges.findAt((1e-2, y, 0)),
                                                     cells=part.cells)
                part.PartitionCellByPlanePointNormal(point=part.datums[dp3.id],
                                                     normal=part.edges.findAt((1e-2, y, 0)),
                                                     cells=part.cells)

                part.Surface(side1Faces=
                             part.faces.getByBoundingBox(xMax=x0, xMin=x1, zMin=height) +
                             part.faces.getByBoundingBox(xMax=-x1, xMin=-x0, zMin=height),
                             name=surf_load_name)
            return part

        self.part = create()
