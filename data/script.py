import pandas as pd
from pathlib import Path

files = ["daily_sales_data_0.csv", "daily_sales_data_1.csv", "daily_sales_data_2.csv"]
df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)

df = df[df["product"] == "Pink Morsels"]        # 先筛选
df["sales"] = df["quantity"] * df["price"]      # 再计算
out = df[["sales", "date", "region"]]           # 最后选三列
out.to_csv("output.csv", index=False)