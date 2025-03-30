# coding=cp936
"""
ABAQUS 计算混凝土 (CDP) 塑性损伤本构

* 根据《混凝土结构设计规范》GB50010-2010 (2024年版)
* 适用混凝土强度等级范围 C20~C80
"""
import numpy as np
from abaqus import *


def cal_ec(fcu_k):
    """
    计算弹性模量
    :param fcu_k: 立方体抗压强度标准值。
    :return: 弹性模量
    """
    ec = 10 ** 5 / (2.2 + 34.7 / fcu_k)
    ec = round(ec, 3)
    return ec


def convert_fcu_k(fcu_k=30, delta_c=None):
    """
    fcu,k 换算成 fck, ftk

    :param fcu_k: 立方体抗压强度标准值（强度等级代表值） (N/mm^2)。
    :param delta_c:  变异系数 δc, 如果为 None, 则按规范公式计算。
    """

    # 按线性插值计算 α1, α2
    if fcu_k <= 50:
        alpha1 = 0.76
    else:
        alpha1 = np.interp(fcu_k, [50, 80], [0.76, 0.82])

    if fcu_k <= 40:
        alpha2 = 1
    else:
        alpha2 = np.interp(fcu_k, [40, 80], [1, 0.87])

    # 计算变异系数
    if delta_c is None:
        if fcu_k <= 20:
            delta_c = 0.18
        elif fcu_k <= 25:
            delta_c = 0.16
        elif fcu_k <= 30:
            delta_c = 0.14
        elif fcu_k <= 35:
            delta_c = 0.13
        elif fcu_k <= 45:
            delta_c = 0.12
        elif fcu_k <= 55:
            delta_c = 0.11
        else:
            delta_c = 0.10

    # 换算
    fck = 0.88 * alpha1 * alpha2 * fcu_k
    ftk = 0.88 * 0.395 * fcu_k ** 0.55 * (1 - 1.645 * delta_c) ** 0.45 * alpha2

    return fck, ftk


class Concrete:
    def __init__(self,
                 name='C30',
                 fcr=20.1,
                 ftr=2.01,
                 er=30000,
                 density=2.4e-09,
                 poisson=0.2,
                 cdp_plasticity=(30.0, 0.1, 1.16, 0.6667, 0.005)):
        """
        混凝土类
        :param name: 名称
        :param fcr: 单轴抗压强度代表值，可取 fc、fck、fcm (N/mm^2)
        :param ftr: 单轴抗拉强度代表值，可取 ft、ftk、ftm (N/mm^2)
        :param er:  Ec 弹性模量 (N/mm^2)
        :param poisson: 泊松比，可取 0.2
        :param density: ρ 密度，一般 2.2e-09~2.4e-09 (tone/mm^3)
        :param cdp_plasticity: CDP 塑性参数
        """

        self.name = name
        self.fcr = fcr
        self.ftr = ftr
        self.er = er
        self.density = density
        self.poisson = poisson
        self.cdp_plasticity = cdp_plasticity

    def compress(self):
        """
        计算混凝土塑性损伤模型受压部分
        """
        x = np.concatenate([
            np.arange(0.3, 1, 0.1),
            np.arange(1, 4, 0.2),
            np.arange(4, 14, 0.5),
            np.arange(14, 50, 5)
        ])

        fcr = self.fcr
        er = self.er

        x0 = x[x <= 1]
        x1 = x[x > 1]

        # 峰值压应变
        strain_peek = (700 + 172 * np.sqrt(fcr)) * 1e-6

        # 受压应力应变曲线下降段参数
        alpha = 0.157 * fcr ** 0.785 - 0.905

        # 受压应力非线性参数
        n = er * strain_peek / (er * strain_peek - fcr)

        # 受压计算参数
        rho = fcr / (er * strain_peek)

        # 受压损伤演化参数
        dc_arg = np.append(
            1 - rho * n / (n - 1 + x0 ** n),
            1 - rho / (alpha * (x1 - 1) ** 2 + x1)
        )

        # 名义应力、应变
        strain_nominal = x * strain_peek
        stress_nominal = (1 - dc_arg) * er * strain_nominal

        # 受压损伤因子
        d = 1 - np.sqrt(stress_nominal / (er * strain_nominal))

        # 真实应力、应变
        stress_true = stress_nominal * (1 + strain_nominal)
        strain_true = np.log(1 + strain_nominal)

        # 非弹性应变
        strain_in = strain_true - (stress_true / er)

        return d, stress_true, strain_in

    def tensile(self):
        """
        计算混凝土塑性损伤模型受拉部分
        """
        x = np.concatenate([
            np.arange(1, 4, 0.2),
            np.arange(4, 14, 0.5),
            np.arange(14, 50, 5)
        ])

        ftr = self.ftr
        er = self.er
        x0 = x[x <= 1]
        x1 = x[x > 1]

        # 峰值拉应变
        strain_peek = 65 * ftr ** 0.54 * 1e-6

        # 受拉应力应变曲线下降段参数
        alpha = 0.312 * ftr ** 2

        # 受拉计算参数
        rho = ftr / (er * strain_peek)

        # 受拉损伤演化参数
        dt_arg = np.append(
            1 - rho * (1.2 - 0.2 * x0 ** 5),
            1 - rho / (alpha * (x1 - 1) ** 1.7 + x1)
        )

        # 名义应力、应变
        strain_nominal = x * strain_peek
        stress_nominal = (1 - dt_arg) * er * strain_nominal

        # 受拉损伤因子
        d = 1 - np.sqrt(stress_nominal / (er * strain_nominal))

        # 真实应力、应变
        stress_true = stress_nominal * (1 + strain_nominal)
        strain_true = np.log(1 + strain_nominal)

        # 塑性应变
        strain_in = strain_true - (stress_true / er)

        return d, stress_true, strain_in


class ConcreteAb(Concrete):
    def __init__(self,
                 model_name,
                 name='C30',
                 fcr=20.1,
                 ftr=2.01,
                 er=30000,
                 density=2.4e-09,
                 poisson=0.2,
                 cdp_plasticity=(30.0, 0.1, 1.16, 0.6667, 0.005)):
        """
        ABAQUS 混凝土类
        :param model_name: 模型名
        :param name: 名称
        :param fcr: 单轴抗压强度代表值，可取 fc、fck、fcm (N/mm^2)
        :param ftr: 单轴抗拉强度代表值，可取 ft、ftk、ftm (N/mm^2)
        :param er:  Ec 弹性模量 (N/mm^2)
        :param poisson: 泊松比，可取 0.2
        :param density: ρ 密度，一般 2.2e-09~2.4e-09 (tone/mm^3)
        :param cdp_plasticity: CDP 塑性参数
        """
        Concrete.__init__(self, name, fcr, ftr, er, density, poisson, cdp_plasticity)
        self.model = mdb.models[model_name]

    def create(self):
        """
        创建混凝土材料，将计算CDP塑性损伤，并将混凝土基本弹塑性参数导入 Abaqus
        :return:
        """
        name = self.name
        er = self.er
        model = self.model

        # 检查
        if name in model.materials.keys():
            return model.materials[name]

        # 计算
        dc_in, stress_c_in, strain_c_in = self.compress()
        dt_in, stress_t_in, strain_t_in = self.tensile()

        # 调整
        dt_in = np.round(dt_in, 5)
        dc_in = np.round(dc_in, 5)
        stress_t_in = np.round(stress_t_in, 6)
        stress_c_in = np.round(stress_c_in, 6)
        strain_t_in = np.round(strain_t_in, 6)
        strain_c_in = np.round(strain_c_in, 6)
        dc_in[0] = 0
        dt_in[0] = 0
        strain_t_in[0] = 0
        strain_c_in[0] = 0

        # 导入
        material = model.Material(name=name)
        material.Density(table=((self.density,),))
        material.Elastic(table=((er, self.poisson),))
        cdp = material.ConcreteDamagedPlasticity(table=(self.cdp_plasticity,))
        cdp.ConcreteCompressionHardening(table=np.column_stack([stress_c_in, strain_c_in]))
        cdp.ConcreteTensionStiffening(table=np.column_stack([stress_t_in, strain_t_in]))
        cdp.ConcreteCompressionDamage(table=np.column_stack([dc_in, strain_c_in]))
        cdp.ConcreteTensionDamage(table=np.column_stack([dt_in, strain_t_in]))

        print('Python: 创建材料 ' + name)
        return material
