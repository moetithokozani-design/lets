# streamlit_app.py
import streamlit as st
import json
import time
import pandas as pd
import plotly.express as px
from nasa_data import get_smap_timeseries, get_simulated_ndvi, get_nasa_explanation

st.set_page_config(page_title="NASA Ag Data Dashboard", layout="wide")

# Auto-refresh every 2 seconds
if st.button("Refresh"):
    st.rerun()
    
# Load game state
@st.cache_data(ttl=2)
def load_game_state():
    try:
        with open("game_state.json", "r") as f:
            return json.load(f)
    except:
        return {"players": [{"name": "Player 1", "cash": 0, "sustainability": 0}]}

state = load_game_state()
current_player = state["players"][state["current_player"]]

# Sidebar
with st.sidebar:
    st.image("https://www.nasa.gov/sites/default/files/thumbnails/image/nasa-logo-web-rgb.png", width=200)
    st.header("🌱 Game Stats")
    st.metric("Current Player", current_player["name"])
    st.metric("Cash", f"${current_player['cash']:,}")
    st.metric("Sustainability", f"{current_player['sustainability']}/10")
    
    st.subheader("Owned Assets")
    for aid in current_player.get("assets", []):
        st.write(f"✅ {aid.replace('_', ' ').title()}")

# Main content
st.title("🛰️ Harvest Horizon: NASA Agricultural Dashboard")

col1, col2 = st.columns(2)

with col1:
    st.subheader("💧 Soil Moisture (SMAP Simulation)")
    smap_data = get_smap_timeseries()
    fig1 = px.line(smap_data, x='date', y='moisture', 
                   labels={'moisture': 'Moisture (%)', 'date': 'Date'},
                   line_shape='spline')
    fig1.update_traces(line_color='#4CAF50')
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("🌿 Crop Health (NDVI Simulation)")
    ndvi = get_simulated_ndvi()
    st.metric("Current NDVI", f"{ndvi:.2f}", delta=None)
    st.info(f"NDVI > 0.6 = Healthy vegetation | < 0.2 = Bare soil")
    
    # Static educational image placeholder
    st.image("https://nasaviz.gsfc.nasa.gov/vis/a000000/a004600/a004662/ndvi_16_945.jpg", 
             caption="Example: NASA MODIS NDVI Data", use_column_width=True)

# Educational section
with st.expander("🌍 How NASA Data Helps Farmers"):
    explanations = get_nasa_explanation()
    for sat, desc in explanations.items():
        st.markdown(f"**{sat}**: {desc}")

st.markdown("---")
st.caption("🔄 Dashboard updates every 2 seconds. Game state shared with Pygame client.")