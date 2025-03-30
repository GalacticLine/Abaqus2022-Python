import pandas as pd
from matplotlib import pyplot as plt
from base import img_path, data_path

# 读取数据
csv_name = 'ReinBar_SMAX_EMAX.csv'
csv_path = data_path + '/' + csv_name
df = pd.read_csv(csv_path)

# 绘图风格
custom_style = {
    'figure.figsize': (8, 7),
    'font.sans-serif': ['Times New Roman + SimSun + WFM Sans Compressed'],  # 中英混排字体
    'mathtext.fontset': 'stix',

    'axes.unicode_minus': False,
    'axes.titlesize': 20,
    'axes.labelsize': 16,
    'axes.labelpad': 12,
    'axes.titlepad': 14,

    'lines.linewidth': 1,
    'lines.markersize': 6,
    'grid.linestyle': '--',
    'grid.linewidth': 0.5,

    'legend.fontsize': 18,

    'xtick.labelsize': 14,
    'ytick.labelsize': 14,
    'xtick.direction': 'in',
    'ytick.direction': 'in',

    'axes.linewidth': 2.0,
}
plt.style.use(custom_style)

# 绘制
title_name = 'ReinBar 钢筋应力-应变曲线'

plt.figure()
plt.minorticks_on()

plt.plot(df['EMAX'], df['SMAX'], 'o--', c='b', markerfacecolor='w', label='Left')

plt.xlim(left=0)
plt.ylim(bottom=0)
plt.title(title_name)
plt.ylabel('应力σ (MPa)')
plt.xlabel('应变ε')
plt.legend()
plt.grid()
plt.tick_params(axis='both', which='major', length=5, width=2)
plt.tick_params(axis='both', which='minor', length=3, width=1)
plt.savefig(img_path + '/' + title_name + '.png')
plt.show()
