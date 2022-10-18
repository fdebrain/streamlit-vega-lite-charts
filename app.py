import numpy as np
import pandas as pd
import streamlit as st
from sklearn.datasets import fetch_openml

from src.plots import (
    plot_2d_histo,
    plot_bar,
    plot_box,
    plot_donut_simple,
    plot_donut_complex,
    plot_histo,
    plot_line,
    plot_scatter,
    plot_series_heatmap,
    plot_timeseries,
)

DATASET_LIST = ["titanic", "iris", "diabetes", "wine", "sonar"]
TIME_SCALES = [
    "year",
    "month",
    "day",
    "date",
    "week",
    "hours",
    "minutes",
    "monthyear",
    "monthdate",
    "yearmonthdate",
]
MSG_SELECT_VALUE_X = "Please select a value for X."


@st.experimental_memo
def get_data(name):
    return fetch_openml(
        name=name,
        version=1,
        as_frame=True,
        target_column=None,
        return_X_y=True,
    )


def generate_select_boxes(options_x, options_y, options_color, key_prefix):
    select_boxes = [None, None, None]
    if options_x:
        col_x = st.selectbox(
            label="X",
            options=[""] + options_x,
            key=f"{key_prefix}_x",
        )
        select_boxes[0] = col_x

    if options_y:
        col_y = st.selectbox(
            label="Y",
            options=[""] + options_y,
            key=f"{key_prefix}_y",
        )
        select_boxes[1] = col_y

    if options_color:
        col_color = st.selectbox(
            label="Color",
            options=[""] + options_color,
            key=f"{key_prefix}_color",
        )
        select_boxes[2] = col_color

    return select_boxes


if __name__ == "__main__":
    st.header("Streamlit Vega Lite Charts")
    st.caption(
        "Generate insightful charts from tabular data using Vega-Lite and Streamlit."
    )

    if name := st.selectbox(label="Select a dataset", options=[""] + DATASET_LIST):
        # Load data + add synthetic datetime column
        df, _ = get_data(name)
        time = pd.DataFrame(
            {
                "date": pd.date_range(
                    start="2000-01-01",
                    end="2022-01-01",
                    periods=len(df),
                )
            }
        )
        df = pd.concat([df, time], axis=1)

        # Dataframe overview
        st.dataframe(df)

        # Segment columns by types
        datetime_cols = list(df.select_dtypes(include=[np.datetime64]).columns.values)
        num_cols = list(df.select_dtypes(include=[np.number]).columns.values)
        cont_cols = [col for col in num_cols if df[col].nunique() > 20]
        cat_cols = [col for col in df.columns if col not in cont_cols + datetime_cols]
        with st.expander(label="Detected types"):
            st.json({"num": cont_cols, "cat": cat_cols, "datetime": datetime_cols})

        # Plot
        (
            tab_bar,
            tab_histo,
            tab_timeseries,
            tab_boxplot,
            tab_scatter,
            tab_donut_simple,
            tab_donut_complex,
            tab_line,
        ) = st.tabs(
            ["Bar", "Histogram", "Time Series", "Boxplot", "Scatter",
                "Donut Simple", "Donut Complex", "Line"]
        )
        with tab_bar:
            col_x, col_y, col_color = generate_select_boxes(
                options_x=cat_cols,
                options_y=cont_cols,
                options_color=cat_cols,
                key_prefix="bar",
            )

            if not col_x:
                st.warning(MSG_SELECT_VALUE_X)
            elif not col_y and not col_color:
                st.subheader("Count bar plot")
                plot_bar(df, col_x=col_x, agg="count")
            elif col_y and not col_color:
                st.subheader("Mean bar plot")
                plot_bar(df, col_x=col_x, col_y=col_y, agg="mean")
            elif not col_y and col_color:
                st.subheader("Stacked bar")
                plot_bar(df, col_x=col_x, col_color=col_color, agg="count")

                st.subheader("Normed bar")
                plot_bar(df, col_x=col_x, col_color=col_color, agg="count", norm=True)
            else:
                st.subheader("Grouped bar")
                plot_bar(
                    df,
                    col_x=col_x,
                    col_y=col_y,
                    col_color=col_color,
                    agg="mean",
                    group=True,
                )

        with tab_histo:
            col_x, col_y, col_color = generate_select_boxes(
                options_x=cont_cols,
                options_y=cont_cols + cat_cols,
                options_color=cat_cols,
                key_prefix="histo",
            )
            bins = st.slider(label="Bins", min_value=1, max_value=100, value=10)
            ordinal = st.checkbox(label="Ordinal", value=False)

            if not col_x:
                st.warning(MSG_SELECT_VALUE_X)
            elif not col_y and not col_color:
                normalize = st.checkbox(label="Normalize", value=False)

                if ordinal and normalize:
                    st.warning("Please select only one (Ordinal or Normalize)")
                else:
                    st.subheader("Simple histogram")
                    plot_histo(
                        df,
                        col_x=col_x,
                        bin=bins,
                        ordinal=ordinal,
                        normalize=normalize,
                    )
            elif col_y and not col_color:
                st.subheader("2D scatter histogram")
                plot_2d_histo(
                    df,
                    mark="circle",
                    col_x=col_x,
                    col_y=col_y,
                    bin_x=bins,
                    bin_y=bins,
                    ordinal=ordinal,
                )

                st.subheader("2D heatmap histogram")
                plot_2d_histo(
                    df,
                    mark="rect",
                    col_x=col_x,
                    col_y=col_y,
                    bin_x=bins,
                    bin_y=bins,
                    ordinal=ordinal,
                )
            elif not col_y and col_color:
                st.subheader("Stacked histogram")
                plot_histo(
                    df,
                    col_x=col_x,
                    col_color=col_color,
                    bin=bins,
                    ordinal=ordinal,
                )

                st.subheader("Layered histogram")
                plot_histo(
                    df,
                    col_x=col_x,
                    col_color=col_color,
                    bin=bins,
                    layered=True,
                    ordinal=ordinal,
                )
            else:
                st.warning("You cannot select Y and Color at the same time.")

        with tab_timeseries:
            col_x, col_y, col_color = generate_select_boxes(
                options_x=datetime_cols,
                options_y=cont_cols,
                options_color=cat_cols,
                key_prefix="series",
            )
            units = st.selectbox(label="Time scale", options=TIME_SCALES)
            mark = st.radio(label="Mark type", options=["line", "bar"], horizontal=True)
            if not col_x:
                st.warning(MSG_SELECT_VALUE_X)
            elif not col_y:
                st.subheader("Count series plot")
                plot_timeseries(
                    df,
                    mark=mark,
                    unit=units,
                    col_x=col_x,
                    col_color=col_color,
                    agg="count",
                )
            else:
                st.header("Aggregated series plot")
                agg = st.selectbox(
                    label="Aggregation method",
                    options=["mean", "median", "max", "min"],
                    key="agg_time_series",
                )
                plot_timeseries(
                    df,
                    mark=mark,
                    unit=units,
                    col_x=col_x,
                    col_y=col_y,
                    col_color=col_color,
                    agg=agg,
                )
                st.header("Heatmap series plot")
                agg_heat = st.selectbox(
                    label="Aggregation method",
                    options=["mean", "median", "max", "min"],
                    key="agg_time_series_heat",
                )
                ht_scale = st.selectbox(
                    label="Heatmap time scale",
                    options=["Month v/s Day", "Day v/s Hour", "Month v/s Year"],
                )
                ht_units = {
                    "Month v/s Day": ["date", "month"],
                    "Day v/s Hour": ["hours", "date"],
                    "Month v/s Year": ["year", "month"],
                }
                plot_series_heatmap(
                    df,
                    col_date=col_x,
                    col_color=col_y,
                    unit_x=ht_units[ht_scale][0],
                    unit_y=ht_units[ht_scale][1],
                    agg=agg_heat,
                )

        with tab_boxplot:
            col_x, col_y, _ = generate_select_boxes(
                options_x=cat_cols,
                options_y=cont_cols,
                options_color=None,
                key_prefix="box",
            )
            zero = st.checkbox(label="Zero", value=True)
            color = st.checkbox(label="Color", value=False)

            if col_y:
                st.header("Box plot")
                plot_box(
                    df,
                    col_x,
                    col_y,
                    col_color=col_x if color else "",
                    zero=zero,
                )
            else:
                st.warning("Please select a value for Y.")

        with tab_scatter:
            col_x, col_y, col_color_1 = generate_select_boxes(
                options_x=cont_cols,
                options_y=cont_cols,
                options_color=cat_cols,
                key_prefix="scatter",
            )
            mark = st.radio(
                label="Mark type",
                options=["point", "circle"],
                horizontal=True,
            )
            if col_x and col_y:
                st.header("Scatter plot")
                plot_scatter(df, mark, col_x, col_y, col_color)
            else:
                st.warning("Please select values for both X and Y.")

        with tab_donut_simple:
            _, _, col_color = generate_select_boxes(
                options_x=None,
                options_y=None,
                options_color=cat_cols,
                key_prefix="sdonut",
            )
            if col_color:
                plot_donut_simple(df, col_color)
            else:
                st.warning("Please select a value for Color.")

        with tab_donut_complex:
            _, _, col_color = generate_select_boxes(
                options_x=None,
                options_y=None,
                options_color=cat_cols,
                key_prefix="cdonut",
            )
            col_color_2 = st.selectbox(
                label="Second Color",
                options=[""] + cat_cols,
                key="cdonut_color2",
            )
            if col_color and col_color_2:
                plot_donut_complex(df, col_color, col_color_2)
            else:
                st.warning("Please select a value for both Colors.")

        with tab_line:
            col_x, col_y, col_color = generate_select_boxes(
                options_x=cont_cols + datetime_cols,
                options_y=cont_cols + datetime_cols,
                options_color=cat_cols,
                key_prefix="line",
            )
            if col_x and col_y:
                plot_line(df, col_x, col_y, col_color)
            else:
                st.warning("Please select values for both X and Y.")
