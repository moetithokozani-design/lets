# dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import json

def main():
    st.set_page_config(page_title="NASA Ag Data Dashboard", layout="wide")
    
    st.title("🌱 Harvest Horizon - NASA Agricultural Dashboard")
    
    # Sidebar with game stats
    with st.sidebar:
        st.header("Game Statistics")
        st.metric("Current Player", "Player 1")
        st.metric("Cash", "$10,000")
        st.metric("Sustainability", "7/10")
        
    # Main dashboard areas
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("NASA Soil Moisture Data")
        # Display real NASA data
        moisture_data = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=30),
            'moisture': [25, 28, 30, 22, 18, 15, 20, 25, 28, 30] * 3
        })
        fig = px.line(moisture_data, x='date', y='moisture', 
                     title="Soil Moisture Trends (SMAP Data)")
        st.plotly_chart(fig)
        
    with col2:
        st.subheader("Crop Health Analysis")
        # NDVI data visualization
        st.image("https://nasaviz.gsfc.nasa.gov/vis/a000000/a004600/a004662/ndvi_16_945.jpg", 
                caption="NASA MODIS NDVI Data")
    
    # Educational content
    with st.expander("🌍 How NASA Data Helps Farmers"):
        st.write("""
        **NASA's Earth Observation Data:**
        - **SMAP**: Soil Moisture Active Passive - monitors soil moisture
        - **MODIS**: Moderate Resolution Imaging Spectroradiometer - tracks vegetation health
        - **ECOSTRESS**: ECOSystem Spaceborne Thermal Radiometer Experiment - measures plant temperatures
        - **Landsat**: High-resolution land imaging
        
        These datasets help farmers make informed decisions about irrigation, planting, and harvesting.
        """)

if __name__ == "__main__":
    main()