from bokeh.plotting import figure
from bokeh.layouts import column
from bokeh.models import (
    Button,
    ColumnDataSource,
    Select,
    MultiSelect,
    Div,
    TextInput,
    BoxSelectTool,
    DataTable,
    TableColumn,
    StringFormatter,
)

# intialize widgets
save_button = Button(label="Save flagged data", button_type="success")
parameter = Select(title="Parameter", options=["CTDSAL", "CTDTMP"], value="CTDSAL")
ref_param = Select(title="Reference", options=["SALNTY"], value="SALNTY")
# ref_param.options = ["foo","bar"]  # can dynamically change dropdowns
station = Select(title="Station")
# explanation of flags:
# https://cchdo.github.io/hdo-assets/documentation/manuals/pdf/90_1/chap4.pdf
flag_list = MultiSelect(
    title="Plot data flagged as:",
    value=["1", "2", "3"],
    options=[
        ("1", "1 [Uncalibrated]"),
        ("2", "2 [Acceptable]"),
        ("3", "3 [Questionable]"),
        ("4", "4 [Bad]"),
    ],
)
# returns list of select options, e.g., ['2'] or ['1','2']
flag_input = Select(
    title="Flag:",
    options=[
        ("1", "1 [Uncalibrated]"),
        ("2", "2 [Acceptable]"),
        ("3", "3 [Questionable]"),
        ("4", "4 [Bad]"),
    ],
    value="3",
)
comment_box = TextInput(value="", title="Comment:")

# button_type: default, primary, success, warning or danger
flag_button = Button(label="Apply to selected", button_type="primary")
comment_button = Button(label="Apply to selected", button_type="warning")

vspace = Div(text=""" """, width=200, height=65)
bulk_flag_text = Div(
    text="""<br><br>
    <b>Bulk Bottle Flagging:</b><br>
    Select multiple bottles using the table
    (with shift/control) or the 'Box Select' tool on the plot.""",
    width=150,
    height=135,
)

controls = column(
    parameter,
    ref_param,
    station,
    flag_list,
    bulk_flag_text,
    flag_input,
    flag_button,
    comment_box,
    comment_button,
    vspace,
    save_button,
    width=170,
)

# set up datasources
src_table = ColumnDataSource(data=dict())
src_table_changes = ColumnDataSource(data=dict())
src_plot_trace = ColumnDataSource(data=dict(x=[], y=[]))
src_plot_ctd = ColumnDataSource(data=dict(x=[], y=[]))
src_plot_upcast = ColumnDataSource(data=dict(x=[], y=[]))
src_plot_btl = ColumnDataSource(data=dict(x=[], y=[]))

# set up plots
fig = figure(
    plot_height=800,
    plot_width=400,
    title="{} vs CTDPRS [Station {}]".format(parameter.value, station.value),
    tools="pan,box_zoom,wheel_zoom,box_select,reset",
    y_axis_label="Pressure (dbar)",
)
fig.line(
    "x",
    "y",
    line_color="#000000",
    line_width=2,
    source=src_plot_trace,
    legend_label="CTD Trace",
)
btl_sal = fig.asterisk(
    "x",
    "y",
    size=12,
    line_width=1.5,
    color="#0033CC",
    source=src_plot_btl,
    legend_label="Bottle sample",
)
ctd_sal = fig.circle(
    "x",
    "y",
    size=7,
    color="#BB0000",
    source=src_plot_ctd,
    legend_label="Downcast CTD sample",
)
upcast_sal = fig.triangle(
    "x",
    "y",
    size=7,
    color="#00BB00",
    source=src_plot_upcast,
    legend_label="Upcast CTD sample",
)
fig.select(BoxSelectTool).select_every_mousemove = False
fig.y_range.flipped = True  # invert y-axis
fig.legend.location = "bottom_left"
fig.legend.border_line_width = 3
fig.legend.border_line_alpha = 1
btl_sal.nonselection_glyph.line_alpha = 0.2
ctd_sal.nonselection_glyph.fill_alpha = 1  # makes CTDSAL *not* change on select
upcast_sal.nonselection_glyph.fill_alpha = 1  # makes CTDSAL *not* change on select


# build data tables
columns = []
fields = ["SSSCC", "SAMPNO", "CTDPRS", "CTDSAL", "SALNTY", "diff", "flag", "Comments"]
titles = ["SSSCC", "Bottle", "CTDPRS", "CTDSAL", "SALNTY", "Residual", "Flag", "Comments"]
widths = [40, 20, 75, 65, 65, 65, 15, 135]
for (field, title, width) in zip(fields, titles, widths):
    if field == "flag":
        strfmt_in = {"text_align": "center", "font_style": "bold"}
    elif field == "Comments":
        strfmt_in = {}
    else:
        strfmt_in = {"text_align": "right"}
    columns.append(TableColumn(
        field=field,
        title=title,
        width=width,
        formatter=StringFormatter(**strfmt_in)
    ))

columns_changed = []
fields = ["SSSCC", "SAMPNO", "diff", "flag_old", "flag_new", "Comments"]
titles = ["SSSCC", "Bottle", "Residual", "Old", "New", "Comments"]
widths = [40, 20, 40, 20, 20, 200]
for (field, title, width) in zip(fields, titles, widths):
    if field == "flag_old":
        strfmt_in = {"text_align": "center", "font_style": "bold"}
    elif field == "flag_new":
        strfmt_in = {"text_align": "center", "font_style": "bold", "text_color": "red"}
    elif field == "Comments":
        strfmt_in = {}
    else:
        strfmt_in = {"text_align": "right"}
    columns_changed.append(TableColumn(
        field=field,
        title=title,
        width=width,
        formatter=StringFormatter(**strfmt_in)
    ))

data_table = DataTable(
    source=src_table,
    columns=columns,
    index_width=20,
    width=480 + 20,  # sum of col widths + idx width
    height=600,
    editable=True,
    fit_columns=True,
    sortable=False,
)
data_table_changed = DataTable(
    source=src_table_changes,
    columns=columns_changed,
    index_width=20,
    width=480 + 20,  # sum of col widths + idx width
    height=200,
    editable=False,
    fit_columns=True,
    sortable=False,
)
data_table_title = Div(text="""<b>All Station Data:</b>""", width=200, height=15)
data_table_changed_title = Div(text="""<b>Flagged Data:</b>""", width=200, height=15)

tables = column(
    data_table_title, data_table, data_table_changed_title, data_table_changed
)
