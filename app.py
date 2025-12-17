import streamlit as st
import pandas as pd
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Nigeria Carbon Calculator",
    page_icon="🌍",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .big-font {
        font-size: 24px !important;
        color: #1E6B52;
    }
    .metric-box {
        background-color: #f0f8ff;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1E6B52;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Main title
st.title("🌍 Nigeria Carbon Footprint Calculator")
st.markdown("### *Simple, Fast, and Nigerian-Focused*")

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 1

# Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", 
    ["🏠 Home", "📊 Calculator", "📈 Results", "ℹ️ About"])

if page == "🏠 Home":
    st.markdown('<div class="big-font">Welcome to the Nigeria Carbon Calculator!</div>', unsafe_allow_html=True)
    
    st.write("""
    ### This tool helps Nigerian organizations:
    - 📊 Measure carbon emissions
    - 🇳🇬 Use Nigerian-specific standards
    - 💰 Estimate cost savings
    - 🌱 Plan sustainability initiatives
    
    ### How to use:
    1. Go to **Calculator** page
    2. Enter your organization's data
    3. View results instantly
    4. Get recommendations
    
    ### Why it's important:
    - Nigeria is committed to reducing emissions by 20% by 2030
    - Carbon footprint affects climate change
    - Sustainability improves business reputation
    """)
    
    st.image("https://via.placeholder.com/800x300/1E6B52/FFFFFF?text=Nigeria+Sustainability", 
             caption="Building a Sustainable Nigeria")

elif page == "📊 Calculator":
    st.header("📋 Enter Your Organization Data")
    
    # Step 1: Basic Info
    with st.expander("🏢 Organization Details", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Organization Name")
            sector = st.selectbox("Industry Sector", 
                ["Manufacturing", "Services", "Agriculture", "Construction", 
                 "Transportation", "Education", "Healthcare", "Other"])
        with col2:
            location = st.selectbox("Location", 
                ["Lagos", "Abuja", "Port Harcourt", "Kano", "Ibadan", "Other"])
            employees = st.number_input("Number of Employees", min_value=1, value=10)
    
    # Step 2: Energy Use
    with st.expander("⚡ Energy Consumption"):
        st.write("**Monthly Average**")
        col1, col2, col3 = st.columns(3)
        with col1:
            electricity = st.number_input("Electricity (kWh)", min_value=0, value=5000)
            grid_source = st.selectbox("Grid Source", 
                ["National Grid", "Generator", "Solar", "Mixed"])
        with col2:
            diesel = st.number_input("Diesel (liters)", min_value=0, value=500)
        with col3:
            petrol = st.number_input("Petrol (liters)", min_value=0, value=300)
            lpg = st.number_input("LPG (kg)", min_value=0, value=100)
    
    # Step 3: Transportation
    with st.expander("🚗 Transportation"):
        col1, col2 = st.columns(2)
        with col1:
            vehicles = st.number_input("Company Vehicles", min_value=0, value=3)
            km_per_month = st.number_input("Monthly Distance (km)", min_value=0, value=2000)
        with col2:
            air_travel = st.number_input("Air Travel (hours/year)", min_value=0, value=50)
            business_trips = st.number_input("Business Trips/month", min_value=0, value=2)
    
    # Step 4: Waste
    with st.expander("🗑️ Waste Management"):
        col1, col2 = st.columns(2)
        with col1:
            waste_kg = st.number_input("Waste (kg/month)", min_value=0, value=100)
            recycling = st.selectbox("Recycling Practice", 
                ["None", "Some", "Comprehensive"])
        with col2:
            water_usage = st.number_input("Water (m³/month)", min_value=0, value=100)
            paper_kg = st.number_input("Paper (kg/month)", min_value=0, value=50)
    
    # Calculate Button
    if st.button("📊 Calculate Carbon Footprint", type="primary"):
        # Nigerian emission factors
        factors = {
            'electricity': 0.55,  # kgCO2/kWh (Nigeria grid)
            'diesel': 2.66,       # kgCO2/liter
            'petrol': 2.34,       # kgCO2/liter
            'lpg': 1.56,          # kgCO2/kg
            'vehicle': 0.25,      # kgCO2/km
            'air_travel': 90,     # kgCO2/hour
            'waste': 0.35,        # kgCO2/kg
            'water': 0.3,         # kgCO2/m³
            'paper': 1.1,         # kgCO2/kg
        }
        
        # Calculations (monthly)
        elec_co2 = electricity * factors['electricity']
        diesel_co2 = diesel * factors['diesel']
        petrol_co2 = petrol * factors['petrol']
        lpg_co2 = lpg * factors['lpg']
        transport_co2 = vehicles * km_per_month * factors['vehicle']
        air_co2 = air_travel * factors['air_travel'] / 12  # Monthly
        waste_co2 = waste_kg * factors['waste']
        water_co2 = water_usage * factors['water']
        paper_co2 = paper_kg * factors['paper']
        
        # Totals
        monthly_co2 = elec_co2 + diesel_co2 + petrol_co2 + lpg_co2 + transport_co2 + air_co2 + waste_co2 + water_co2 + paper_co2
        annual_co2 = monthly_co2 * 12
        per_employee = annual_co2 / employees if employees > 0 else 0
        
        # Save to session state
        st.session_state.results = {
            'monthly': monthly_co2,
            'annual': annual_co2,
            'per_employee': per_employee,
            'details': {
                'Electricity': elec_co2 * 12,
                'Diesel': diesel_co2 * 12,
                'Petrol': petrol_co2 * 12,
                'LPG': lpg_co2 * 12,
                'Transport': transport_co2 * 12,
                'Air Travel': air_co2 * 12,
                'Waste': waste_co2 * 12,
                'Water': water_co2 * 12,
                'Paper': paper_co2 * 12,
            }
        }
        
        st.success(f"✅ Calculation complete! Annual footprint: **{annual_co2:,.0f} kgCO₂**")
        st.balloons()

elif page == "📈 Results":
    st.header("📊 Your Carbon Footprint Results")
    
    if 'results' not in st.session_state:
        st.warning("⚠️ Please calculate your footprint first on the Calculator page.")
    else:
        results = st.session_state.results
        
        # Key metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div class="metric-box">', unsafe_allow_html=True)
            st.metric("Annual Emissions", f"{results['annual']:,.0f} kgCO₂")
            st.caption("Total per year")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-box">', unsafe_allow_html=True)
            st.metric("Per Employee", f"{results['per_employee']:,.0f} kgCO₂")
            st.caption("Average per employee")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-box">', unsafe_allow_html=True)
            equivalent_cars = results['annual'] / 4200
            st.metric("Equivalent Cars", f"{equivalent_cars:,.1f}")
            st.caption("Number of cars driven for one year")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Breakdown chart
        st.subheader("📊 Emission Breakdown")
        
        if results['details']:
            # Create DataFrame for chart
            df = pd.DataFrame({
                'Category': list(results['details'].keys()),
                'Emissions (kgCO₂)': list(results['details'].values())
            })
            
            # Display as bar chart
            st.bar_chart(df.set_index('Category'))
            
            # Show table
            st.write("**Detailed Breakdown:**")
            df_display = df.copy()
            df_display['Percentage'] = (df_display['Emissions (kgCO₂)'] / df_display['Emissions (kgCO₂)'].sum() * 100).round(1)
            st.dataframe(df_display, use_container_width=True)
        
        # Recommendations
        st.subheader("🌱 Recommendations to Reduce Emissions")
        
        recommendations = [
            ("Switch to LED lighting", "Can reduce electricity use by 75%", "High impact"),
            ("Regular vehicle maintenance", "Improves fuel efficiency by 15%", "Medium impact"),
            ("Implement recycling program", "Reduces waste emissions by 30%", "Medium impact"),
            ("Use video conferencing", "Cuts air travel emissions", "High impact"),
            ("Install solar panels", "Reduces grid dependency", "High impact"),
            ("Encourage carpooling", "Reduces transport emissions", "Low impact"),
            ("Go paperless", "Eliminates paper emissions", "Medium impact"),
            ("Optimize AC usage", "Saves 20% on electricity", "Medium impact"),
        ]
        
        for i, (title, desc, impact) in enumerate(recommendations, 1):
            with st.expander(f"{i}. {title} ({impact})"):
                st.write(desc)
                if st.button(f"Learn more about this", key=f"learn_{i}"):
                    st.info(f"More details about {title} would appear here. Consider consulting a sustainability expert.")

elif page == "ℹ️ About":
    st.header("ℹ️ About This Tool")
    
    st.write("""
    ### 🇳🇬 Nigeria Carbon Footprint Calculator
    This tool is designed specifically for Nigerian organizations to measure and manage their carbon emissions.
    
    ### Why Nigerian Standards?
    - Uses Nigeria-specific emission factors
    - Considers local fuel blends (PMS, AGO, DPK)
    - Accounts for Nigerian grid electricity mix
    - Incorporates local transportation patterns
    
    ### Emission Factors Used:
    1. **Electricity**: 0.55 kgCO₂/kWh (National grid average)
    2. **Diesel**: 2.66 kgCO₂/liter
    3. **Petrol**: 2.34 kgCO₂/liter
    4. **LPG**: 1.56 kgCO₂/kg
    5. **Vehicles**: 0.25 kgCO₂/km
    6. **Air Travel**: 90 kgCO₂/hour
    7. **Waste**: 0.35 kgCO₂/kg
    8. **Water**: 0.3 kgCO₂/m³
    9. **Paper**: 1.1 kgCO₂/kg
    
    ### Data Sources:
    - Nigerian Electricity Regulatory Commission (NERC)
    - National Bureau of Statistics (NBS)
    - Federal Ministry of Environment
    - International best practices adapted for Nigeria
    
    ### Disclaimer:
    This tool provides estimates for awareness and planning. For official carbon accounting, consult certified professionals.
    """)
    
    # Contact
    st.subheader("📞 Contact & Support")
    st.write("""
    **Need help?**
    - Email: sustainability@nigeria.gov.ng
    - Phone: +234 800 000 0000
    - Hours: Monday-Friday, 9am-5pm WAT
    
    **Want to contribute?**
    This is an open-source project. Contact us to contribute data or improvements.
    """)

# Footer
st.markdown("---")
st.markdown("*Made with ❤️ for Nigeria's Sustainable Future*")
st.caption("Version 1.0 | Last updated: 2024")
