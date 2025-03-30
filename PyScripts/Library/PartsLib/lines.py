# coding=cp936
from abaqus import *
from abaqusConstants import *


class Lines:
    """
     3维-可变形 线部件静态方法类
    """

    @staticmethod
    def create_lines(model_name,
                     name='Lines',
                     length=1000.0,
                     num=4,
                     spacing=100.0,
                     section_name=''):
        """
        创建沿 x 轴线方向均布的多线部件。
        :param model_name: 模型名
        :param name: 名称
        :param length: 长
        :param num: 数量
        :param spacing: 间隔
        :param section_name: 截面名
        :return: 部件
        """
        model = mdb.models[model_name]

        # 检查
        if name in model.parts.keys():
            return model.parts[name]

        # 绘制
        x = length / 2
        y = (num - 1) * spacing / 2
        point1 = (-x, y)
        point2 = (x, y)
        sketch = model.ConstrainedSketch(name='__profile__', sheetSize=1.2 * length)
        line = sketch.Line(point1, point2)
        sketch.linearPattern(geomList=(line,), vertexList=(),
                             number1=1, spacing1=100.0, angle1=0.0,
                             number2=num, spacing2=spacing, angle2=270.0)

        # 创建
        part = model.Part(name=name, dimensionality=THREE_D, type=DEFORMABLE_BODY)
        part.BaseWire(sketch=sketch)
        del model.sketches[sketch.name]

        # 截面指派
        if section_name in model.sections.keys():
            region = part.Set(name='All', edges=part.edges)
            part.SectionAssignment(region=region, sectionName=section_name)

        print('Python: 创建部件 ' + name)
        return part

    @staticmethod
    def add_lines(model_name,
                  part=None,
                  length=1000.0,
                  width=100.0,
                  num_top=2,
                  offset=50.0):
        """
        在部件上按指定偏移添加一排均布的多线部件
        :param model_name: 模型名
        :param part: 部件
        :param length: 长
        :param width: 宽
        :param num_top: 数量
        :param offset: 偏移
        :return: 添加的多线部件
        """
        model = mdb.models[model_name]

        # 基准面
        plane = part.DatumPlaneByPrincipalPlane(principalPlane=XYPLANE, offset=offset)

        # 从基准面进入草图
        sketch_plane = part.datums[plane.id]
        sketch_edge = part.edges[0]
        transform = part.MakeSketchTransform(sketchPlane=sketch_plane,
                                             sketchUpEdge=sketch_edge,
                                             sketchPlaneSide=SIDE1,
                                             sketchOrientation=RIGHT,
                                             origin=(0.0, 0.0, offset))
        sketch = model.ConstrainedSketch(name='__profile__', sheetSize=2 * length, transform=transform)
        part.projectReferencesOntoSketch(sketch=sketch, filter=COPLANAR_EDGES)

        # 绘制
        spacing_top = width / (num_top - 1)
        x = length / 2
        y = (num_top - 1) * spacing_top / 2
        line = sketch.Line(point1=(y, -x), point2=(y, x))
        sketch.linearPattern(geomList=(line,), vertexList=(),
                             number1=num_top, spacing1=spacing_top, angle1=180.0,
                             number2=1, spacing2=100.0, angle2=90.0)

        # 创建
        wire = part.Wire(sketchPlane=sketch_plane, sketchUpEdge=sketch_edge, sketchPlaneSide=SIDE1,
                         sketchOrientation=RIGHT, sketch=sketch)

        del model.sketches[sketch.name]
        return wire

    @staticmethod
    def create_stirrups(model_name,
                        name='Stirrups',
                        length=1000.0,
                        width=100.0,
                        height=100.0,
                        spacing=100.0,
                        section_name=''):
        """
        创建均布的箍筋网部件
        :param model_name: 模型名
        :param name: 名称
        :param length: 长
        :param width: 宽
        :param height: 高
        :param spacing: 间距
        :param section_name: 截面名
        :return: 部件
        """
        model = mdb.models[model_name]

        # 检查
        if name in model.parts.keys():
            return model.parts[name]

        # 绘制
        x = width / 2
        y = height / 2
        sketch = model.ConstrainedSketch(name='__profile__', sheetSize=1.2 * max(width, height))
        sketch.rectangle(point1=(-x, -y), point2=(x, y))

        # 创建
        temp_name = '__' + name + '__'
        part = model.Part(name=temp_name, dimensionality=THREE_D, type=DEFORMABLE_BODY)
        part.BaseWire(sketch=sketch)
        del model.sketches[sketch.name]

        # 装配阵列
        x = length / 2 - length % spacing / 2
        # y = width / 2
        # z = height / 2
        num = int(length / spacing) + 1
        assembly = model.rootAssembly
        instance = assembly.Instance(name=temp_name + '-1', part=part, dependent=ON)
        instance.rotateAboutAxis(axisPoint=(0.0, 0.0, 0.0), axisDirection=(0.0, 10.0, 0.0), angle=90.0)
        instance.translate(vector=(x, 0.0, 0.0))
        instances = assembly.LinearInstancePattern(instanceList=(instance.name,),
                                                   direction1=(-1.0, 0.0, 0.0), direction2=(0.0, 1.0, 0.0),
                                                   number1=num, number2=1,
                                                   spacing1=spacing, spacing2=100.0)
        # 合并
        merge = assembly.InstanceFromBooleanMerge(name=name, instances=[instance] + list(instances),
                                                  originalInstances=DELETE, domain=GEOMETRY)
        part = model.parts[name]

        # 截面指派
        if section_name in model.sections.keys():
            region = part.Set(name='All', edges=part.edges)
            part.SectionAssignment(region=region, sectionName=section_name)

        del assembly.instances[merge.name]
        del model.parts[temp_name]

        print('Python: 创建部件 ' + name)
        return part

    @staticmethod
    def create_beam_mesh(model_name,
                         name='BeamMesh',
                         length=1000.0,
                         width=100.0,
                         height=100.0,
                         num_top=2,
                         num_bottom=5,
                         spacing_stirrup=100.0,
                         section_name_top='',
                         section_name_bottom='',
                         section_name_stirrup=''):
        """
        创建梁钢筋网部件
        :param model_name: 模型名
        :param name: 部件名
        :param length: 长
        :param width: 宽
        :param height: 高
        :param num_top: 上部纵筋数量
        :param num_bottom: 下部纵筋数量
        :param spacing_stirrup: 箍筋间距
        :param section_name_top: 上部纵筋截面名
        :param section_name_bottom: 下部纵筋截面名
        :param section_name_stirrup: 箍筋截面名
        :return: 部件
        """
        model = mdb.models[model_name]

        # 检查
        if name in model.parts.keys():
            return model.parts[name]

        # 创建底部纵筋
        name0 = '__' + name + '_Long__'
        part0 = Lines.create_lines(model_name, name0, length, num_bottom, spacing=width / (num_bottom - 1))
        region0 = part0.Set(name='BottomRein', edges=part0.edges)

        # 添加上部钢筋
        wire = Lines.add_lines(model_name, part0, length, width, num_top, offset=height)
        region01 = part0.Set(name='TopRein', edges=part0.getFeatureEdges(wire.name))

        # 创建箍筋
        name1 = '__' + name + '_Stirrups__'
        part1 = Lines.create_stirrups(model_name, name1, length, height, width, spacing_stirrup)
        region1 = part1.Set(edges=part1.edges, name='Stirrups')

        # 装配
        assembly = model.rootAssembly
        instance0 = assembly.Instance(name=name0 + '-1', part=part0, dependent=ON)
        instance1 = assembly.Instance(name=name1 + '-1', part=part1, dependent=ON)
        instance1.translate(vector=(0.0, 0.0, height / 2))

        # 截面指派
        sections = model.sections.keys()
        if section_name_bottom in sections:
            part0.SectionAssignment(region0, section_name_bottom)
        if section_name_top in sections:
            part0.SectionAssignment(region01, section_name_top)
        if section_name_stirrup in sections:
            part1.SectionAssignment(region1, section_name_stirrup)

        # 合并
        merge = assembly.InstanceFromBooleanMerge(name=name,
                                                  instances=(instance0, instance1,),
                                                  originalInstances=DELETE,
                                                  domain=GEOMETRY)
        part = model.parts[name]
        part.Set(name='All', edges=part.edges)

        del assembly.instances[merge.name]
        del model.parts[name0]
        del model.parts[name1]

        print('Python: 创建部件 ' + name)
        return part
