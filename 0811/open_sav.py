# -*- coding: utf-8 -*-
"""
打开 SPSS(.sav) 文件的通用脚本
用法:
    python open_sav.py "D:\\...\\入住老人调研结果.sav"        # 预览内容(带值标签)
    python open_sav.py "xxx.sav" --labels                      # 同上(默认)
    python open_sav.py "xxx.sav" --raw                         # 显示原始数字编码
    python open_sav.py "xxx.sav" --to-csv out.csv              # 导出 CSV
    python open_sav.py "xxx.sav" --to-excel out.xlsx           # 导出 Excel
"""
import sys
import pyreadstat


def read_file(path, raw=False):
    df, meta = pyreadstat.read_sav(path)
    if raw:
        return df, meta
    # 把数字编码替换为值标签(如 1=男, 2=女)
    labels = getattr(meta, "variable_value_labels", None) or {}
    df2 = df.copy()
    for col, mapping in labels.items():
        if col in df2.columns:
            df2[col] = df2[col].map(mapping)
    return df2, meta


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)

    path = args[0]
    mode = "--labels"
    out = None
    for a in args[1:]:
        if a in ("--labels", "--raw"):
            mode = a
        elif a in ("--to-csv", "--to-excel"):
            idx = args.index(a)
            out = args[idx + 1]
            mode = a

    df, meta = read_file(path, raw=(mode == "--raw"))

    if mode == "--to-csv":
        df.to_csv(out, index=False, encoding="utf-8-sig")
        print(f"已导出 CSV: {out}   ({len(df)} 行 x {len(df.columns)} 列)")
        return
    if mode == "--to-excel":
        df.to_excel(out, index=False)
        print(f"已导出 Excel: {out}   ({len(df)} 行 x {len(df.columns)} 列)")
        return

    print(f"文件: {path}")
    print(f"数据: {len(df)} 行 x {len(df.columns)} 列")
    print(f"编码: {getattr(meta, 'file_encoding', '?')}")
    print("=" * 90)
    for col in df.columns:
        label = ""
        if mode == "--labels":
            mapping = (meta.variable_value_labels or {}).get(col, {})
            shown = df[col].dropna().unique()
            label = "  [" + " / ".join(str(v) for v in shown) + "]"
        print(f"  {col}{label}")
    print("=" * 90)
    import pandas as pd
    with pd.option_context("display.max_columns", None, "display.width", 200, "display.max_rows", 60):
        print(df)


if __name__ == "__main__":
    main()
