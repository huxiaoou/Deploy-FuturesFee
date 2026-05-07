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


def cal_impact_rate(spread: str, price: float) -> float:
    __unit_list = ["元/吨", "元/500千克", "元/立方米", "元(人民币)/桶", "元(人民币)/吨", "元/克", "元/千克"]
    for unit in __unit_list:
        if spread.endswith(unit):
            return float(spread[: -len(unit)]) / price / 2 * 10000
    return 0.00


def summary(df: pd.DataFrame, rate_names: list[str]):
    res = {}
    for rate_name in rate_names:
        res[rate_name] = {
            "mean": df[rate_name].mean(),
            "max": df[rate_name].max(),
            "q75": df[rate_name].quantile(0.75),
            "q50": df[rate_name].quantile(0.50),
            "q25": df[rate_name].quantile(0.25),
            "min": df[rate_name].min(),
        }
    print(pd.DataFrame(res).T)
    return


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
        "JR.CZC",
        "RS.CZC",
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

    source_file = "全部国内主力合约.xlsx"
    df = pd.read_excel(source_file, dtype=str)
    df.columns = ["code", "name", "fee_rate", "fee_rate_td", "price", "mulitplier", "spread"]
    df = df.dropna(axis=0, how="any", subset="name")

    df["to_drop"] = df["code"].apply(lambda x: re.sub(r"\d", "", x) in drop_list)
    df = df[df["to_drop"] == False].drop(columns=["to_drop"])

    # --- aver_rate ---
    df["open_rate"] = df.apply(lambda x: cal_rate(x["fee_rate"], float(x["price"]), float(x["mulitplier"])), axis=1)
    df["close_rate"] = df.apply(lambda x: cal_rate(x["fee_rate_td"], float(x["price"]), float(x["mulitplier"])), axis=1)
    df["aver_fee_rate"] = (df["open_rate"] + df["close_rate"]) / 2

    # --- impact_rate ---
    df["impact_rate"] = df.apply(lambda x: cal_impact_rate(x["spread"], float(x["price"])), axis=1)

    # --- total_rate ---
    df["total_rate"] = df["aver_fee_rate"] + df["impact_rate"]

    # --- display ---
    df = df.sort_values(by="total_rate", ascending=False).reset_index(drop=True)
    print(df)
    summary(df, ["aver_fee_rate", "impact_rate", "total_rate"])


if __name__ == "__main__":
    main()
