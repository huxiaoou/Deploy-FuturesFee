import pandas as pd
import re

pd.set_option("display.unicode.east_asian_width", True)
pd.set_option("display.max_rows", None)


def cal_rate(rate: str, price: float, mulitplier: float) -> float:
    if rate.endswith("%"):
        return float(rate[:-1]) * 100
    elif rate.endswith("元/手"):
        return float(rate[:-3]) / (price * mulitplier) * 10000
    return 0.00


def main():
    drop_list = [
        "IF.CFE",
        "IH.CFE",
        "IC.CFE",
        "IM.CFE",
        "TF.CFE",
        "T.CFE",
        "TS.CFE",
        "TL.CFE",

        "ZC.CZC",
        "WH.CZC",
        "PM.CZC",
        "RI.CZC",

        "pt.GFE",
        "ps.GFE",
        "pd.GFE",
        "si.GFE",
        "lc.GFE",

        "bc.INE",
        "ec.INE",
        
        "WR.SHF",
        "OP.SHF",

        "BB.DCE",
        "FB.DCE",
    ]

    source_file = "futures_fee_rate.xlsx"
    df = pd.read_excel(source_file, dtype=str)
    df.columns = ["code", "name", "fee_rate", "fee_rate_td", "price", "mulitplier"]
    df = df.dropna(axis=0, how="any", subset="name")
    
    df["to_drop"] = df["code"].apply(lambda x: re.sub(r"\d", "", x) in drop_list)
    df = df[df["to_drop"] == False].drop(columns=["to_drop"])
    
    df["open_rate"] = df.apply(lambda x: cal_rate(x["fee_rate"], float(x["price"]), float(x["mulitplier"])), axis=1)
    df["close_rate"] = df.apply(lambda x: cal_rate(x["fee_rate_td"], float(x["price"]), float(x["mulitplier"])), axis=1)
    df["aver_rate"] = (df["open_rate"] + df["close_rate"]) / 2
    df = df.sort_values(by="aver_rate", ascending=False).reset_index(drop=True)
    print(df)

    aver_rate_mean = df["aver_rate"].mean()
    max_rate = df["aver_rate"].max()
    q75_rate = df["aver_rate"].quantile(0.75)
    q50_rate = df["aver_rate"].quantile(0.50)
    q25_rate = df["aver_rate"].quantile(0.25)
    min_rate = df["aver_rate"].min()
    
    print("\n统计数据:")
    print(f"平均费率: {aver_rate_mean:.2f}‰")
    print(f"最大费率: {max_rate:.2f}‰")
    print(f"75%分位数: {q75_rate:.2f}‰")
    print(f"50%分位数: {q50_rate:.2f}‰")
    print(f"25%分位数: {q25_rate:.2f}‰")
    print(f"最小费率: {min_rate:.2f}‰")


if __name__ == "__main__":
    main()
