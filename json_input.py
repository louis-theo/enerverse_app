import streamlit as st
import json
import pandas as pd

def calculate_baseline_emissions(data):
    # Extract Be Lean, Be Clean, Be Green sections from JSON data
    be_lean_data = data.get("Be Lean", [])
    be_clean_data = data.get("Be Clean", [])
    be_green_data = data.get("Be Green", [])
    total_baseline_emissions = 0
    total_emissions_after_demand_reduction = 0
    total_emissions_after_heat_network = 0
    total_emissions_after_renewable_energy = 0

    for dwelling in be_lean_data:
        try:
            # Extract relevant values from Be Lean
            ter = float(dwelling.get("TER", 0))
            der = float(dwelling.get("DER", 0))
            floor_area = float(dwelling.get("Total Floor Area", 0))
            plot_reference = dwelling.get("Plot Reference", "Unknown Plot")

            # Calculate baseline emissions for the dwelling
            baseline_emissions = (ter * floor_area) / 1000  # Convert kg CO2 to tonnes CO2
            total_baseline_emissions += baseline_emissions

            # Calculate emissions after energy demand reduction for the dwelling
            emissions_after_demand_reduction = (der * floor_area) / 1000  # Convert kg CO2 to tonnes CO2
            total_emissions_after_demand_reduction += emissions_after_demand_reduction

            # Find corresponding Be Clean dwelling using Plot Reference
            be_clean_dwelling = next((d for d in be_clean_data if d.get("Plot Reference") == plot_reference), None)
            be_clean_der = float(be_clean_dwelling.get("DER", 0)) if be_clean_dwelling else 0

            # Calculate emissions after heat network/CHP for the dwelling
            emissions_after_heat_network = (be_clean_der * floor_area) / 1000  # Convert kg CO2 to tonnes CO2
            total_emissions_after_heat_network += emissions_after_heat_network

            # Find corresponding Be Green dwelling using Plot Reference
            be_green_dwelling = next((d for d in be_green_data if d.get("Plot Reference") == plot_reference), None)
            be_green_der = float(be_green_dwelling.get("DER", 0)) if be_green_dwelling else 0

            # Calculate emissions after renewable energy for the dwelling
            emissions_after_renewable_energy = (be_green_der * floor_area) / 1000  # Convert kg CO2 to tonnes CO2
            total_emissions_after_renewable_energy += emissions_after_renewable_energy

        except ValueError:
            pass

    # Calculate regulated carbon dioxide savings in tonnes of CO2 per annum
    be_lean_savings = total_baseline_emissions - total_emissions_after_demand_reduction
    be_clean_savings = total_emissions_after_demand_reduction - total_emissions_after_heat_network
    be_green_savings = total_emissions_after_heat_network - total_emissions_after_renewable_energy

    # Calculate percentage savings
    be_lean_percentage_savings = (be_lean_savings / total_baseline_emissions) * 100 if total_baseline_emissions else 0
    be_clean_percentage_savings = (be_clean_savings / total_baseline_emissions) * 100 if total_baseline_emissions else 0
    be_green_percentage_savings = (be_green_savings / total_baseline_emissions) * 100 if total_baseline_emissions else 0

    # Return totals and savings
    return (total_baseline_emissions, total_emissions_after_demand_reduction, total_emissions_after_heat_network, 
            total_emissions_after_renewable_energy, be_lean_savings, be_clean_savings, be_green_savings, 
            be_lean_percentage_savings, be_clean_percentage_savings, be_green_percentage_savings)

# Streamlit UI
st.title("Carbon Dioxide Emissions Calculator for Domestic Buildings")

uploaded_file = st.file_uploader("Upload JSON file", type=["json"])

if uploaded_file is not None:
    data = json.load(uploaded_file)
    (total_baseline, total_demand_reduction, total_heat_network, total_renewable,
     be_lean_savings, be_clean_savings, be_green_savings,
     be_lean_percentage_savings, be_clean_percentage_savings, be_green_percentage_savings) = calculate_baseline_emissions(data)

    # Prepare data for the tables
    emissions_data = {
        "Stage": ["Baseline", "After Energy Demand Reduction", "After Heat Network/CHP", "After Renewable Energy"],
        "Tonnes CO2 per annum": [total_baseline, total_demand_reduction, total_heat_network, total_renewable]
    }

    savings_data = {
        "Stage": ["Savings from Energy Demand Reduction", "Savings from Heat Network/CHP", "Savings from Renewable Energy"],
        "Tonnes CO2 per annum": [be_lean_savings, be_clean_savings, be_green_savings],
        "Percentage Savings (%)": [be_lean_percentage_savings, be_clean_percentage_savings, be_green_percentage_savings]
    }

    # Convert data to DataFrame for better display
    emissions_df = pd.DataFrame(emissions_data)
    savings_df = pd.DataFrame(savings_data)

    # Display tables
    st.subheader("Carbon Dioxide Emissions for Domestic Buildings (tonnes CO2 per annum)")
    st.table(emissions_df)

    st.subheader("Regulated Domestic Carbon Dioxide Savings")
    st.table(savings_df)

    # Display total emissions
    st.subheader("Total Emissions for All Dwellings")
    st.write(f"Total Baseline Emissions: {total_baseline:.4f} tCO2/year")
    st.write(f"Total Emissions After Demand Reduction: {total_demand_reduction:.4f} tCO2/year")
    st.write(f"Total Emissions After Heat Network/CHP: {total_heat_network:.4f} tCO2/year")
    st.write(f"Total Emissions After Renewable Energy: {total_renewable:.4f} tCO2/year")
