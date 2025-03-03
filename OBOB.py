import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import plotly.express as px

# Define deviation thresholds for specific equipment
equipment_thresholds = ({
    # 1670
    "1670-PA-02A": {"Driving End Temp": {"min": 50, "max": 60}, "Driven End Temp": {"min": 70, "max": 80},
                "RMS Velocity (mm/s)": {"min": 0, "max": 4}},
    "1670-PA-02B": {"Driving End Temp": {"min": 39, "max": 48}, "Driven End Temp": {"min": 55, "max": 70},
                  "RMS Velocity (mm/s)": {"min": 0, "max": 4.5}},
    "1670-PA-02C": {"Driving End Temp": {"min": 39, "max": 48}, "Driven End Temp": {"min": 55, "max": 70},
                  "RMS Velocity (mm/s)": {"min": 0, "max": 4.5}},
    "1670-PA-04A": {"Driving End Temp": {"min": 41, "max": 52}, "Driven End Temp": {"min": 39, "max": 49},
                  "RMS Velocity (mm/s)": {"min": 0, "max": 4}},
    "1670-PA-04B": {"Driving End Temp": {"min": 41, "max": 52}, "Driven End Temp": {"min": 39, "max": 49},
                  "RMS Velocity (mm/s)": {"min": 0, "max": 4}},
    "1670-PA-04C": {"Driving End Temp": {"min": 29, "max": 40}, "Driven End Temp": {"min": 29, "max": 40},
                "RMS Velocity (mm/s)": {"min": 0, "max": 4.8}},

    # 1600
    "1600-PA-04A": {"Driving End Temp": {"min": 40, "max": 50}, "Driven End Temp": {"min": 40, "max": 68},
                  "RMS Velocity (mm/s)": {"min": 0, "max": 4.8}},
    "1600-PA-04D": {"Driving End Temp": {"min": 40, "max": 50}, "Driven End Temp": {"min": 40, "max": 68},
                  "RMS Velocity (mm/s)": {"min": 0, "max": 4.8}},

# 1680
    "1680-PA-01A": {"Driving End Temp": {"min": 40, "max": 50}, "Driven End Temp": {"min": 40, "max": 60}, "RMS Velocity (mm/s)": {"min": 4.0, "max": 4.2}},
    "1680-PA-01B": {"Driving End Temp": {"min": 40, "max": 50}, "Driven End Temp": {"min": 40, "max": 60}, "RMS Velocity (mm/s)": {"min": 4.0, "max": 4.2}},
    "1680-PH-01A": {"Driving End Temp": {"min": 40, "max": 50}, "Driven End Temp": {"min": 40, "max": 60}, "RMS Velocity (mm/s)": {"min": 4.0, "max": 4.2}},
    "1680-PH-01B": {"Driving End Temp": {"min": 40, "max": 50}, "Driven End Temp": {"min": 40, "max": 60}, "RMS Velocity (mm/s)": {"min": 4.0, "max": 4.2}},
})

# Define the file path at the top of the script
file_path = "data/condition_data.csv"


# Create the directory if it doesn't exist
if not os.path.exists("data"):
    os.makedirs("data")
# Initialize session state variables
if "page" not in st.session_state:
    st.session_state.page = "main"  # Set default page to "main"

def load_data(file_path):
    """Load data from a CSV file."""
    if not os.path.exists(file_path):
        return pd.DataFrame()  # Return an empty DataFrame if file doesn't exist
    return pd.read_csv(file_path)

def validate_columns(df, required_columns):
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        st.error(f"Missing columns in dataset: {', '.join(missing)}")
        return False
    return True

# Add Utility Functions Here
def calculate_kpis(file_path):
    """Calculate KPIs and return data for charts."""
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        st.warning(f"No data file found at {file_path}. Showing default KPI values.")
        return {
            "compliance_rate": "No Data",
            "avg_temp": "No Data",
            "running_percentage": "No Data",
            "data": pd.DataFrame()  # Return an empty DataFrame for charts
        }

    # Load the CSV file
    data = pd.read_csv(file_path)
    if data.empty:
        st.warning("The data file is empty. Showing default KPI values.")
        return {
            "compliance_rate": "No Data",
            "avg_temp": "No Data",
            "running_percentage": "No Data",
            "data": pd.DataFrame()  # Return an empty DataFrame for charts
        }

    # Calculate KPIs
    compliance_rate = data["Is Running"].mean() * 100
    avg_temp = data[["Driving End Temp", "Driven End Temp"]].mean().mean()
    running_percentage = (data["Is Running"].sum() / len(data)) * 100

    # Return KPIs and data
    return {
        "compliance_rate": f"{compliance_rate:.2f}%",
        "avg_temp": f"{avg_temp:.2f}°C",
        "running_percentage": f"{running_percentage:.2f}%",
        "data": data
    }

# Display the logo at the top of the homepage
st.image("indorama_logo.png", use_container_width=True)

# Main Page Functionality
if "page" not in st.session_state:
    st.session_state.page = "main"

if st.session_state.page == "main":
        #Main Page
    st.subheader("Your Gateway to Enhanced Maintenance Efficiency")

    # Greeting Based on Time
    current_hour = datetime.now().hour
    if current_hour < 12:
        greeting = "Good Morning!"
    elif 12 <= current_hour < 18:
        greeting = "Good Afternoon!"
    else:
        greeting = "Good Evening!"

    st.header(greeting)

    # Footer Section
    st.write("---")  # Separator line
    st.write("### 📜 Footer Information")

    st.write("""
                - **Application Version**: 1.0.0  
                - **Developer**: [Nwaoba Kenneth / PE Mechanical]  
                - **Contact Support**: [nwaoba00@gmail.com](mailto:support@yourcompany.com)
                """)

    st.write("""
                This application is designed to improve condition monitoring and maintenance tracking for Indorama Petrochemicals Ltd.
                For assistance or feedback, please reach out via the support link above.
                """)

    # Display KPIs
    st.subheader("Key Performance Indicators (KPIs)")
    kpis = calculate_kpis(file_path)
    col1, col2, col3 = st.columns(3)
    col1.metric("Compliance Rate", kpis["compliance_rate"])
    col2.metric("Average Temperature", kpis["avg_temp"])
    col3.metric("Running Equipment", kpis["running_percentage"])


    # High Priority Dashboard Section
    st.write("---")  # Separator line
    st.subheader("📊 High Priority Equipment Dashboard")

    # Load the data
    data = load_data(file_path)

    if data.empty:
        st.warning("No data available. Please enter condition monitoring data first.")
    else:
        # Filter high-priority equipment
        high_priority_data = data[data["High Priority"] == True]

        if high_priority_data.empty:
            st.info("No equipment is marked as high priority.")
        else:
            # Add date filters for high-priority equipment
            st.write("#### Filter by Date Range")
            start_date = st.date_input("Start Date", value=datetime(2023, 1, 1), key="high_priority_start_date")
            end_date = st.date_input("End Date", value=datetime.now(), key="high_priority_end_date")

            # Filter data by date range
            high_priority_data["Date"] = pd.to_datetime(high_priority_data["Date"], errors="coerce")
            filtered_data = high_priority_data[
                (high_priority_data["Date"] >= pd.Timestamp(start_date)) &
                (high_priority_data["Date"] <= pd.Timestamp(end_date))
                ]

            # Display filtered high-priority equipment
            st.subheader("High Priority Equipment")
            st.dataframe(filtered_data)

            # Downloadable CSV for High Priority Equipment
            st.write("#### Download High Priority Report")
            csv = filtered_data.to_csv(index=False)
            st.download_button("Download as CSV", data=csv, file_name="high_priority_report.csv", mime="text/csv")

    st.write("---")

    # Weekly Report Dashboard
    st.title("Weekly Report Dashboard")

    # Filter by date range
    start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=7),
                               key="weekly_report_start_date")
    end_date = st.date_input("End Date", value=datetime.now(), key="weekly_report_end_date")

    # Load the data
    data = load_data(file_path)

    if data.empty:
        st.warning("No data available. Please enter condition monitoring data first.")
    else:
        # Validate required columns
        required_columns = ["Date", "Equipment", "Driving End Temp", "Driven End Temp", "RMS Velocity (mm/s)",
                            "Oil Level", "Is Running"]
        if not validate_columns(data, required_columns):
            st.error("Dataset does not contain all required columns for analysis.")
        else:
            # Filter data for date range and running equipment
            data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
            filtered_data = data[
                (data["Date"] >= pd.Timestamp(start_date)) &
                (data["Date"] <= pd.Timestamp(end_date)) &
                (data["Is Running"] == True)  # Only include running equipment
                ]

            if filtered_data.empty:
                st.success(
                    "✅ All equipment is operating within thresholds, or no running equipment was found for the selected date range.")
            else:
                # Check for deviations
                deviations = []
                for _, row in filtered_data.iterrows():
                    equipment = row["Equipment"]
                    if equipment in equipment_thresholds:
                        thresholds = equipment_thresholds[equipment]
                        if (
                                not thresholds["Driving End Temp"]["min"] <= row["Driving End Temp"] <=
                                    thresholds["Driving End Temp"]["max"] or
                                not thresholds["Driven End Temp"]["min"] <= row["Driven End Temp"] <=
                                    thresholds["Driven End Temp"]["max"] or
                                not thresholds["RMS Velocity (mm/s)"]["min"] <= row["RMS Velocity (mm/s)"] <=
                                    thresholds["RMS Velocity (mm/s)"]["max"]
                        ):
                            deviations.append(row)

                deviation_data = pd.DataFrame(deviations)

                if deviation_data.empty:
                    st.success(
                        "✅ All running equipment is operating within thresholds for the selected date range.")
                else:
                    st.subheader("⚠️ Running Equipment with Deviations")
                    st.dataframe(deviation_data)

                    # Recommendations
                    st.write("### 🔍 Recommendations")
                    recommendations = []
                    for _, row in deviation_data.iterrows():
                        equipment = row["Equipment"]

                        if not thresholds["Driving End Temp"]["min"] <= row["Driving End Temp"] <= \
                               thresholds["Driving End Temp"]["max"]:
                            recommendations.append(
                                f"🔧 **{equipment}**: Driving End Temp is outside the range {thresholds['Driving End Temp']['min']} - {thresholds['Driving End Temp']['max']} °C.")

                        if not thresholds["Driven End Temp"]["min"] <= row["Driven End Temp"] <= \
                               thresholds["Driven End Temp"]["max"]:
                            recommendations.append(
                                f"🔧 **{equipment}**: Driven End Temp is outside the range {thresholds['Driven End Temp']['min']} - {thresholds['Driven End Temp']['max']} °C.")

                        if not thresholds["RMS Velocity (mm/s)"]["min"] <= row["RMS Velocity (mm/s)"] <= \
                               thresholds["RMS Velocity (mm/s)"]["max"]:
                            recommendations.append(
                                f"📊 **{equipment}**: RMS Velocity is outside the range {thresholds['RMS Velocity (mm/s)']['min']} - {thresholds['RMS Velocity (mm/s)']['max']} mm/s.")

                        if row["Oil Level"] == "Low":
                            recommendations.append(f"🛢️ **{equipment}**: Oil level is low. Consider refilling.")

                    if recommendations:
                        for rec in recommendations:
                            st.info(rec)
                    else:
                        st.success("✅ No immediate issues detected in the deviations data.")

                    # Downloadable Weekly Report
                    st.write("#### Download Weekly Report")
                    csv = deviation_data.to_csv(index=False)
                    st.download_button("Download Report as CSV", data=csv, file_name="weekly_report.csv",
                                       mime="text/csv")

        # Ensure data is available from KPI calculation
    data = kpis["data"]

    if not data.empty:  # Check if the data is available
        st.write("---")
        st.subheader("Running Equipment by Area")

        # Calculate the percentage of running equipment per area
        if "Area" in data.columns and "Is Running" in data.columns:
            running_percentage_by_area = (
                    data.groupby("Area")["Is Running"].mean() * 100
            ).reset_index()
            running_percentage_by_area.rename(
                columns={"Is Running": "Running Percentage (%)"}, inplace=True
            )

            # Display the table
            st.table(running_percentage_by_area)
        else:
            st.warning("The dataset does not contain 'Area' or 'Is Running' columns.")
    else:
        st.warning("No data available to calculate running equipment percentages.")

    # Add KPI Charts
    data = kpis["data"]
    if not data.empty:  # Check if data is available
        st.write("---")
        st.subheader("KPI Charts")

        import plotly.express as px

        # Average Temperature Trend
        if "Driving End Temp" in data.columns and "Driven End Temp" in data.columns:
            # Calculate the average temperature
            data["Avg Temp"] = data[["Driving End Temp", "Driven End Temp"]].mean(axis=1)

            # Aggregate average temperature by date
            avg_temp_trend = data.groupby("Date", as_index=False)["Avg Temp"].mean()

            st.write("### Average Temperature Trend")

            # Create a Plotly line chart
            fig = px.line(
                avg_temp_trend,
                x="Date",
                y="Avg Temp",
                title="Average Temperature Trend Over Time",
                labels={"Avg Temp": "Average Temperature (°C)", "Date": "Date"},
                markers=True,  # Adds markers for each data point
            )

            # Enhance chart aesthetics
            fig.update_traces(line=dict(width=2))
            fig.update_layout(
                title_font_size=18,
                xaxis_title_font_size=14,
                yaxis_title_font_size=14,
                hovermode="x unified",  # Combine hover info
            )

            st.plotly_chart(fig)
        else:
            st.warning("Temperature data (Driving End or Driven End) is missing in the dataset.")


        # Running Equipment Count
        if "Is Running" in data.columns and "Area" in data.columns:
            running_equipment_by_area = data.groupby(["Date", "Area"])["Is Running"].sum().reset_index()
            st.write("### Running Equipment Count by Area")

            # Create the bar chart with Plotly
            fig = px.bar(
                running_equipment_by_area,
                x="Date",
                y="Is Running",
                color="Area",
                title="Running Equipment Count by Area",
                labels={"Is Running": "Running Equipment Count"},
            )
            fig.update_layout(barmode="stack")
            st.plotly_chart(fig)
        else:
            st.warning("The dataset does not contain 'Is Running' or 'Area' columns.")

    else:
        st.warning("No data available for KPI charts.")


    # Next Button to Navigate
    if st.button("Next"):
        st.session_state.page = "monitoring"

elif st.session_state.page == "high_priority_dashboard":
    st.title("High Priority Equipment Dashboard")

    # Load data
    data = load_data(file_path)

    if data.empty:
        st.warning("No data available. Please enter condition monitoring data first.")
    else:
        # Filter high-priority equipment
        high_priority_data = data[data["High Priority"] == True]

        if high_priority_data.empty:
            st.info("No equipment is marked as high priority.")
        else:
            # Add date filters
            start_date = st.date_input("Start Date", value=datetime(2023, 1, 1), key="high_priority_start_date")
            end_date = st.date_input("End Date", value=datetime.now(), key="high_priority_end_date")

            # Filter data by date range
            high_priority_data["Date"] = pd.to_datetime(high_priority_data["Date"])
            filtered_data = high_priority_data[
                (high_priority_data["Date"] >= start_date) &
                (high_priority_data["Date"] <= end_date)
            ]

            st.subheader("High Priority Equipment")
            st.dataframe(filtered_data)

            # Downloadable CSV for High Priority Equipment
            st.write("#### Download High Priority Report")
            csv = filtered_data.to_csv(index=False)
            st.download_button("Download as CSV", data=csv, file_name="high_priority_report.csv", mime="text/csv")

elif st.session_state.page == "monitoring":

    def load_data(file_path):
        """Load data from a CSV file."""
        if not os.path.exists(file_path):
            return pd.DataFrame()  # Return an empty DataFrame if file doesn't exist
        return pd.read_csv(file_path)

    def filter_data(df, equipment, start_date, end_date):
        """Filter data by equipment and date range."""
        df["Date"] = pd.to_datetime(df["Date"])  # Convert Date column to datetime
        filtered_df = df[
            (df["Equipment"] == equipment) &
            (df["Date"] >= pd.to_datetime(start_date)) &
            (df["Date"] <= pd.to_datetime(end_date))
            ]
        return filtered_df

    # Tabs for Condition Monitoring and Report
    tab1, tab2 = st.tabs(["Condition Monitoring", "Report"])

    with tab1:
        st.header("Condition Monitoring Data Entry")

        # Equipment lists for each area
        equipment_lists = {
            "1670": [
                "1670-PA-02A", "1670-PA-02B", "1670-PA-02C", "1670-PA-04A", "1670-PA-04B",
                "1670-PA-04C"
            ],
            "1600": [
                "1600-PA-04A", "1600-PA-04D"
            ],
            "1680": [
                "1680-PA-01A", "1680-PA-01B", "1680-PH-01A", "1680-PH-01B"
            ],
        }

        # Persistent fields
        date = st.date_input("Date", key="date")
        area = st.selectbox("Select Area", options=list(equipment_lists.keys()), key="area")
        equipment_options = equipment_lists.get(area, [])
        equipment = st.selectbox("Select Equipment", options=equipment_options, key="equipment")


        # Tick box for "Is the equipment running?"
        is_running = st.checkbox("Is the equipment running?", key="is_running")

        # Data Entry Fields
        if is_running:
            de_temp = st.number_input("Driving End Temperature (°C)", min_value=0.0, max_value=200.0, step=0.1,
                                      key="de_temp")
            dr_temp = st.number_input("Driven End Temperature (°C)", min_value=0.0, max_value=200.0, step=0.1,
                                      key="dr_temp")
            oil_level = st.selectbox("Oil Level", ["Normal", "Low", "High"], key="oil_level")
            abnormal_sound = st.selectbox("Abnormal Sound", ["No", "Yes"], key="abnormal_sound")
            leakage = st.selectbox("Leakage", ["No", "Yes"], key="leakage")
            observation = st.text_area("Observations", key="observation")

            # Vibration Monitoring
            st.subheader("Vibration Monitoring")
            vibration_rms_velocity = st.number_input("RMS Velocity (mm/s)", min_value=0.0, max_value=100.0, step=0.1,
                                                     key="vibration_rms_velocity")
            vibration_peak_acceleration = st.number_input("Peak Acceleration (g)", min_value=0.0, max_value=10.0,
                                                          step=0.1,
                                                          key="vibration_peak_acceleration")
            vibration_displacement = st.number_input("Displacement (µm)", min_value=0.0, max_value=1000.0, step=0.1,
                                                     key="vibration_displacement")

            # Add a checkbox for marking equipment as high priority
            high_priority = st.checkbox("Mark as High Priority", key="high_priority")

            # Gearbox Inputs
            gearbox = st.checkbox("Does the equipment have a gearbox?", key="gearbox")
            if gearbox:
                gearbox_temp = st.number_input("Gearbox Temperature (°C)", min_value=0.0, max_value=200.0, step=0.1,
                                               key="gearbox_temp")
                gearbox_oil = st.selectbox("Gearbox Oil Level", ["Normal", "Low", "High"], key="gearbox_oil")
                gearbox_leakage = st.selectbox("Gearbox Leakage", ["No", "Yes"], key="gearbox_leakage")
                gearbox_abnormal_sound = st.selectbox("Gearbox Abnormal Sound", ["No", "Yes"], key="gearbox_abnormal_sound")
                # Vibration Monitoring for gearbox
                st.subheader("Gearbox_Vibration Monitoring")
                gearbox_vibration_rms_velocity = st.number_input("Gearbox RMS Velocity (mm/s)", min_value=0.0, max_value=100.0,
                                                         step=0.1,
                                                         key="gearbox_vibration_rms_velocity")
                gearbox_vibration_peak_acceleration = st.number_input("Gearbox Peak Acceleration (g)", min_value=0.0, max_value=10.0,
                                                              step=0.1,
                                                              key="gearbox_vibration_peak_acceleration")
                gearbox_vibration_displacement = st.number_input("Gearbox Displacement (µm)", min_value=0.0, max_value=1000.0, step=0.1,
                                                         key="gearbox_vibration_displacement")

        # Submit Button
        if st.button("Submit Data"):
            try:
                # Check if essential fields are filled (add your required fields here)
                if not date or not area or not equipment:
                    st.error("Please fill in all required fields before submitting.")
                elif is_running and ("de_temp" not in st.session_state or "dr_temp" not in st.session_state):
                    st.error("Please provide temperature values if the equipment is running.")
                else:
                    # Prepare data
                    if not is_running:
                        # If equipment is not running, set all numeric fields to 0 and strings to 'N/A'
                        data = {
                            "Date": [date],
                            "Area": [area],
                            "Equipment": [equipment],
                            "Is Running": [False],
                            "High Priority": [False],
                            "Driving End Temp": [0.0],
                            "Driven End Temp": [0.0],
                            "Oil Level": ["N/A"],
                            "Abnormal Sound": ["N/A"],
                            "Leakage": ["N/A"],
                            "Observation": ["Not Running"],
                            "RMS Velocity (mm/s)": [0.0],
                            "Peak Acceleration (g)": [0.0],
                            "Displacement (µm)": [0.0],
                            "Gearbox Temp": [0.0],
                            "Gearbox Oil Level": ["N/A"],
                            "Gearbox Leakage": ["N/A"],
                            "Gearbox Abnormal Sound": ["N/A"],
                            "Gearbox RMS Velocity (mm/s)": [0.0],
                            "Gearbox Peak Acceleration (g)": [0.0],
                            "Gearbox Displacement (µm)": [0.0],
                        }

                    else:
                        # If equipment is running, save entered values
                        data = {
                            "Date": [date],
                            "Area": [area],
                            "Equipment": [equipment],
                            "Is Running": [True],
                            "High Priority": [high_priority],
                            "Driving End Temp": [st.session_state.de_temp],
                            "Driven End Temp": [st.session_state.dr_temp],
                            "Oil Level": [st.session_state.oil_level],
                            "Abnormal Sound": [st.session_state.abnormal_sound],
                            "Leakage": [st.session_state.leakage],
                            "Observation": [st.session_state.observation],
                            "RMS Velocity (mm/s)": [st.session_state.vibration_rms_velocity],
                            "Peak Acceleration (g)": [st.session_state.vibration_peak_acceleration],
                            "Displacement (µm)": [st.session_state.vibration_displacement],
                            "Gearbox Temp": [
                                st.session_state.gearbox_temp if "gearbox_temp" in st.session_state else 0.0],
                            "Gearbox Oil Level": [
                                st.session_state.gearbox_oil if "gearbox_oil" in st.session_state else "N/A"],
                            "Gearbox Leakage": [
                                st.session_state.gearbox_leakage if "gearbox_leakage" in st.session_state else "N/A"],
                            "Gearbox Abnormal Sound": [
                                st.session_state.gearbox_leakage if "gearbox_abnormal_sound" in st.session_state else "N/A"]
                        }

                    # Save to CSV
                    df = pd.DataFrame(data)
                    file_path = "data/condition_data.csv"
                    if not os.path.exists("data"):
                        os.makedirs("data")
                    if os.path.exists(file_path):
                        df.to_csv(file_path, mode="a", header=False, index=False)
                    else:
                        df.to_csv(file_path, index=False)

                    st.success("Data Submitted Successfully!")

            except Exception as e:
                st.error(f"An error occurred: {e}")

    # Tab 2: Reports and Visualizations
    with tab2:
        st.header("Reports and Visualization")
        file_path = "data/condition_data.csv"

        # Load data
        data = load_data(file_path)

        if data.empty:
            st.warning("No data available. Please enter condition monitoring data first.")
        else:
            st.write("### Full Data")
            st.dataframe(data)

            # Check if 'Equipment' column exists
            if "Equipment" not in data.columns:
                st.error("The 'Equipment' column is missing. Please check the data file.")
            else:
                # Combine all equipment into a single list
                all_equipment = [equipment for area in equipment_lists.values() for equipment in area]

                # Dropdown for Equipment Selection
                selected_equipment = st.selectbox("Select Equipment", options=all_equipment)

                # Date Range Inputs
                start_date = st.date_input("Start Date", value=datetime(2023, 1, 1))
                end_date = st.date_input("End Date", value=datetime.now())

                if start_date > end_date:
                    st.error("Start date cannot be later than end date.")
                else:
                    # Filter data for the selected equipment and date range
                    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
                    data = data.dropna(subset=["Date"])  # Remove invalid dates
                    filtered_data = data[
                        (data["Equipment"] == selected_equipment) &
                        (data["Date"] >= pd.to_datetime(start_date)) &
                        (data["Date"] <= pd.to_datetime(end_date))
                        ]

                    # Check if filtered data is empty
                    if filtered_data.empty:
                        st.warning(f"No data found for {selected_equipment} between {start_date} and {end_date}.")
                        st.write(f"### {selected_equipment} Report")
                        st.write("The equipment hasn't been running during the selected date range.")
                    else:
                        st.write(f"### Filtered Data for {selected_equipment}")
                        st.dataframe(filtered_data)

                        # Visualizations
                        st.subheader("Data Visualizations")

                        # Allow user to choose the dataset for visualization
                        data_option = st.radio(
                            "Select data for visualization:",
                            options=["General Table (All Data)", "Filtered Table"],
                            key="data_option"
                        )

                        # Select appropriate dataset based on user choice
                        if data_option == "General Table (All Data)":
                            visualization_data = data  # Use the full dataset
                            st.write("Using data from the general table (all records).")
                        else:
                            visualization_data = filtered_data  # Use the filtered dataset
                            st.write("Using data from the filtered table.")

                        # Driving and Driven End Temperature Trend
                        if "Driving End Temp" in visualization_data.columns and "Driven End Temp" in visualization_data.columns:
                            st.write("#### Driving and Driven End Temperature Trend for Equipment")
                            temp_chart_data = visualization_data[["Date", "Driving End Temp", "Driven End Temp"]].melt(
                                id_vars="Date",
                                var_name="Temperature Type",
                                value_name="Temperature")
                            fig = px.line(
                                temp_chart_data,
                                x="Date",
                                y="Temperature",
                                color="Temperature Type",
                                title="Driving and Driven End Temperature Trend",
                                labels={"Temperature": "Temperature (°C)"}
                            )
                            st.plotly_chart(fig)
                        else:
                            st.warning(
                                "Temperature data (Driving End or Driven End) is missing in the selected dataset.")

                        # Equipment Vibration Trend
                        if "RMS Velocity (mm/s)" in visualization_data.columns and "Peak Acceleration (g)" in visualization_data.columns and "Displacement (µm)" in visualization_data.columns:
                            st.write("#### Vibration Trend for Equipment")
                            vibration_chart_data = visualization_data[
                                ["Date", "RMS Velocity (mm/s)", "Peak Acceleration (g)", "Displacement (µm)"]].melt(
                                id_vars="Date",
                                var_name="Vibration Type",
                                value_name="Value")
                            fig = px.line(
                                vibration_chart_data,
                                x="Date",
                                y="Value",
                                color="Vibration Type",
                                title="Vibration Trend for Equipment",
                                labels={"Value": "Value"}
                            )
                            st.plotly_chart(fig)
                        else:
                            st.warning("Vibration data is missing in the selected dataset.")

                        # Driving and Driven End Temperature Trend for Gearbox
                        if "Gearbox Temp" in visualization_data.columns:
                            st.write("#### Gearbox Temperature Trend")
                            fig = px.line(
                                visualization_data,
                                x="Date",
                                y="Gearbox Temp",
                                title="Gearbox Temperature Trend",
                                labels={"Gearbox Temp": "Temperature (°C)"}
                            )
                            st.plotly_chart(fig)
                        else:
                            st.warning("Gearbox Temperature data is missing in the selected dataset.")

                        # Equipment Vibration Trend for Gearbox
                        if "Gearbox RMS Velocity (mm/s)" in visualization_data.columns and "Gearbox Peak Acceleration (g)" in visualization_data.columns and "Gearbox Displacement (µm)" in visualization_data.columns:
                            st.write("#### Vibration Trend for Gearbox")
                            gearbox_vibration_chart_data = visualization_data[
                                ["Date", "Gearbox RMS Velocity (mm/s)", "Gearbox Peak Acceleration (g)",
                                 "Gearbox Displacement (µm)"]].melt(id_vars="Date",
                                                                    var_name="Vibration Type",
                                                                    value_name="Value")
                            fig = px.line(
                                gearbox_vibration_chart_data,
                                x="Date",
                                y="Value",
                                color="Vibration Type",
                                title="Vibration Trend for Gearbox",
                                labels={"Value": "Value"}
                            )
                            st.plotly_chart(fig)
                        else:
                            st.warning("Gearbox Vibration data is missing in the selected dataset.")

                        # Oil Level Distribution for Equipment
                        if "Oil Level" in visualization_data.columns:
                            st.write("#### Oil Level Distribution for Equipment")
                            oil_summary = visualization_data["Oil Level"].value_counts().reset_index()
                            oil_summary.columns = ["Oil Level", "Count"]
                            fig = px.bar(
                                oil_summary,
                                x="Oil Level",
                                y="Count",
                                title="Oil Level Distribution for Equipment",
                                labels={"Count": "Number of Records"}
                            )
                            st.plotly_chart(fig)
                        else:
                            st.warning("Oil Level data is missing in the selected dataset.")

                        # Oil Level Distribution for Gearbox
                        if "Gearbox Oil Level" in visualization_data.columns:
                            st.write("#### Oil Level Distribution for Gearbox")

                            # Check for missing or null values
                            if visualization_data["Gearbox Oil Level"].notna().any():
                                # Create a summary of Gearbox Oil Level distribution
                                gearbox_oil_summary = visualization_data[
                                    "Gearbox Oil Level"].value_counts().reset_index()
                                gearbox_oil_summary.columns = ["Gearbox Oil Level", "Count"]

                                # Create the bar chart
                                fig = px.bar(
                                    gearbox_oil_summary,
                                    x="Gearbox Oil Level",
                                    y="Count",
                                    title="Oil Level Distribution for Gearbox",
                                    labels={"Count": "Number of Records"}
                                )
                                st.plotly_chart(fig)
                            else:
                                st.warning("No valid Gearbox Oil Level data available in the selected dataset.")
                        else:
                            st.warning("Gearbox Oil Level data is missing in the selected dataset.")

# Add Back Button
if st.button("Back to Home"):
    st.session_state.page = "main"