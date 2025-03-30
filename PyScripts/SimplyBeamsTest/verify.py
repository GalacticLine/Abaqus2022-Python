import math

# 参数
l = 5000
b = 300
h = 500
fc = 20.1
ft = 2.01
Es = 2e5
Ec = 3e4
d0 = 12
d1 = 18
a_s = 25
fy = 400
alpha_1 = 1

# 计算

# 有效高度
h0 = h - (a_s + d1 / 2)

# 等效弹性模量
alpha_E = Es / Ec

# 钢筋截面面积
As = 3 * (d1 / 2) ** 2 * math.pi + 2 * (d0 / 2) ** 2 * math.pi

# 受压区高度
x = fy * As / (alpha_1 * fc * b)

# 开裂弯矩
xcr = (1 + 2 * alpha_E * As / (b * h)) / (1 + alpha_E * As / (b * h)) * h / 2
Mcr = ft * b * (h - xcr) * ((h - xcr) / 2 + 2 * xcr / 3) + 2 * alpha_E * ft * As * (h0 - 2 * xcr / 3)

# 配筋率检查
rho = As / (b * h0) * 100
xi_b = 0.518
if rho < max(0.002, 0.45 * ft / fy):
    print('少筋梁')
    Mu = Mcr
elif x > xi_b * h0:
    Mu = alpha_1 * fc * b * h0 ** 2 * xi_b * (1 - 0.5 * xi_b)
    print('超筋梁')
else:
    Mu = fy * As * (h0 - x / 2)
    print('适筋梁')

# 不同加载方式下的荷载计算
print("\n跨中单点加载:")
p_cr0 = 4 * Mcr / l / 1e3
p_u0 = 4 * Mu / l / 1e3
print(f"开裂荷载: ", p_cr0)
print(f"极限荷载: ", p_u0)

print("\n均布加载:")
p_cr1 = 2 * p_cr0
p_u1 = 2 * p_u0
print(f"开裂荷载: ", p_cr1)
print(f"极限荷载: ", p_u1)

print("\n三分点加载:")
p_cr2 = 3 / 2 * p_cr0
p_u2 = 3 / 2 * p_u0
print(f"开裂荷载: ", p_cr2)
print(f"极限荷载: ", p_u2)
