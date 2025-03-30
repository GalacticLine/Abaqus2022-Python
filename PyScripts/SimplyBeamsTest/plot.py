import pandas as pd
from matplotlib import pyplot as plt
from base import img_path, data_path

custom_style = {
    'figure.figsize': (8, 6),
    'font.sans-serif': ['Times New Roman + SimSun + WFM Sans Compressed'],
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

csv_path0 = data_path + '/' + 'SimplyBeam0_URF.csv'
csv_path1 = data_path + '/' + 'SimplyBeam1_URF.csv'
csv_path2 = data_path + '/' + 'SimplyBeam2_URF.csv'
df0 = pd.read_csv(csv_path0)
df0 = df0[df0['U'] < 110][::3]
df1 = pd.read_csv(csv_path1)
df1 = df1[df1['U'] < 110][::3]
df2 = pd.read_csv(csv_path2)[::3]
df2 = df2[df2['U'] < 110][::3]
plt.figure()
plt.minorticks_on()

plt.plot(df0['U'], df0['RF'] / 1000, '^--', c='b', markerfacecolor='w', label='均布加载')
plt.plot(df1['U'], df1['RF'] / 1000, 'o--', c='y', markerfacecolor='w', label='单点加载')
plt.plot(df2['U'], df2['RF'] / 1000, '*--', c='g', markerfacecolor='w', label='三分点加载')
plt.xlim(left=0)
plt.ylim(bottom=0)

plt.legend()
title_name = '简支梁三种加载方式跨中荷载-位移曲线'
plt.title(title_name)
plt.xlabel('位移 (mm)')
plt.ylabel('荷载 (kN)')

# 刻度线
plt.tick_params(axis='both', which='major', length=5, width=2)
plt.tick_params(axis='both', which='minor', length=3, width=1)
plt.savefig(img_path + '/' + title_name + '.png')

plt.show()
