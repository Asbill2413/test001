# -*- coding: utf-8 -*-
import pyreadstat

df2, meta = pyreadstat.read_sav("D:/Program Files/Tencent/xwechat_files/wxid_fkvkpdswd0n822_b4e6/msg/file/2026-08/工作人员调研结果.sav")
labs = meta.variable_value_labels

def show(series, title):
    print(f"— {title}:")
    vc = series.value_counts(dropna=False)
    for k,v in vc.items():
        if pd.isna(k) if False else False: pass
    print(series.value_counts(dropna=False).to_string())
    # map numeric to label
    col = series.name
    if col in labs:
        print("   (标签:)", {v:c for c,v in labs[col].items()})

import pandas as pd
print("="*60)
print("【工作人员调研】18 份")
print("="*60)
for col in ["年龄","性别","最高学历","岗位类别","是否持有养老护理相关职业资格证书","在本机构工作年限","目前平均月收入（到手）","日均照护时间","对机构的管理制度是否满意","与同事之间的协作配合情况","过去一年内是否有离职或转行的想法","未来3年的职业规划"]:
    print(f"\n— {col}:")
    vc = df2[col].value_counts(dropna=False)
    print(vc.to_string())
    if col in labs:
        print("   标签:", labs[col])

print("\n— 负责照护的老人数量:", df2["负责照护的老人数量（护理员回答）"].dropna().tolist())
print("\n— 最大困难(多选):")
for col in ["困难1：人手不足","困难2：薪酬过低","困难3：老人家属难沟通","困难4：缺乏心理疏导支持","困难5：技能跟不上需求"]:
    print(f"  {col}: {df2[col].value_counts(dropna=False).to_dict()}")

print("\n— 5点量表题(1=非常不同意 ~ 5=非常同意):")
agree_cols = ["认为目前工作强度过大，身体疲惫感明显","经常因工作压力大而失眠或焦虑","与老人或家属的沟通经常遇到困难","对目前的薪资待遇满意","认为机构福利保障完善","机构提供岗前培训和在职技能提升机会","在本机构有清晰晋升通道和发展空间","在工作中经常感受到老人及家属的尊重与认可"]
for col in agree_cols:
    vc = df2[col].value_counts(dropna=False)
    valid = df2[col].dropna()
    mean = valid.mean() if len(valid) else float('nan')
    print(f"  {col[:22]}... 均值={mean:.2f} 分布={vc.to_dict()}")
