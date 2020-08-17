import pandas as pd
from pathlib import Path
import gsw
from functools import partial

import ctd_io
import callbacks as cb
import widgets

from bokeh.io import curdoc
from bokeh.layouts import row

# TODO: abstract parts of this to a separate file
# TODO: following above, make parts reusable?

ssscc_list = sorted(Path("data/pressure/").glob("*.csv"))
ssscc_list = [x.stem.split("_")[0] for x in ssscc_list]
widgets.station.options = ssscc_list
widgets.station.value = ssscc_list[0]

# load continuous CTD data and make into a dict (only ~20MB)
ctd_data = ctd_io.load_ct1(dir="data/pressure/")

# load bottle trip file
upcast_data = ctd_io.load_pkl(dir="data/bottle/")
upcast_data["CTDSAL"] = gsw.SP_from_C(
    upcast_data["CTDCOND1"], upcast_data["CTDTMP1"], upcast_data["CTDPRS"]
)

# load salt file
salt_data = ctd_io.load_salt(dir="data/salt/")
salt_data["SALNTY"] = salt_data["SALNTY"].round(4)
if "SALNTY_FLAG_W" not in salt_data.columns:
    salt_data["SALNTY_FLAG_W"] = 2

# load ctd btl data
df_ctd_btl = pd.read_csv(
    "data/ctd_to_bottle.csv",
    skiprows=[1],
    skipfooter=1,
    engine="python",
)
df_btl_all = pd.merge(df_ctd_btl, salt_data, on=["STNNBR", "CASTNO", "SAMPNO"])
btl_data = df_btl_all.loc[
    :,
    [
        "SSSCC",
        "SAMPNO",
        "CTDPRS",
        "CTDTMP",
        "REFTMP",
        "CTDSAL",
        "SALNTY",
        "SALNTY_FLAG_W",
    ],
]
btl_data["Residual"] = btl_data["SALNTY"] - btl_data["CTDSAL"]
btl_data[["CTDPRS", "Residual"]] = btl_data[["CTDPRS", "Residual"]].round(4)
btl_data["Comments"] = ""
btl_data["New Flag"] = btl_data["SALNTY_FLAG_W"].copy()

# update with old handcoded flags if file exists
handcoded_file = "salt_flags_handcoded.csv"
if Path(handcoded_file).exists():
    handcodes = pd.read_csv(handcoded_file, dtype={"SSSCC": str}, keep_default_na=False)
    handcodes = handcodes.rename(columns={"salinity_flag": "New Flag"}).drop(
        columns="diff"
    )
    # there's gotta be a better way... but this is good enough for now
    btl_data = btl_data.merge(handcodes, on=["SSSCC", "SAMPNO"], how="left")
    merge_rows = ~btl_data["New Flag_y"].isnull() | ~btl_data["Comments_y"].isnull()
    btl_data.loc[merge_rows, "New Flag_x"] = btl_data.loc[merge_rows, "New Flag_y"]
    btl_data.loc[merge_rows, "Comments_x"] = btl_data.loc[merge_rows, "Comments_y"]
    btl_data = btl_data.rename(
        columns={"New Flag_x": "New Flag", "Comments_x": "Comments"}
    ).drop(columns=["New Flag_y", "Comments_y"])

# set up change callbacks
for x in [widgets.parameter, widgets.station, widgets.flag_list]:
    x.on_change(
        "value",
        partial(
            cb.update_selectors,
            ctd_data=ctd_data,
            btl_data=btl_data,
            upcast_data=upcast_data,
            btl_sal=widgets.btl_sal,
            station=widgets.station,
            flag_list=widgets.flag_list,
            parameter=widgets.parameter,
            src_table=widgets.src_table,
            src_plot_trace=widgets.src_plot_trace,
            src_plot_ctd=widgets.src_plot_ctd,
            src_plot_upcast=widgets.src_plot_upcast,
            src_plot_btl=widgets.src_plot_btl,
            fig=widgets.fig,
        ),
    )
widgets.flag_button.on_click(
    partial(
        cb.apply_flag,
        btl_data=btl_data,
        station=widgets.station,
        src_table=widgets.src_table,
        flag_input=widgets.flag_input,
    )
)
widgets.comment_button.on_click(
    partial(
        cb.apply_comment,
        btl_data=btl_data,
        station=widgets.station,
        src_table=widgets.src_table,
        comment_box=widgets.comment_box,
    )
)
widgets.save_button.on_click(
    partial(cb.save_data, src_table_changes=widgets.src_table_changes)
)
widgets.src_table.on_change(
    "data",
    partial(
        cb.edit_flag,
        btl_data=btl_data,
        src_table=widgets.src_table,
        src_table_changes=widgets.src_table_changes,
    ),
)
widgets.src_table.selected.on_change(
    "indices", partial(cb.selected_from_table, btl_sal=widgets.btl_sal)
)
widgets.btl_sal.data_source.selected.on_change(
    "indices", partial(cb.selected_from_plot, src_table=widgets.src_table)
)

# Page layout
curdoc().add_root(row(widgets.controls, widgets.tables, widgets.fig))
curdoc().title = "CTDO Data Flagging Tool"

cb.update_selectors(
    attr=None,
    old=None,
    new=None,
    ctd_data=ctd_data,
    btl_data=btl_data,
    upcast_data=upcast_data,
    btl_sal=widgets.btl_sal,
    station=widgets.station,
    flag_list=widgets.flag_list,
    parameter=widgets.parameter,
    src_table=widgets.src_table,
    src_plot_trace=widgets.src_plot_trace,
    src_plot_ctd=widgets.src_plot_ctd,
    src_plot_upcast=widgets.src_plot_upcast,
    src_plot_btl=widgets.src_plot_btl,
    fig=widgets.fig,
)
