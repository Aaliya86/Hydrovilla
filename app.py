
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="HydroVilla Recommendation System",
    page_icon="🌱",
    layout="wide"
)

# Load reference data
@st.cache_data
def load_data():
    return pd.read_csv("hydroponic_reference_ranges.csv")

df = load_data()

st.title("🌱 HydroVilla")
st.subheader("AI-Based Hydroponic Plant Growth Recommendation System")

st.write(
    "Select your plant, choose its growth stage, "
    "enter current environmental readings and get recommendations."
)

st.divider()

# STEP 1: Plant Selection
st.header("Step 1: Select Plant")

plants = sorted(df["Species"].unique())

selected_plant = st.selectbox(
    "Choose Plant",
    plants
)

# STEP 2: Growth Stage Selection
st.header("Step 2: Select Growth Stage")

available_stages = sorted(
    df[df["Species"] == selected_plant]["Growth_Stage"].unique()
)

selected_stage = st.selectbox(
    "Choose Growth Stage",
    available_stages
)

st.success(
    f"Selected Plant: {selected_plant} | Growth Stage: {selected_stage}"
)

st.divider()

# STEP 3: Parameter Inputs
st.header("Step 3: Enter Current Readings")

parameters = {
    "pH": (0.0, 14.0, 6.0),
    "EC_mS_cm": (0.0, 10.0, 2.0),
    "TDS_ppm": (0.0, 5000.0, 1000.0),
    "Water_Temp_C": (0.0, 50.0, 20.0),
    "Air_Temp_C": (0.0, 50.0, 25.0),
    "Relative_Humidity_pct": (0.0, 100.0, 65.0),
    "PPFD_umol_m2_s": (0.0, 1500.0, 450.0),
    "DLI_mol_m2_day": (0.0, 60.0, 25.0),
    "Photoperiod_h": (0.0, 24.0, 16.0),
    "CO2_ppm": (0.0, 3000.0, 450.0),
    "Root_Zone_Temp_C": (0.0, 50.0, 20.0),
    "N_mg_L": (0.0, 1000.0, 200.0),
    "P_mg_L": (0.0, 500.0, 50.0),
    "K_mg_L": (0.0, 1000.0, 300.0),
    "Ca_mg_L": (0.0, 1000.0, 200.0),
    "Mg_mg_L": (0.0, 500.0, 60.0)
}

current_values = {}

col1, col2 = st.columns(2)

for index, (parameter, values) in enumerate(parameters.items()):

    minimum, maximum, default = values

    with col1 if index % 2 == 0 else col2:

        current_values[parameter] = st.number_input(
            parameter,
            min_value=float(minimum),
            max_value=float(maximum),
            value=float(default),
            key=parameter
        )

st.divider()

# STEP 4: Generate Recommendations
if st.button("Generate Recommendations", type="primary"):

    results = []

    selected_ranges = df[
        (df["Species"] == selected_plant) &
        (df["Growth_Stage"] == selected_stage)
    ]

    for parameter, current_value in current_values.items():

        reference = selected_ranges[
            selected_ranges["Parameter"] == parameter
        ]

        if reference.empty:
            continue

        lower = reference.iloc[0]["Lower_Range"]
        upper = reference.iloc[0]["Upper_Range"]

        if current_value < lower:
            status = "Below Range"
            recommendation = (
                "Below the dataset reference band. "
                "Review and adjust cautiously towards a validated target."
            )

        elif current_value > upper:
            status = "Above Range"
            recommendation = (
                "Above the dataset reference band. "
                "Review and adjust cautiously towards a validated target."
            )

        else:
            status = "Within Range"
            recommendation = (
                "Within the dataset reference band. "
                "Continue monitoring."
            )

        results.append({
            "Parameter": parameter,
            "Current Value": current_value,
            "Reference Lower": lower,
            "Reference Upper": upper,
            "Status": status,
            "Recommendation": recommendation
        })

    result_df = pd.DataFrame(results)

    st.divider()
    st.header("Step 4: Recommendation Results")

    if not result_df.empty:

        st.dataframe(
            result_df,
            use_container_width=True,
            hide_index=True
        )

        below = (result_df["Status"] == "Below Range").sum()
        above = (result_df["Status"] == "Above Range").sum()
        within = (result_df["Status"] == "Within Range").sum()

        c1, c2, c3 = st.columns(3)

        c1.metric("Below Range", below)
        c2.metric("Above Range", above)
        c3.metric("Within Range", within)

        csv = result_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download Recommendation Report",
            data=csv,
            file_name="HydroVilla_Recommendations.csv",
            mime="text/csv"
        )

    else:
        st.warning("No reference data available for this selection.")

st.divider()

st.caption(
    "Note: Reference bands are derived from healthy records "
    "in a simulated dataset. They are provisional and require "
    "validation against real-world hydroponic research and measurements."
)
