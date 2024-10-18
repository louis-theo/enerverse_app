import streamlit as st
import pandas as pd

def calculate_baseline_emissions(num_dwellings):
    total_baseline_emissions = 0
    total_emissions_after_demand_reduction = 0
    total_emissions_after_heat_network = 0
    total_emissions_after_renewable_energy = 0

    for i in range(num_dwellings):
        st.subheader(f"Enter data for dwelling {i + 1}")
        try:
            # Get user inputs
            plot_reference = st.text_input(f"Plot Reference for Dwelling {i + 1}", key=f"plot_{i}")
            ter = st.number_input(f"Target Emission Rate (TER) for Dwelling {i + 1} (kg CO2/m²/year)", min_value=0.0, step=0.01, key=f"ter_{i}")
            der = st.number_input(f"Dwelling Emission Rate after Be Lean (DER) for Dwelling {i + 1} (kg CO2/m²/year)", min_value=0.0, step=0.01, key=f"der_{i}")
            be_clean_der = st.number_input(f"Dwelling Emission Rate after Be Clean (DER) for Dwelling {i + 1} (kg CO2/m²/year)", min_value=0.0, step=0.01, key=f"be_clean_der_{i}")
            be_green_der = st.number_input(f"Dwelling Emission Rate after Be Green (DER) for Dwelling {i + 1} (kg CO2/m²/year)", min_value=0.0, step=0.01, key=f"be_green_der_{i}")
            floor_area = st.number_input(f"Total Floor Area for Dwelling {i + 1} (m²)", min_value=0.0, step=0.1, key=f"floor_area_{i}")

            # Calculate baseline emissions for the dwelling
            baseline_emissions = (ter * floor_area) / 1000  # Convert kg CO2 to tonnes CO2
            total_baseline_emissions += baseline_emissions

            # Calculate emissions after energy demand reduction for the dwelling
            emissions_after_demand_reduction = (der * floor_area) / 1000  # Convert kg CO2 to tonnes CO2
            total_emissions_after_demand_reduction += emissions_after_demand_reduction

            # Calculate emissions after heat network/CHP for the dwelling
            emissions_after_heat_network = (be_clean_der * floor_area) / 1000  # Convert kg CO2 to tonnes CO2
            total_emissions_after_heat_network += emissions_after_heat_network

            # Calculate emissions after renewable energy for the dwelling
            emissions_after_renewable_energy = (be_green_der * floor_area) / 1000  # Convert kg CO2 to tonnes CO2
            total_emissions_after_renewable_energy += emissions_after_renewable_energy

        except ValueError:
            st.error(f"Invalid numerical value entered for dwelling {i + 1}")

    # Calculate regulated carbon dioxide savings in tonnes of CO2 per annum
    be_lean_savings = total_baseline_emissions - total_emissions_after_demand_reduction
    be_clean_savings = total_emissions_after_demand_reduction - total_emissions_after_heat_network
    be_green_savings = total_emissions_after_heat_network - total_emissions_after_renewable_energy

    # Calculate percentage savings
    be_lean_percentage_savings = (be_lean_savings / total_baseline_emissions) * 100 if total_baseline_emissions else 0
    be_clean_percentage_savings = (be_clean_savings / total_baseline_emissions) * 100 if total_baseline_emissions else 0
    be_green_percentage_savings = (be_green_savings / total_baseline_emissions) * 100 if total_baseline_emissions else 0

    # Calculate cumulative on-site savings
    cumulative_on_site_savings = be_lean_savings + be_clean_savings + be_green_savings

    # Calculate shortfall from zero carbon
    shortfall_from_zero_carbon = total_baseline_emissions - cumulative_on_site_savings

    # Return totals and savings
    return (total_baseline_emissions, total_emissions_after_demand_reduction, total_emissions_after_heat_network, 
            total_emissions_after_renewable_energy, be_lean_savings, be_clean_savings, be_green_savings, 
            be_lean_percentage_savings, be_clean_percentage_savings, be_green_percentage_savings, 
            cumulative_on_site_savings, shortfall_from_zero_carbon)

# Streamlit UI
st.title("Carbon Dioxide Emissions Calculator for Domestic Buildings")

num_dwellings = st.number_input("Enter the number of dwellings", min_value=1, step=1)

if num_dwellings > 0:
    (total_baseline, total_demand_reduction, total_heat_network, total_renewable,
     be_lean_savings, be_clean_savings, be_green_savings,
     be_lean_percentage_savings, be_clean_percentage_savings, be_green_percentage_savings,
     cumulative_on_site_savings, shortfall_from_zero_carbon) = calculate_baseline_emissions(num_dwellings)

    # Prepare data for the tables
    emissions_data = {
        "Stage": ["Baseline", "After Energy Demand Reduction", "After Heat Network/CHP", "After Renewable Energy"],
        "Tonnes CO2 per annum": [total_baseline, total_demand_reduction, total_heat_network, total_renewable]
    }

    savings_data = {
        "Stage": ["Savings from Energy Demand Reduction", "Savings from Heat Network/CHP", "Savings from Renewable Energy", "Cumulative On-Site Savings", "Shortfall from Zero Carbon"],
        "Tonnes CO2 per annum": [be_lean_savings, be_clean_savings, be_green_savings, cumulative_on_site_savings, shortfall_from_zero_carbon],
        "Percentage Savings (%)": [be_lean_percentage_savings, be_clean_percentage_savings, be_green_percentage_savings, "N/A", "N/A"]
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
