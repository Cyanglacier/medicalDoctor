import pandas as pd
import random

# 读取CSV文件
df = pd.read_csv('tcm_exam_1.csv')

# 随机抽取500条记录
sample_df = df.sample(n=500, random_state=42)

# 导出到新的CSV文件
sample_df.to_csv('tcm_exam_sample_500.csv', index=False)