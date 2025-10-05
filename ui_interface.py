import streamlit as st
from game_engine import FarmingSimulator, NASADataFetcher, start_new_game

# Page configuration
st.set_page_config(
    page_title="FarmSense - NASA Agriculture Game",
    page_icon="🌾",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #2E7D32;
        text-align: center;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #558B2F;
        text-align: center;
    }
    .info-box {
        background-color: #E8F5E9;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
    }
    .warning-box {
        background-color: #FFF3E0;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #FF9800;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'game_state' not in st.session_state:
    st.session_state.game_state = None
    st.session_state.nasa_fetcher = NASADataFetcher()
    st.session_state.game_started = False
    st.session_state.show_results = False

# Header
st.markdown('<p class="main-header">🌾 FarmSense</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Learn Sustainable Farming with NASA Data</p>', unsafe_allow_html=True)

# Sidebar for game info
with st.sidebar:
    st.header("📖 About FarmSense")
    st.write("""
    FarmSense teaches you how to use real NASA satellite data 
    to make smart farming decisions.
    
    **You will:**
    - Analyze real climate data
    - Make irrigation decisions
    - Optimize fertilizer use
    - Learn sustainable practices
    """)
    
    st.divider()
    
    st.header("🛰️ NASA Data Used")
    st.write("""
    - **Temperature** (T2M)
    - **Precipitation** (PRECTOTCORR)
    - **Soil Moisture** (GWETROOT)
    - **Solar Radiation** (ALLSKY_SFC_SW_DWN)
    
    *Data from NASA POWER API*
    """)
    
    if st.button("🔄 Restart Game", use_container_width=True):
        st.session_state.game_state = None
        st.session_state.game_started = False
        st.session_state.show_results = False
        st.rerun()

# Main content area
if not st.session_state.game_started:
    # Welcome screen
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="info-box">
        <h3>🎯 Your Mission</h3>
        <p>You're managing a wheat farm in Kansas. Use NASA satellite data 
        to make the best decisions for your crop.</p>
        
        <p><strong>Challenge:</strong> Maximize your yield while conserving resources!</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        
        if st.button("🚀 Start Farming", use_container_width=True, type="primary"):
            start_new_game()
            st.session_state.game_started = True
            st.rerun()

elif not st.session_state.show_results:
    # Game play screen
    game = st.session_state.game_state
    
    st.markdown("---")
    st.header("🌍 Step 1: Review NASA Data")
    
    # Show NASA data analysis
    analysis = game.analyze_conditions()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "🌡️ Avg Temperature",
            f"{analysis['avg_temperature']}°C",
            help="Temperature affects crop water needs"
        )
    
    with col2:
        st.metric(
            "🌧️ Avg Precipitation",
            f"{analysis['avg_precipitation']} mm/day",
            help="Recent rainfall amounts"
        )
    
    with col3:
        st.metric(
            "💧 Soil Moisture",
            f"{analysis['avg_soil_moisture']}",
            help="0-1 scale, optimal: 0.3-0.5"
        )
    
    # Recommendations
    st.markdown("---")
    st.subheader("💡 NASA Data Insights")
    
    for rec in analysis['recommendation']:
        st.info(rec)
    
    # Decision making
    st.markdown("---")
    st.header("🎮 Step 2: Make Your Decisions")
    
    st.markdown("""
    <div class="warning-box">
    <strong>Think carefully!</strong> Your decisions should be based on the NASA data above.
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💧 Irrigation Level")
        irrigation = st.slider(
            "How much to irrigate?",
            min_value=0,
            max_value=100,
            value=50,
            help="Consider soil moisture and recent rainfall"
        )
        st.caption(f"Water usage: ~{irrigation * 10} liters")
        
        if analysis['avg_soil_moisture'] < 0.3:
            st.warning("Low soil moisture detected!")
        elif analysis['avg_soil_moisture'] > 0.5:
            st.info("Soil is already moist!")
    
    with col2:
        st.subheader("🌱 Fertilizer Amount")
        fertilizer = st.slider(
            "How much fertilizer?",
            min_value=0,
            max_value=100,
            value=50,
            help="Optimal range: 40-60 units"
        )
        st.caption(f"Cost: ${fertilizer * 5}")
        
        if fertilizer > 70:
            st.warning("High fertilizer may cause runoff!")
        elif fertilizer < 30:
            st.info("Low fertilizer may limit growth")
    
    st.write("")
    
    # Submit decisions
    if st.button("🌾 Harvest & See Results", use_container_width=True, type="primary"):
        game.make_decision('irrigation', irrigation)
        game.make_decision('fertilizer', fertilizer)
        st.session_state.show_results = True
        st.rerun()

else:
    # Results screen
    game = st.session_state.game_state
    
    yield_pct, feedback = game.calculate_yield()
    
    st.markdown("---")
    st.header("📊 Harvest Results")
    
    # Big yield display
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if yield_pct > 110:
            st.success("🎉 Outstanding Performance!")
            st.balloons()
        elif yield_pct > 90:
            st.success("✅ Good Job!")
        elif yield_pct > 70:
            st.warning("⚠️ Could Be Better")
        else:
            st.error("❌ Needs Improvement")
        
        st.metric(
            "Crop Yield",
            f"{yield_pct}%",
            help="100% is baseline yield"
        )
    
    st.markdown("---")
    
    # Detailed feedback
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Performance Details")
        st.write(feedback)
        
        st.divider()
        
        st.subheader("🔍 Your Decisions")
        st.write(f"**Irrigation:** {game.decisions['irrigation']} units")
        st.write(f"**Fertilizer:** {game.decisions['fertilizer']} units")
    
    with col2:
        st.subheader("💰 Resource Usage")
        st.write(f"**Water Used:** {game.water_usage} liters")
        st.write(f"**Fertilizer Cost:** ${game.fertilizer_cost}")
        
        efficiency = (yield_pct / (game.water_usage / 100)) if game.water_usage > 0 else 0
        st.metric("Water Efficiency", f"{efficiency:.1f}%")
    
    st.markdown("---")
    
    # Educational takeaway
    st.subheader("📚 What You Learned")
    st.markdown("""
    <div class="info-box">
    <p><strong>NASA satellite data can help farmers:</strong></p>
    <ul>
        <li>Monitor soil moisture to optimize irrigation</li>
        <li>Track temperature and rainfall patterns</li>
        <li>Make data-driven decisions that conserve resources</li>
        <li>Improve crop yields sustainably</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    
    if st.button("🔄 Try Again", use_container_width=True, type="primary"):
        st.session_state.game_state = None
        st.session_state.game_started = False
        st.session_state.show_results = False
        st.rerun()
