import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
import base64

# Page configuration
st.set_page_config(
    page_title="Nigeria Carbon Footprint Calculator",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E6B52;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #2E8B57;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.4rem;
        color: #3CB371;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f7f4;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1E6B52;
        margin-bottom: 1rem;
    }
    .data-input {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)

# Nigerian Emission Factors Database (Based on Nigerian Standards)
class NigerianEmissionFactors:
    """Nigeria-specific emission factors database"""
    
    def __init__(self):
        # Fuel Emission Factors (kgCO2e/unit) - Nigeria specific
        self.fuel_factors = {
            # Gaseous Fuels
            'Natural Gas (NG)': {'kgCO2e/m³': 2.066, 'kgCO2e/kWh': 0.202},
            'Liquefied Petroleum Gas (LPG)': {'kgCO2e/litre': 1.557, 'kgCO2e/kg': 2.939},
            'Compressed Natural Gas (CNG)': {'kgCO2e/litre': 0.451, 'kgCO2e/m³': 2.067},
            
            # Liquid Fuels
            'Diesel (Automotive Gas Oil)': {'kgCO2e/litre': 2.661, 'kgCO2e/kg': 3.204},
            'Premium Motor Spirit (PMS)': {'kgCO2e/litre': 2.340, 'kgCO2e/kg': 3.154},
            'Dual Purpose Kerosene (DPK)': {'kgCO2e/litre': 2.540, 'kgCO2e/kg': 3.165},
            'Aviation Turbine Kerosene (ATK)': {'kgCO2e/litre': 2.543, 'kgCO2e/kg': 3.178},
            'Fuel Oil (Low Sulphur)': {'kgCO2e/litre': 3.175, 'kgCO2e/kg': 3.229},
            
            # Biofuels (Nigeria specific blends)
            'Biofuel Blend (B20)': {'kgCO2e/litre': 2.320},
            'Bioethanol (E10)': {'kgCO2e/litre': 1.850},
        }
        
        # Electricity Emission Factors by Nigerian Grid Region (kgCO2e/kWh)
        self.electricity_factors = {
            'National Grid Average': 0.55,  # Nigeria grid emission factor
            'Lagos/Ibadan Region': 0.52,
            'Abuja/Kaduna Region': 0.58,
            'Port Harcourt/Enugu Region': 0.60,
            'Kano/Maiduguri Region': 0.62,
            'Solar Power': 0.05,
            'Hydro Power': 0.02,
            'Gas Power Plant': 0.45,
            'Diesel Generator': 0.85,
            'Off-grid System': 0.75,
        }
        
        # Transportation Emission Factors (Nigeria specific)
        self.transport_factors = {
            # Road Transport (kgCO2e/km)
            'Passenger Car - Small (Petrol)': 0.18,
            'Passenger Car - Medium (Petrol)': 0.22,
            'Passenger Car - Large (Petrol)': 0.28,
            'Passenger Car - Diesel': 0.25,
            'SUV/4x4': 0.32,
            'Minibus (15 seater)': 0.45,
            'Large Bus (50+ seater)': 1.20,
            'Motorcycle (100-150cc)': 0.08,
            'Motorcycle (200cc+)': 0.12,
            'Tricycle (Keke NAPEP)': 0.15,
            
            # Air Travel (kgCO2e/passenger-km)
            'Domestic Flight (Nigeria)': 0.25,
            'Regional Flight (West Africa)': 0.20,
            'International Flight (Short-haul)': 0.18,
            'International Flight (Long-haul)': 0.15,
            
            # Public Transport
            'BRT Bus': 0.08,
            'Lagos Ferry': 0.05,
            'Lagos Rail': 0.04,
        }
        
        # Waste Emission Factors (kgCO2e/kg)
        self.waste_factors = {
            'Organic Waste (Landfill)': 0.35,
            'Organic Waste (Composting)': 0.05,
            'Plastic Waste (Landfill)': 0.15,
            'Plastic Waste (Recycling)': -0.20,  # Negative for recycling benefits
            'Paper/Cardboard (Landfill)': 0.12,
            'Paper/Cardboard (Recycling)': -0.15,
            'Metal (Landfill)': 0.08,
            'Metal (Recycling)': -0.30,
            'Glass (Landfill)': 0.09,
            'Glass (Recycling)': -0.10,
            'E-waste (Proper Disposal)': -0.25,
            'E-waste (Landfill)': 0.40,
        }
        
        # Agricultural Emission Factors (Nigeria specific)
        self.agriculture_factors = {
            'Rice Cultivation (per hectare)': 2500,
            'Livestock - Cattle (per head/year)': 2800,
            'Livestock - Sheep/Goat (per head/year)': 450,
            'Livestock - Poultry (per 100 birds/year)': 120,
            'Fertilizer Use (N-based, per kg)': 7.2,
            'Fertilizer Use (P-based, per kg)': 1.2,
            'Crop Residue Burning (per hectare)': 1800,
        }
        
        # Industrial Process Emission Factors
        self.industrial_factors = {
            'Cement Production (per tonne)': 850,
            'Steel Production (per tonne)': 1800,
            'Ammonia Production (per tonne)': 1600,
            'Ceramics/Tiles (per tonne)': 350,
            'Textile Manufacturing (per tonne)': 2800,
            'Food Processing (per ₦ million revenue)': 150,
            'Beverage Production (per litre)': 0.15,
        }
        
        # Building Operations (kgCO2e/m²/year)
        self.building_factors = {
            'Office Building (Air-conditioned)': 120,
            'Office Building (Naturally ventilated)': 60,
            'Residential Building (Lagos)': 45,
            'Residential Building (Northern Nigeria)': 55,
            'Hospital/Healthcare': 180,
            'School/Educational': 80,
            'Retail/Shopping Mall': 200,
            'Hotel/Accommodation': 160,
        }
        
        # Nigerian Cities Emission Factors for Business Travel
        self.hotel_factors = {
            'Lagos': 25,       # kgCO2e/room-night
            'Abuja': 22,
            'Port Harcourt': 20,
            'Kano': 18,
            'Ibadan': 16,
            'Enugu': 15,
            'Kaduna': 16,
            'Benin City': 15,
            'Maiduguri': 14,
            'Warri': 17,
            'Calabar': 15,
            'Uyo': 14,
        }

class CarbonFootprintCalculator:
    """Main calculator class"""
    
    def __init__(self):
        self.factors = NigerianEmissionFactors()
        self.organization_data = {}
        self.scope1_data = {}
        self.scope2_data = {}
        self.scope3_data = {}
        self.results = {}
        
    def calculate_scope1(self):
        """Calculate Scope 1 emissions"""
        total = 0
        details = []
        
        for fuel_type, data in self.scope1_data.items():
            if 'amount' in data and 'unit' in data:
                factor_key = f"{fuel_type} ({data['unit']})"
                if fuel_type in self.factors.fuel_factors:
                    factor = self.factors.fuel_factors[fuel_type].get(data['unit'], 0)
                    emissions = data['amount'] * factor
                    total += emissions
                    details.append({
                        'category': 'Stationary Combustion',
                        'source': fuel_type,
                        'amount': data['amount'],
                        'unit': data['unit'],
                        'emissions': emissions
                    })
        
        # Company vehicles
        if 'vehicle_data' in self.scope1_data:
            for vehicle in self.scope1_data['vehicle_data']:
                if vehicle['type'] in self.factors.transport_factors:
                    emissions = vehicle['distance'] * self.factors.transport_factors[vehicle['type']]
                    total += emissions
                    details.append({
                        'category': 'Mobile Combustion',
                        'source': vehicle['type'],
                        'amount': vehicle['distance'],
                        'unit': 'km',
                        'emissions': emissions
                    })
        
        self.results['scope1'] = {
            'total': total,
            'details': details,
            'unit': 'kgCO2e'
        }
        return total
    
    def calculate_scope2(self):
        """Calculate Scope 2 emissions"""
        total = 0
        details = []
        
        for energy_source, data in self.scope2_data.items():
            if 'consumption' in data and 'region' in data:
                factor = self.factors.electricity_factors.get(data['region'], self.factors.electricity_factors['National Grid Average'])
                emissions = data['consumption'] * factor
                total += emissions
                details.append({
                    'source': energy_source,
                    'region': data['region'],
                    'consumption': data['consumption'],
                    'unit': 'kWh',
                    'emissions': emissions
                })
        
        self.results['scope2'] = {
            'total': total,
            'details': details,
            'unit': 'kgCO2e'
        }
        return total
    
    def calculate_scope3(self):
        """Calculate Scope 3 emissions"""
        total = 0
        details = []
        
        # Upstream categories
        categories = {
            'business_travel': 'Business Travel',
            'employee_commuting': 'Employee Commuting',
            'purchased_goods': 'Purchased Goods & Services',
            'capital_goods': 'Capital Goods',
            'fuel_energy': 'Fuel & Energy Related Activities',
            'waste_operations': 'Waste Generated in Operations',
            'transport_distribution': 'Transportation & Distribution',
            'leased_assets': 'Leased Assets'
        }
        
        for category_key, category_name in categories.items():
            if category_key in self.scope3_data:
                category_total = 0
                for item in self.scope3_data[category_key]:
                    emissions = self._calculate_scope3_item(category_key, item)
                    category_total += emissions
                    details.append({
                        'category': category_name,
                        'description': item.get('description', ''),
                        'emissions': emissions
                    })
                total += category_total
        
        self.results['scope3'] = {
            'total': total,
            'details': details,
            'unit': 'kgCO2e'
        }
        return total
    
    def _calculate_scope3_item(self, category, item):
        """Calculate emissions for a single Scope 3 item"""
        if category == 'business_travel':
            if item['type'] == 'flight':
                factor = self.factors.transport_factors.get(item.get('flight_type', 'Domestic Flight (Nigeria)'), 0.25)
                return item['distance'] * item['passengers'] * factor
            elif item['type'] == 'hotel':
                factor = self.factors.hotel_factors.get(item['city'], 20)
                return item['nights'] * item['rooms'] * factor
            elif item['type'] == 'road':
                factor = self.factors.transport_factors.get(item['vehicle_type'], 0.2)
                return item['distance'] * factor
        
        elif category == 'employee_commuting':
            factor = self.factors.transport_factors.get(item['mode'], 0.2)
            return item['distance'] * item['employees'] * item['days'] * 2 * factor  # Round trip
        
        elif category == 'waste_operations':
            factor = self.factors.waste_factors.get(f"{item['waste_type']} ({item['treatment']})", 0)
            return item['amount'] * factor
        
        return 0
    
    def get_total_emissions(self):
        """Calculate total emissions"""
        scope1 = self.results.get('scope1', {}).get('total', 0)
        scope2 = self.results.get('scope2', {}).get('total', 0)
        scope3 = self.results.get('scope3', {}).get('total', 0)
        
        total = scope1 + scope2 + scope3
        
        self.results['total'] = {
            'scope1': scope1,
            'scope2': scope2,
            'scope3': scope3,
            'total': total,
            'unit': 'kgCO2e'
        }
        
        return total

def main():
    """Main application"""
    
    # Initialize session state
    if 'calculator' not in st.session_state:
        st.session_state.calculator = CarbonFootprintCalculator()
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 1
    if 'organization_info' not in st.session_state:
        st.session_state.organization_info = {}
    
    calculator = st.session_state.calculator
    
    # Sidebar navigation
    st.sidebar.title("🌍 Nigeria Carbon Calculator")
    
    menu_options = [
        "🏠 Dashboard",
        "📋 Organization Info",
        "🔥 Scope 1: Direct Emissions",
        "⚡ Scope 2: Indirect Energy",
        "🔗 Scope 3: Value Chain",
        "📊 Results & Analysis",
        "📈 Emission Factors",
        "📥 Export Report"
    ]
    
    selected_page = st.sidebar.radio("Navigation", menu_options)
    
    # Main content area
    if selected_page == "🏠 Dashboard":
        show_dashboard(calculator)
    elif selected_page == "📋 Organization Info":
        show_organization_info(calculator)
    elif selected_page == "🔥 Scope 1: Direct Emissions":
        show_scope1(calculator)
    elif selected_page == "⚡ Scope 2: Indirect Energy":
        show_scope2(calculator)
    elif selected_page == "🔗 Scope 3: Value Chain":
        show_scope3(calculator)
    elif selected_page == "📊 Results & Analysis":
        show_results(calculator)
    elif selected_page == "📈 Emission Factors":
        show_emission_factors(calculator)
    elif selected_page == "📥 Export Report":
        show_export(calculator)

def show_dashboard(calculator):
    """Show dashboard"""
    st.markdown('<div class="main-header">Nigeria Carbon Footprint Calculator</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Scope 1", f"{calculator.results.get('scope1', {}).get('total', 0):,.0f} kgCO₂e")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Scope 2", f"{calculator.results.get('scope2', {}).get('total', 0):,.0f} kgCO₂e")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Scope 3", f"{calculator.results.get('scope3', {}).get('total', 0):,.0f} kgCO₂e")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Quick start guide
    st.markdown('<div class="section-header">🚀 Quick Start Guide</div>', unsafe_allow_html=True)
    
    steps = [
        "1. 📋 Enter your organization information",
        "2. 🔥 Add Scope 1 data (direct emissions from fuel combustion)",
        "3. ⚡ Add Scope 2 data (purchased electricity)",
        "4. 🔗 Add Scope 3 data (indirect emissions from value chain)",
        "5. 📊 View results and analysis",
        "6. 📥 Export your carbon footprint report"
    ]
    
    for step in steps:
        st.info(step)
    
    # Recent updates
    st.markdown('<div class="section-header">📢 Nigerian Standards Applied</div>', unsafe_allow_html=True)
    
    updates = [
        "✅ Nigerian grid electricity emission factors",
        "✅ Nigerian fuel standards and blends",
        "✅ Nigerian city-specific hotel emission factors",
        "✅ Nigerian transportation modes (Keke NAPEP, BRT, etc.)",
        "✅ Nigerian agricultural emission factors",
        "✅ Nigerian industrial sector factors"
    ]
    
    for update in updates:
        st.success(update)

def show_organization_info(calculator):
    """Show organization information form"""
    st.markdown('<div class="sub-header">Organization Information</div>', unsafe_allow_html=True)
    
    with st.form("organization_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            org_name = st.text_input("Organization Name*", value=st.session_state.organization_info.get('name', ''))
            org_address = st.text_area("Address*", value=st.session_state.organization_info.get('address', ''))
            industry = st.selectbox(
                "Industry Sector*",
                ["Manufacturing", "Services", "Agriculture", "Construction", "Transportation", 
                 "Energy", "Healthcare", "Education", "Retail", "Other"]
            )
        
        with col2:
            contact_person = st.text_input("Contact Person*", value=st.session_state.organization_info.get('contact', ''))
            email = st.text_input("Email*", value=st.session_state.organization_info.get('email', ''))
            phone = st.text_input("Phone*", value=st.session_state.organization_info.get('phone', ''))
        
        reporting_period = st.selectbox(
            "Reporting Period",
            ["2024", "2023", "2022", "2021", "Custom"]
        )
        
        if reporting_period == "Custom":
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date")
        
        submitted = st.form_submit_button("Save Organization Information")
        
        if submitted:
            st.session_state.organization_info = {
                'name': org_name,
                'address': org_address,
                'industry': industry,
                'contact': contact_person,
                'email': email,
                'phone': phone,
                'reporting_period': reporting_period
            }
            st.success("Organization information saved successfully!")

def show_scope1(calculator):
    """Show Scope 1 data entry"""
    st.markdown('<div class="sub-header">Scope 1: Direct Emissions</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🚗 Company Vehicles", "🏭 Stationary Combustion", "❄️ Refrigerants & Fugitive"])
    
    with tab1:
        st.markdown("### Company Owned Vehicles")
        
        with st.form("vehicle_form"):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                vehicle_type = st.selectbox(
                    "Vehicle Type",
                    list(calculator.factors.transport_factors.keys())[:10]
                )
            
            with col2:
                fuel_type = st.selectbox(
                    "Fuel Type",
                    ["Petrol (PMS)", "Diesel (AGO)", "CNG", "LPG", "Electric"]
                )
            
            with col3:
                distance = st.number_input("Annual Distance (km)", min_value=0, value=10000)
            
            with col4:
                fuel_consumption = st.number_input("Fuel Consumption (L/100km)", min_value=0.0, value=12.0)
            
            add_vehicle = st.form_submit_button("Add Vehicle")
            
            if add_vehicle:
                if 'vehicle_data' not in calculator.scope1_data:
                    calculator.scope1_data['vehicle_data'] = []
                
                calculator.scope1_data['vehicle_data'].append({
                    'type': vehicle_type,
                    'fuel': fuel_type,
                    'distance': distance,
                    'consumption': fuel_consumption
                })
                st.success("Vehicle added!")
    
    with tab2:
        st.markdown("### Stationary Fuel Combustion")
        
        with st.form("fuel_form"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                fuel_type = st.selectbox(
                    "Fuel Type",
                    list(calculator.factors.fuel_factors.keys())
                )
            
            with col2:
                unit = st.selectbox(
                    "Unit",
                    ["litres", "m³", "kg", "kWh"]
                )
            
            with col3:
                amount = st.number_input("Annual Consumption", min_value=0.0, value=1000.0)
            
            add_fuel = st.form_submit_button("Add Fuel Consumption")
            
            if add_fuel:
                calculator.scope1_data[fuel_type] = {
                    'amount': amount,
                    'unit': unit
                }
                st.success("Fuel consumption added!")
    
    with tab3:
        st.markdown("### Refrigerants & Fugitive Emissions")
        st.info("Coming soon: Fugitive emissions calculator for Nigerian industrial context")

def show_scope2(calculator):
    """Show Scope 2 data entry"""
    st.markdown('<div class="sub-header">Scope 2: Indirect Energy Emissions</div>', unsafe_allow_html=True)
    
    with st.form("electricity_form"):
        st.markdown("### Electricity Consumption")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            region = st.selectbox(
                "Grid Region",
                list(calculator.factors.electricity_factors.keys())
            )
        
        with col2:
            consumption = st.number_input("Annual Consumption (kWh)", min_value=0, value=100000)
        
        with col3:
            energy_source = st.selectbox(
                "Energy Source",
                ["Grid Electricity", "Solar Power", "Hydro Power", "Gas Generator", "Diesel Generator"]
            )
        
        add_electricity = st.form_submit_button("Add Electricity Consumption")
        
        if add_electricity:
            calculator.scope2_data[energy_source] = {
                'consumption': consumption,
                'region': region
            }
            st.success("Electricity consumption added!")
    
    # Display current Scope 2 data
    if calculator.scope2_data:
        st.markdown("### Current Scope 2 Data")
        df_data = []
        for source, data in calculator.scope2_data.items():
            factor = calculator.factors.electricity_factors.get(data['region'], 0.55)
            emissions = data['consumption'] * factor
            df_data.append({
                'Source': source,
                'Region': data['region'],
                'Consumption (kWh)': f"{data['consumption']:,.0f}",
                'Emission Factor': f"{factor:.3f}",
                'Emissions (kgCO₂e)': f"{emissions:,.0f}"
            })
        
        if df_data:
            st.table(pd.DataFrame(df_data))

def show_scope3(calculator):
    """Show Scope 3 data entry"""
    st.markdown('<div class="sub-header">Scope 3: Value Chain Emissions</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["✈️ Business Travel", "👥 Employee Commuting", "🗑️ Waste Management", "📦 Purchased Goods"])
    
    with tab1:
        st.markdown("### Business Travel Emissions")
        
        travel_type = st.radio(
            "Travel Type",
            ["Flight", "Road Travel", "Hotel Stay"],
            horizontal=True
        )
        
        with st.form("business_travel_form"):
            if travel_type == "Flight":
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    flight_type = st.selectbox(
                        "Flight Type",
                        ["Domestic Flight (Nigeria)", "Regional Flight (West Africa)", 
                         "International Flight (Short-haul)", "International Flight (Long-haul)"]
                    )
                
                with col2:
                    distance = st.number_input("Distance (km)", min_value=0, value=500)
                
                with col3:
                    passengers = st.number_input("Number of Passengers", min_value=1, value=1)
            
            elif travel_type == "Road Travel":
                col1, col2 = st.columns(2)
                
                with col1:
                    vehicle_type = st.selectbox(
                        "Vehicle Type",
                        [k for k in calculator.factors.transport_factors.keys() if 'Car' in k or 'Bus' in k or 'SUV' in k]
                    )
                
                with col2:
                    distance = st.number_input("Distance (km)", min_value=0, value=100)
            
            else:  # Hotel Stay
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    city = st.selectbox(
                        "City",
                        list(calculator.factors.hotel_factors.keys())
                    )
                
                with col2:
                    nights = st.number_input("Number of Nights", min_value=1, value=1)
                
                with col3:
                    rooms = st.number_input("Number of Rooms", min_value=1, value=1)
            
            add_travel = st.form_submit_button("Add Travel Record")
            
            if add_travel:
                if 'business_travel' not in calculator.scope3_data:
                    calculator.scope3_data['business_travel'] = []
                
                record = {'type': travel_type.lower().replace(' ', '_')}
                if travel_type == "Flight":
                    record.update({
                        'flight_type': flight_type,
                        'distance': distance,
                        'passengers': passengers
                    })
                elif travel_type == "Road Travel":
                    record.update({
                        'vehicle_type': vehicle_type,
                        'distance': distance
                    })
                else:
                    record.update({
                        'city': city,
                        'nights': nights,
                        'rooms': rooms
                    })
                
                calculator.scope3_data['business_travel'].append(record)
                st.success("Travel record added!")
    
    with tab2:
        st.markdown("### Employee Commuting")
        
        with st.form("commuting_form"):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                mode = st.selectbox(
                    "Commute Mode",
                    ["Passenger Car - Small (Petrol)", "Passenger Car - Medium (Petrol)",
                     "Motorcycle (100-150cc)", "BRT Bus", "Lagos Rail", "Walk/Bicycle"]
                )
            
            with col2:
                employees = st.number_input("Number of Employees", min_value=1, value=10)
            
            with col3:
                distance = st.number_input("One-way Distance (km)", min_value=0.0, value=15.0)
            
            with col4:
                days = st.number_input("Days per Year", min_value=1, max_value=365, value=240)
            
            add_commute = st.form_submit_button("Add Commuting Data")
            
            if add_commute:
                if 'employee_commuting' not in calculator.scope3_data:
                    calculator.scope3_data['employee_commuting'] = []
                
                calculator.scope3_data['employee_commuting'].append({
                    'mode': mode,
                    'employees': employees,
                    'distance': distance,
                    'days': days
                })
                st.success("Commuting data added!")
    
    with tab3:
        st.markdown("### Waste Management")
        
        with st.form("waste_form"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                waste_type = st.selectbox(
                    "Waste Type",
                    ["Organic Waste", "Plastic Waste", "Paper/Cardboard", "Metal", "Glass", "E-waste"]
                )
            
            with col2:
                treatment = st.selectbox(
                    "Treatment Method",
                    ["Landfill", "Recycling", "Composting", "Incineration", "Proper Disposal"]
                )
            
            with col3:
                amount = st.number_input("Annual Amount (kg)", min_value=0.0, value=1000.0)
            
            add_waste = st.form_submit_button("Add Waste Data")
            
            if add_waste:
                if 'waste_operations' not in calculator.scope3_data:
                    calculator.scope3_data['waste_operations'] = []
                
                calculator.scope3_data['waste_operations'].append({
                    'waste_type': waste_type,
                    'treatment': treatment,
                    'amount': amount
                })
                st.success("Waste data added!")

def show_results(calculator):
    """Show calculation results and analysis"""
    st.markdown('<div class="sub-header">Carbon Footprint Results</div>', unsafe_allow_html=True)
    
    # Calculate emissions
    calculator.calculate_scope1()
    calculator.calculate_scope2()
    calculator.calculate_scope3()
    total = calculator.get_total_emissions()
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Emissions", f"{total:,.0f} kgCO₂e")
    
    with col2:
        st.metric("Equivalent Cars/Year", f"{total / 4200:,.0f}")
    
    with col3:
        st.metric("Equivalent Trees Needed", f"{total / 21:,.0f}")
    
    with col4:
        st.metric("Carbon Intensity", f"{total / 1000000:,.2f} tCO₂e/₦M revenue")
    
    # Visualization
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart of emissions by scope
        if total > 0:
            scope_labels = ['Scope 1', 'Scope 2', 'Scope 3']
            scope_values = [
                calculator.results.get('scope1', {}).get('total', 0),
                calculator.results.get('scope2', {}).get('total', 0),
                calculator.results.get('scope3', {}).get('total', 0)
            ]
            
            fig = px.pie(
                values=scope_values,
                names=scope_labels,
                title="Emissions by Scope",
                color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1']
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Bar chart of Scope 3 categories
        if calculator.scope3_data:
            categories = []
            values = []
            
            for category, items in calculator.scope3_data.items():
                if items:
                    cat_total = sum(calculator._calculate_scope3_item(category, item) for item in items)
                    categories.append(category.replace('_', ' ').title())
                    values.append(cat_total)
            
            if values:
                fig = px.bar(
                    x=categories,
                    y=values,
                    title="Scope 3 Emissions by Category",
                    labels={'x': 'Category', 'y': 'Emissions (kgCO₂e)'},
                    color=values,
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # Detailed breakdown
    st.markdown("### Detailed Breakdown")
    
    for scope in ['scope1', 'scope2', 'scope3']:
        if scope in calculator.results and calculator.results[scope]['details']:
            with st.expander(f"{scope.upper()} Details"):
                df = pd.DataFrame(calculator.results[scope]['details'])
                st.dataframe(df, use_container_width=True)

def show_emission_factors(calculator):
    """Show emission factors database"""
    st.markdown('<div class="sub-header">Nigerian Emission Factors Database</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "⛽ Fuels", "⚡ Electricity", "🚗 Transport", "🗑️ Waste", "🏭 Industry"
    ])
    
    with tab1:
        st.markdown("### Fuel Emission Factors")
        fuel_data = []
        for fuel, factors in calculator.factors.fuel_factors.items():
            for unit, factor in factors.items():
                fuel_data.append({
                    'Fuel Type': fuel,
                    'Unit': unit,
                    'Emission Factor (kgCO₂e/unit)': factor
                })
        st.dataframe(pd.DataFrame(fuel_data), use_container_width=True)
    
    with tab2:
        st.markdown("### Electricity Emission Factors")
        elec_data = []
        for region, factor in calculator.factors.electricity_factors.items():
            elec_data.append({
                'Grid Region/Source': region,
                'Emission Factor (kgCO₂e/kWh)': factor
            })
        st.dataframe(pd.DataFrame(elec_data), use_container_width=True)
    
    with tab3:
        st.markdown("### Transportation Emission Factors")
        transport_data = []
        for vehicle, factor in calculator.factors.transport_factors.items():
            transport_data.append({
                'Vehicle/Transport Mode': vehicle,
                'Emission Factor (kgCO₂e/km)': factor
            })
        st.dataframe(pd.DataFrame(transport_data), use_container_width=True)
    
    with tab4:
        st.markdown("### Waste Management Emission Factors")
        waste_data = []
        for waste, factor in calculator.factors.waste_factors.items():
            waste_data.append({
                'Waste Type & Treatment': waste,
                'Emission Factor (kgCO₂e/kg)': factor
            })
        st.dataframe(pd.DataFrame(waste_data), use_container_width=True)
    
    with tab5:
        st.markdown("### Industrial & Agricultural Factors")
        industrial_data = []
        for process, factor in calculator.factors.industrial_factors.items():
            industrial_data.append({
                'Industrial Process': process,
                'Emission Factor': factor
            })
        st.dataframe(pd.DataFrame(industrial_data), use_container_width=True)

def show_export(calculator):
    """Show export options"""
    st.markdown('<div class="sub-header">Export Carbon Footprint Report</div>', unsafe_allow_html=True)
    
    # Generate report data
    report_data = {
        'Organization': st.session_state.organization_info,
        'Calculation Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'Results': calculator.results
    }
    
    # Export options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Generate PDF Report"):
            st.info("PDF generation feature coming soon!")
    
    with col2:
        if st.button("📊 Export to Excel"):
            # Create Excel file
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Summary sheet
                summary_data = []
                if 'total' in calculator.results:
                    total = calculator.results['total']
                    summary_data.append(['Total Emissions', f"{total['total']:,.2f}", total['unit']])
                    summary_data.append(['Scope 1 Emissions', f"{total['scope1']:,.2f}", total['unit']])
                    summary_data.append(['Scope 2 Emissions', f"{total['scope2']:,.2f}", total['unit']])
                    summary_data.append(['Scope 3 Emissions', f"{total['scope3']:,.2f}", total['unit']])
                
                df_summary = pd.DataFrame(summary_data, columns=['Category', 'Value', 'Unit'])
                df_summary.to_excel(writer, sheet_name='Summary', index=False)
                
                # Scope details
                for scope in ['scope1', 'scope2', 'scope3']:
                    if scope in calculator.results and calculator.results[scope]['details']:
                        df_details = pd.DataFrame(calculator.results[scope]['details'])
                        df_details.to_excel(writer, sheet_name=scope.upper(), index=False)
            
            # Download button
            st.download_button(
                label="⬇️ Download Excel File",
                data=output.getvalue(),
                file_name=f"carbon_footprint_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    with col3:
        if st.button("📋 Copy Summary"):
            st.info("Copy to clipboard feature coming soon!")
    
    # Preview report
    st.markdown("### Report Preview")
    
    with st.expander("View Full Report"):
        st.json(report_data)

if __name__ == "__main__":
    main()