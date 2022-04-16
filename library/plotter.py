import numpy as np
import matplotlib.pyplot as plt
from glob import glob
from datetime import datetime


def get_data(config=None):
    if config is None:
        config = {
            "logger": {"path": "helium_nu", "file_name": "scheer2_helium"},
            "plotter": {
                "pattern": "[('date','datetime64[s]'),('fill_height','f8'),('volume','f8'),('percentage','f8')]",
                "max_days": 30,
            },
        }
    files = glob(f"{config['logger']['path']}{config['logger']['file_name']}_*.csv")[-config["plotter"]["max_days"]:]
    data = np.array([0], dtype=eval(config["plotter"]["pattern"]))
    for file in files:
        dat = np.genfromtxt(
            file, comments="#", delimiter=",", dtype=eval(config["plotter"]["pattern"])
        )
        data = np.concatenate((data, dat), axis=0)
    return data[1:]


def get_consumption(data):
    x = np.array(data["date"], dtype="float64")
    y = data["volume"]
    y[y <= 12] = np.nan
    y[y >= 78] = np.nan

    nux = np.arange(np.min(x), np.max(x), 600)
    extra_point = 2 * nux[-1] - nux[-2]
    bins = np.ones(len(nux) + 1) * extra_point
    bins[:-1] = nux

    tempx = x[np.logical_not(np.isnan(y))]
    tempy = y[np.logical_not(np.isnan(y))]

    nuy_d = np.histogram(tempx, bins)[0]
    nuy_d = np.array(nuy_d, dtype="float64")
    nuy_d[nuy_d == 0] = np.nan
    nuy = np.histogram(tempx, bins, weights=tempy)[0] / nuy_d

    nudy = np.gradient(nuy) * 6
    nudy[nudy > 0] = np.nan

    nudy = np.convolve(nudy, np.ones(5), "same") / 5
    nudx = np.arange(np.min(x), np.max(x), 3600)
    dextra_point = 2 * nudx[-1] - nudx[-2]
    bins = np.ones(len(nudx) + 1) * dextra_point
    bins[:-1] = nudx

    tempdx = nux[np.logical_not(np.isnan(nudy))]
    tempdy = nudy[np.logical_not(np.isnan(nudy))]

    nudy_d = np.histogram(tempdx, bins)[0]
    nudy_d = np.array(nudy_d, dtype="float64")
    nudy_d[nudy_d == 0] = np.nan
    nunudy = np.histogram(tempdx, bins, weights=tempdy)[0] / nudy_d
    return np.array(nudx, dtype="datetime64[s]"), nunudy


def generate_plot_scheer_2(args, config):
    data = get_data(config)

    x, y = data["date"], data["volume"]
    fig, axa = plt.subplots(figsize=(6, 3.6), dpi=300)
    fig.patch.set_facecolor("white")

    if args["time"] is not None:
        x_max = np.array(x[-1], dtype="float64")
        x_min = np.array(x[-1], dtype="float64")
        x_min = x_min - np.array(np.timedelta64(int(args["time"] * 3600), "s"), dtype="float64")
        if args["before"] is not None:
            x_max = x_max - np.array(
                np.timedelta64(int(args["before"] * 3600), "s"), dtype="float64"
            )
            x_min = x_min - np.array(
                np.timedelta64(int(args["before"] * 3600), "s"), dtype="float64"
            )
        index = [
            np.abs(np.array(x, dtype="float64") - x_min).argmin(),
            np.abs(np.array(x, dtype="float64") - x_max).argmin(),
        ]

        x = x[index[0]:index[1]]
        x = (np.array(x, dtype="float64") - np.array(x[-1], dtype="float64")) / 3600
        y = y[index[0]:index[1]]

        axa.set_xlabel(f"time till {str(data['date'][-1]).replace('T',' ')} [h]")
    else:
        x = data["date"]
        y = data["volume"]
        axa.set_xlabel("date")
        axa.xaxis.set_tick_params(rotation=45)

    seeblau = [89 / 255, 199 / 255, 235 / 255]
    axa.plot(x, y, ".", ms=1, c=seeblau, label=f"")
    if args["consumption"]:
        axb = axa.twinx()
        (dx, dy) = get_consumption(data)
        if args["time"] is not None:
            dx_max = np.array(dx[-1], dtype="float64")
            dx_min = np.array(dx[-1], dtype="float64")
            dx_min = dx_min - np.array(
                np.timedelta64(int(args["time"] * 3600), "s"), dtype="float64"
            )
            if args["before"] is not None:
                dx_max = dx_max - np.array(
                    np.timedelta64(int(args["before"] * 3600), "s"), dtype="float64"
                )
                dx_min = dx_min - np.array(
                    np.timedelta64(int(args["before"] * 3600), "s"), dtype="float64"
                )
            dindex = [
                np.abs(np.array(dx, dtype="float64") - dx_min).argmin(),
                np.abs(np.array(dx, dtype="float64") - dx_max).argmin(),
            ]
            dx = dx[dindex[0]:dindex[1]]
            dx = (np.array(dx, dtype="float64") - np.array(dx[-1], dtype="float64")) / 3600
            dy = dy[dindex[0]:dindex[1]]

        pinky = [224 / 255, 96 / 255, 126 / 255]
        axb.plot(dx, dy, "+", ms=4, c=pinky)
        axa.set_ylabel("He volume [L]", color=seeblau)
        axa.tick_params(axis="y", labelcolor=seeblau)
        axb.set_ylabel(r"He consumption [L$\,$/$\,$h]", color=pinky)
        axb.tick_params(axis="y", labelcolor=pinky)
    else:
        axa.set_ylabel("He volume [L]")

    if not args["y_zoom"]:
        axa.set_ylim([0, 85])

    axa.grid()
    title = config["plotter"]["title"]
    if title is not None:
        plt.title(title)

    file_name = "._temp.png"
    plt.savefig(file_name, bbox_inches="tight")
    plt.close("all")
    caption = f"plot generated at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}"
    return file_name, caption


"""
# Test
args = plot_arg_handler('y:1 c:1')
print(args)
generate_plot(args)
"""
