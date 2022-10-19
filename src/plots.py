import streamlit as st

CONFIG_MAIN = {
    "width": 600,
    "height": 400,
    "config": {"view": {"stroke": None}},  # Plot contour stroke
}


CONFIG_MARK = {
    "tooltip": True,
    "stroke": 1,
    "strokeWidth": 0.5,
}

ATT_DATA_NUM_GROUP = "datum.groupcount/datum.total"


def plot_bar(
    df,
    col_x,
    col_y=None,
    col_color=None,
    agg=None,
    norm=False,
    group=False,
):
    config_norm = (
        {
            "stack": "normalize",
            "format": ".1%",
            "axis": {"format": ".1%"},
        }
        if norm
        else {}
    )

    config_group = {"xOffset": {"field": col_color}} if group else {}

    st.vega_lite_chart(
        data=df,
        spec={
            **CONFIG_MAIN,
            "mark": {"type": "bar", **CONFIG_MARK},
            "encoding": {
                "x": {
                    "field": col_x,
                    "type": "ordinal",
                    "axis": {"labelAngle": 0},
                },
                "y": {
                    "field": col_y,
                    "type": "quantitative",
                    "aggregate": agg,
                    **config_norm,
                },
                "color": {
                    "field": col_color,
                    "type": "nominal",
                },
                **config_group,
            },
        },
    )


# TODO: Add 2D count view
def plot_timeseries(
    df,
    mark,
    col_x,
    unit,
    col_y=None,
    col_color=None,
    agg=None,
    norm=False,
):
    config_norm = (
        {"stack": "normalize", "format": ".1%", "axis": {"format": ".1%"}}
        if norm
        else {"format": ".2f"}
    )

    config_mark = (
        CONFIG_MARK
        if mark == "bar"
        else {
            "tooltip": True,
            "point": True,
        }
    )

    st.vega_lite_chart(
        data=df,
        spec={
            **CONFIG_MAIN,
            "mark": {"type": mark, **config_mark},
            "encoding": {
                "x": {
                    "field": col_x,
                    "type": "ordinal",
                    "timeUnit": unit,
                    "axis": {"labelAngle": -45 if len(df) > 20 else 0},
                },
                "y": {
                    "field": col_y,
                    "type": "quantitative",
                    "aggregate": agg,
                    **config_norm,
                },
                "color": {
                    "field": col_color,
                    "type": "nominal",
                },
            },
        },
    )


def plot_series_heatmap(
    df,
    col_date,
    col_color,
    agg="mean",
    unit_x="date",
    unit_y="month",
):
    st.vega_lite_chart(
        data=df,
        spec={
            "config": {
                "axis": {
                    "grid": True,
                    "tickBand": "extent",
                    "gridColor": "black",
                    "gridWidth": 0.5,
                }
            },
            "mark": {"type": "rect", "tooltip": True},
            "encoding": {
                "x": {
                    "field": col_date,
                    "timeUnit": unit_x,
                    "type": "ordinal",
                    "title": unit_x.capitalize(),
                },
                "y": {
                    "field": col_date,
                    "timeUnit": unit_y,
                    "type": "ordinal",
                    "title": unit_y.capitalize(),
                },
                "color": {
                    "field": col_color,
                    "aggregate": agg,
                    "type": "quantitative",
                    "legend": {"title": col_color.capitalize()},
                },
            },
        },
    )


def plot_histo(
    df,
    col_x,
    col_color=None,
    ordinal=False,
    bin=None,
    layered=False,
    normalize=False,
):
    config_bin = {"maxbins": bin} if bin else True
    config_params = (
        [
            {
                "name": "select",
                "select": {"type": "point", "fields": [col_color]},
                "bind": "legend",
            },
        ]
        if layered
        else []
    )
    config_layer = (
        {
            "opacity": {
                "condition": {"param": "select", "value": 0.8},
                "value": 0.1,
            },
            "order": {
                "field": col_color,
                "condition": {"param": "select", "value": 1},
                "value": 0,
            },
        }
        if layered
        else {}
    )
    st.vega_lite_chart(
        data=df,
        spec={
            **CONFIG_MAIN,
            "mark": {"type": "bar", **CONFIG_MARK, "blend": "normal", "binSpacing": 0},
            "params": config_params,
            "transform": [
                {"filter": f"datum.{col_x} != null"},  # Ignore NaNs
                {"bin": config_bin, "field": col_x, "as": "bin_col_x"},
                {
                    "aggregate": [{"op": "count", "as": "xCount"}],
                    "groupby": ["bin_col_x", "bin_col_x_end"],
                },
                {"joinaggregate": [{"op": "sum", "field": "xCount", "as": "TotalCount"}]},
                {"calculate": "datum.xCount/datum.TotalCount", "as": "PercentOfTotal"},
            ]
            if normalize
            else [],
            "encoding": {
                "x": {
                    "field": "bin_col_x" if normalize else col_x,
                    "type": "ordinal" if ordinal else "quantitative",
                    "axis": {"labelAngle": -45 if ordinal else 0},
                    "bin": {"maxbins": bin, "binned": True} if normalize else config_bin,
                    "title": col_x.capitalize(),
                },
                "x2": {"field": "bin_col_x_end"} if normalize else {},
                "y": {
                    "field": "PercentOfTotal" if normalize else None,
                    "type": "quantitative",
                    "aggregate": None if normalize else "count",
                    "title": "Relative Frequency" if normalize else "Count",
                    "stack": None if layered else "zero",
                    "axis": {"format": ".1~%"} if normalize else {},
                },
                "color": {"field": col_color, "type": "nominal"},
                **config_layer,
            },
        },
    )


def plot_2d_histo(df, mark, col_x, col_y, bin_x, bin_y, ordinal):
    st.vega_lite_chart(
        data=df,
        spec={
            **CONFIG_MAIN,
            "config": {
                "axis": {
                    "grid": True,
                    "tickBand": "extent",
                    "gridColor": "black",
                    "gridWidth": 0.5,
                }
                if mark == "rect"
                else {}
            },
            "mark": {"type": mark, "tooltip": True},
            "encoding": {
                "x": {
                    "field": col_x,
                    "bin": {"maxbins": bin_x},
                    "title": col_x.capitalize(),
                    "type": "ordinal" if ordinal else "quantitative",
                },
                "y": {
                    "field": col_y,
                    "bin": {"maxbins": bin_y},
                    "title": col_y.capitalize(),
                    "type": "ordinal" if ordinal else "quantitative",
                    "sort": "-y",
                },
                "size": {"aggregate": "count"},
                "color": {"aggregate": "count"} if mark == "rect" else {},
            },
        },
    )


def plot_box(df, col_x, col_y, col_color, zero):
    st.vega_lite_chart(
        data=df,
        spec={
            **CONFIG_MAIN,
            "mark": {"type": "boxplot", "ticks": True, **CONFIG_MARK},
            "encoding": {
                "x": {
                    "field": col_x,
                    "type": "ordinal",
                    "title": col_x.capitalize(),
                    "axis": {"labelAngle": 0},
                },
                "y": {
                    "field": col_y,
                    "type": "quantitative",
                    "title": col_y.capitalize(),
                    "scale": {"zero": zero},
                },
                "color": {
                    "field": col_color,
                    "type": "nominal",
                    "title": col_color.capitalize(),
                },
                "size": {"value": 30},
            },
        },
    )


def plot_scatter(df, mark, col_x, col_y, col_color=None):
    config_params = (
        [
            {
                "name": "select",
                "select": {"type": "point", "fields": [col_color]},
                "bind": "legend",
            },
        ]
        if col_color
        else []
    )
    # TODO: Fix ordering when selecting legend
    config_layer = (
        {
            "opacity": {
                "condition": {"param": "select", "value": 1.0},
                "value": 0.1,
            },
        }
        if col_color
        else {}
    )

    st.vega_lite_chart(
        data=df,
        spec={
            **CONFIG_MAIN,
            "mark": {"type": mark, "tooltip": True},
            "params": config_params,
            "encoding": {
                "x": {
                    "field": col_x,
                    "type": "quantitative",
                    "title": col_x.capitalize(),
                },
                "y": {
                    "field": col_y,
                    "type": "quantitative",
                    "title": col_y.capitalize(),
                },
                "color": {
                    "field": col_color,
                    "type": "nominal",
                    "title": col_color.capitalize(),
                },
                **config_layer,
            },
        },
    )


def plot_donut_simple(df, col_color):
    st.vega_lite_chart(
        data=df,
        spec={
            **CONFIG_MAIN,
            "mark": {"type": "arc", "innerRadius": 100, **CONFIG_MARK},
            "transform": [
                {
                    "window": [{"op": "count", "as": "total"}],
                    "frame": [None, None],
                },
                {
                    "joinaggregate": [{"op": "count", "as": "groupcount"}],
                    "groupby": [col_color],
                },
                {"calculate": ATT_DATA_NUM_GROUP, "as": "share"},
            ],
            "encoding": {
                "theta": {
                    "type": "quantitative",
                    "title": "Count",
                    "aggregate": "count",
                },
                "color": {
                    "field": col_color,
                    "type": "nominal",
                    "title": col_color.capitalize(),
                },
                "order": {
                    "field": "share",
                    "type": "quantitative",
                    "sort": "descending",
                    "title": "Share [%]",
                    "format": ".1%",
                },
            },
        },
    )


def plot_donut_complex(df, col_color_1, col_color_2):
    st.vega_lite_chart(
        data=df,
        spec={
            **CONFIG_MAIN,
            "layer": [{
                "mark": {"type": "arc", "innerRadius": 75, "radius": 150, **CONFIG_MARK},
                "transform": [
                    {
                        "window": [{"op": "count", "as": "total"}],
                        "frame": [None, None],
                    },
                    {
                        "joinaggregate": [{"op": "count", "as": "groupcount"}],
                        "groupby": [col_color_1, col_color_2],
                    },
                    {"calculate": ATT_DATA_NUM_GROUP, "as": "share"},
                ],
                "encoding": {
                    "theta": {
                        "type": "quantitative",
                        "title": "Count",
                        "aggregate": "count",
                    },
                    "color": {
                        "field": col_color_1,
                        "type": "nominal",
                        "title": col_color_1.capitalize(),
                    },
                    "order": {
                        "field": "share",
                        "type": "quantitative",
                        "sort": "descending",
                        "title": "Share [%]",
                        "format": ".1%",
                    },
                },
            }, {
                "mark": {"type": "arc", "innerRadius": 125, "radius": 175, **CONFIG_MARK},
                "transform": [
                    {
                        "window": [{"op": "count", "as": "total"}],
                        "frame": [None, None],
                    },
                    {
                        "joinaggregate": [{"op": "count", "as": "groupcount"}],
                        "groupby": [col_color_1, col_color_2],
                    },
                    {"calculate": ATT_DATA_NUM_GROUP, "as": "share"},
                ],
                "encoding": {
                    "theta": {
                        "type": "quantitative",
                        "title": "Count",
                        "aggregate": "count",
                    },
                    "color": {
                        "field": col_color_2,
                        "type": "nominal",
                        "title": col_color_2.capitalize(),
                    },
                    "order": {
                        "field": "share",
                        "type": "quantitative",
                        "sort": "descending",
                        "title": "Share [%]",
                        "format": ".1%",
                    },
                },
            }]
        },
    )


def plot_line(df, col_x, col_y, col_color):
    st.vega_lite_chart(
        data=df,
        spec={
            **CONFIG_MAIN,
            "mark": {
                "type": "line",
                "point": "true",
                "tooltip": True,
            },
            "encoding": {
                "x": {"field": col_x, "type": "quantitative", "bin": True},
                "y": {"field": col_y, "type": "quantitative", "aggregate": "mean"},
                "color": {"field": col_color, "type": "nominal"},
            },
        },
    )
