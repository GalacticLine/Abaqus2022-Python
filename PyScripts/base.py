# coding=cp936
import os
import inspect

# 获取最外层调用者的文件路径
frame = inspect.currentframe()
while frame.f_back is not None:
    frame = frame.f_back
call_path = os.path.dirname(os.path.abspath(frame.f_code.co_filename))
del frame

# 设置路径
work_path = os.path.join(call_path, 'Result')
data_path = os.path.join(work_path, 'Data')
img_path = os.path.join(work_path, 'Img')

# 创建目录
if not os.path.exists(work_path):
    os.makedirs(work_path)
if not os.path.exists(data_path):
    os.makedirs(data_path)
if not os.path.exists(img_path):
    os.makedirs(img_path)

os.chdir(work_path)
print("Python: 工作目录 " + work_path)
