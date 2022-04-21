import argparse

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def main(input_csv, output="clock-offset.png", filter_time_fn=None):
    results = pd.read_csv(input_csv)
    results["datetime"] = pd.to_datetime(results["datetime"])

    if filter_time_fn:
        print(f"Removing everything but time_fn={filter_time_fn!r}")
        results = results.loc[results.time_fn == filter_time_fn].copy()

    results["name"] = "OnePlus 8"  # results.name.map(lambda name: name.split(":")[1])
    by_address = results.groupby(["name", "time_fn"]).clockoffset_mean
    for _, df in by_address:
        print(_)
        print(df)
        results.loc[df.index, "clockoffset_mean"] -= df.iloc[0]

    cols = ["time_fn", "name", "datetime"]
    results.sort_values(cols, inplace=True)
    print(results[cols + ["clockoffset_mean"]])

    results.rename(
        columns={"clockoffset_mean": "aligned clock offset mean (ms)"}, inplace=True
    )

    fg = sns.relplot(
        kind="line",
        data=results,
        x="datetime",
        y="aligned clock offset mean (ms)",
        row="name",
        col="time_fn",
        aspect=2,
        height=3,
        marker="o",
    )
    _set_date_formatter(fg)
    fg.savefig(output)


def _set_date_formatter(facet_grid):
    for ax in facet_grid.axes.flat:
        if ax.get_xlabel():
            locator = mdates.MinuteLocator(byminute=[0, 20, 40])
            ax.xaxis.set_major_locator(locator)
            ax.xaxis.set_major_formatter(mdates.AutoDateFormatter(locator))
            plt.setp(ax.get_xticklabels(), rotation=90)


if __name__ == "__main__":
    sns.set()
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv")
    parser.add_argument("-o", "--output", default="clock-offset.png")
    parser.add_argument("-tf", "--time_fn", default=None)
    args = parser.parse_args()
    main(
        args.input_csv,
        args.output,
        filter_time_fn=args.time_fn,
    )
