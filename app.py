import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import plotly.subplots as sp
import io
import requests

st.set_page_config(layout="wide")
st.title("Interactive EMG Signal Viewer")

# URL to your raw Excel file on GitHub
GITHUB_RAW_URL = "https://raw.githubusercontent.com/icfog2025/Demos_tests/main/FoGProvoking_DelsysData_shortWalks.xlsx"

# Try to load the file from GitHub
try:
    response = requests.get(GITHUB_RAW_URL)
    response.raise_for_status()  # Raise error for bad status
    file_bytes = io.BytesIO(response.content)
    df = pd.read_excel(file_bytes)

    st.success("EMG file loaded from GitHub!")

except Exception as e:
    st.error("Failed to load EMG data from GitHub.")
    st.info("You can still upload your own Excel file below:")
    uploaded_file = st.file_uploader("Upload your EMG Excel file", type=["xlsx"])
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            st.success("File uploaded and loaded successfully!")
        except Exception as e:
            st.error(f"Error reading uploaded file: {e}")
            df = None
    else:
        df = None

# If we have valid data to show
if 'df' in locals() and df is not None:
    try:
        time = df.iloc[:, 0]
        channel_names = df.columns[1:]
        emg_channels = df[channel_names]

        selected_channels = st.multiselect(
            "Select EMG channels to plot",
            channel_names,
            default=list(channel_names)
        )

        if selected_channels:
            fig = sp.make_subplots(
                rows=len(selected_channels), cols=1,
                shared_xaxes=True, vertical_spacing=0.02,
                subplot_titles=selected_channels
            )

            for i, channel in enumerate(selected_channels):
                fig.add_trace(
                    go.Scatter(x=time, y=emg_channels[channel], mode='lines', name=channel),
                    row=i + 1, col=1
                )

            fig.update_layout(
                height=300 * len(selected_channels),
                showlegend=False
            )
            fig.update_xaxes(title_text="Time (s)")
            fig.update_yaxes(title_text="EMG")

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Please select at least one channel to display.")

    except Exception as e:
        st.error(f"An error occurred while processing the data: {e}")
