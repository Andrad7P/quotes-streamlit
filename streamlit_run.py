# streamlit_run.py
# ---
# lambda-test: false  # auxiliary-file
# ---
# ## Demo Streamlit application (extended with 2 simple charts).
#
# Based on: https://docs.streamlit.io/library/get-started/create-an-app

def main():
    import numpy as np
    import pandas as pd
    import streamlit as st

    st.title("Uber pickups in NYC!")

    DATE_COLUMN = "date/time"
    DATA_URL = (
        "https://s3-us-west-2.amazonaws.com/"
        "streamlit-demo-data/uber-raw-data-sep14.csv.gz"
    )

    @st.cache_data
    def load_data(nrows):
        data = pd.read_csv(DATA_URL, nrows=nrows)

        def lowercase(x):
            return str(x).lower()

        data.rename(lowercase, axis="columns", inplace=True)
        data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
        return data

    data_load_state = st.text("Loading data...")
    data = load_data(10000)
    data_load_state.text("Done! (using st.cache_data)")

    if st.checkbox("Show raw data"):
        st.subheader("Raw data")
        st.write(data)

    # -------- Original chart: number of pickups by hour --------
    st.subheader("Number of pickups by hour")
    hist_values = np.histogram(data[DATE_COLUMN].dt.hour, bins=24, range=(0, 24))[0]
    st.bar_chart(hist_values)

    # ======================= NEW CHART A =======================
    # Pickups by weekday (simple bar chart)
    st.subheader("Pickups by weekday")
    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekday_counts = (
        data[DATE_COLUMN]
        .dt.day_name()
        .value_counts()
        .reindex(weekday_order, fill_value=0)
    )
    # Streamlit can plot a Series directly
    st.bar_chart(weekday_counts)

    # ======================= NEW CHART B =======================
    # Daily pickups + cumulative pickups (simple line chart)
    st.subheader("Daily pickups and cumulative total")
    daily = (
        data[DATE_COLUMN]
        .dt.floor("D")           # snap to day
        .value_counts()
        .sort_index()
        .rename("pickups")
        .to_frame()
    )
    daily["cumulative"] = daily["pickups"].cumsum()
    st.line_chart(daily)  # plots both 'pickups' and 'cumulative'

    # -------- Interactivity (original) --------
    hour_to_filter = st.slider("hour", 0, 23, 17)
    filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]

    st.subheader("Map of all pickups at %s:00" % hour_to_filter)
    st.map(filtered_data)


if __name__ == "__main__":
    main()
