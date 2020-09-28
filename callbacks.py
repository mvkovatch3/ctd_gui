import pandas as pd


def update_selectors(
    attr,
    old,
    new,
    ctd_data=None,
    btl_data=None,
    upcast_data=None,
    btl_sal=None,
    station=None,
    flag_list=None,
    parameter=None,
    src_table=None,
    src_plot_trace=None,
    src_plot_ctd=None,
    src_plot_upcast=None,
    src_plot_btl=None,
    fig=None,
):
    print("running update_selectors from callbacks!")

    ctd_rows = ctd_data["SSSCC"] == station.value
    table_rows = btl_data["SSSCC"] == station.value
    btl_rows = (btl_data["New Flag"].isin(flag_list.value)) & (
        btl_data["SSSCC"] == station.value
    )

    # update table data
    current_table = btl_data[table_rows].reset_index()
    src_table.data = {  # this causes edit_flag() to execute
        "SSSCC": current_table["SSSCC"],
        "SAMPNO": current_table["SAMPNO"],
        "CTDPRS": current_table["CTDPRS"],
        "CTDSAL": current_table["CTDSAL"],
        "SALNTY": current_table["SALNTY"],
        "diff": current_table["Residual"],
        "flag": current_table["New Flag"],
        "Comments": current_table["Comments"],
    }

    # update plot data
    src_plot_trace.data = {
        "x": ctd_data.loc[ctd_rows, parameter.value],
        "y": ctd_data.loc[ctd_rows, "CTDPRS"],
    }
    src_plot_ctd.data = {
        "x": btl_data.loc[table_rows, parameter.value],
        "y": btl_data.loc[table_rows, "CTDPRS"],
    }
    src_plot_upcast.data = {
        "x": upcast_data.loc[upcast_data["SSSCC"] == station.value, "CTDSAL"],
        "y": upcast_data.loc[upcast_data["SSSCC"] == station.value, "CTDPRS"],
    }
    src_plot_btl.data = {
        "x": btl_data.loc[btl_rows, "SALNTY"],
        "y": btl_data.loc[btl_rows, "CTDPRS"],
    }

    # update plot labels/axlims
    fig.title.text = "{} vs CTDPRS [Station {}]".format(parameter.value, station.value)
    fig.xaxis.axis_label = parameter.value

    # deselect all datapoints
    btl_sal.data_source.selected.indices = []
    src_table.selected.indices = []


def edit_flag(attr, old, new, btl_data=None, src_table=None, src_table_changes=None):
    print("running edit_flag from callbacks!")
    btl_data.loc[
        btl_data["SSSCC"] == src_table.data["SSSCC"].values[0], "New Flag",
    ] = src_table.data["flag"].values
    btl_data.loc[
        btl_data["SSSCC"] == src_table.data["SSSCC"].values[0], "Comments",
    ] = src_table.data["Comments"].values

    edited_rows = (btl_data["New Flag"].isin([3, 4])) | (btl_data["Comments"] != "")

    src_table_changes.data = {
        "SSSCC": btl_data.loc[edited_rows, "SSSCC"],
        "SAMPNO": btl_data.loc[edited_rows, "SAMPNO"],
        "diff": btl_data.loc[edited_rows, "Residual"],
        "flag_old": btl_data.loc[edited_rows, "SALNTY_FLAG_W"],
        "flag_new": btl_data.loc[edited_rows, "New Flag"],
        "Comments": btl_data.loc[edited_rows, "Comments"],
    }


def apply_flag(btl_data=None, station=None, src_table=None, flag_input=None):
    print("running apply_flag from callbacks!")

    table_rows = btl_data["SSSCC"] == station.value
    selected_rows = src_table.selected.indices

    # update table data
    current_table = btl_data[table_rows].reset_index()
    current_table.loc[selected_rows, "New Flag"] = int(flag_input.value)
    src_table.data = {  # this causes edit_flag() to execute
        "SSSCC": current_table["SSSCC"],
        "SAMPNO": current_table["SAMPNO"],
        "CTDPRS": current_table["CTDPRS"],
        "CTDSAL": current_table["CTDSAL"],
        "SALNTY": current_table["SALNTY"],
        "diff": current_table["Residual"],
        "flag": current_table["New Flag"],
        "Comments": current_table["Comments"],
    }


def apply_comment(btl_data=None, station=None, src_table=None, comment_box=None):
    print("running apply_comment from callbacks!")

    table_rows = btl_data["SSSCC"] == station.value
    selected_rows = src_table.selected.indices

    # update table data
    current_table = btl_data[table_rows].reset_index()
    current_table.loc[selected_rows, "Comments"] = comment_box.value
    src_table.data = {  # this causes edit_flag() to execute
        "SSSCC": current_table["SSSCC"],
        "SAMPNO": current_table["SAMPNO"],
        "CTDPRS": current_table["CTDPRS"],
        "CTDSAL": current_table["CTDSAL"],
        "SALNTY": current_table["SALNTY"],
        "diff": current_table["Residual"],
        "flag": current_table["New Flag"],
        "Comments": current_table["Comments"],
    }


def save_data(src_table_changes=None):
    print("running save_data from callbacks!")

    # get data from table
    df_out = pd.DataFrame.from_dict(src_table_changes.data)

    # minor changes to columns/names/etc.
    df_out = df_out.rename(columns={"flag_new": "salinity_flag"}).drop(
        columns="flag_old"
    )

    # save it
    df_out.to_csv("salt_flags_handcoded.csv", index=None)


def selected_from_plot(attr, old, new, src_table=None):
    print("running selected_from_plot from callbacks!")
    src_table.selected.indices = new


def selected_from_table(attr, old, new, btl_sal=None):
    print("Running selected_from_table from callbacks!")
    btl_sal.data_source.selected.indices = new
