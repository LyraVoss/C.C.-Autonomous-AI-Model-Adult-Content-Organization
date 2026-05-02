import streamlit as st
import requests
import pandas as pd
import asyncio
import websockets
import json

# Configuration - Update with your deployment URL
import os

# Uses the Render URL if available, otherwise defaults to localhost
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
WS_URL = os.getenv("WS_URL", "ws://localhost:8000/ws/creators")

st.set_page_config(page_title="C.C. Autonomous Dashboard", layout="wide", page_icon="👠")

st.title("👠 C.C. Autonomous AI Management Console")

# Sidebar - Key Health & Service Status
st.sidebar.header("🛡️ System Integrity")
if st.sidebar.button("Scan API Health"):
    with st.sidebar:
        services = ["openai", "elevenlabs", "stability", "stripe"]
        for s in services:
            # Placeholder for actual health check logic
            st.success(f"{s.upper()}: Connected")

# Main Interface Tabs
tab1, tab2, tab3 = st.tabs(["🎭 Creator Control", "💬 Live Feed", "📈 Revenue Analytics"])

with tab1:
    st.header("Active AI Personalities")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Profile Selection")
        # In production, fetch this from GET /creators
        creators = ["Luna Star", "Siren", "Mistress X"]
        selected = st.selectbox("Switch Active Model", creators)
        st.image("https://placeholder.com", caption=f"Active: {selected}")
        
    with col2:
        st.subheader("Manual Override")
        prompt = st.text_input("Force AI Response/Post", placeholder="Type a custom prompt...")
        if st.button("Generate & Post"):
            st.write(f"Routing request to {selected} brain...")
            # requests.post(f"{API_BASE_URL}/creators/generate", json={"prompt": prompt})

with tab2:
    st.header("Real-Time Interaction Feed")
    st.info("Monitoring WebSocket: /ws/creators/stream")
    # This acts as a rolling log of fan interactions
    if "log" not in st.session_state:
        st.session_state.log = []
    
    st.code("\n".join(st.session_state.log[-10:]), language="text")
    if st.button("Refresh Feed"):
        st.session_state.log.append(f"[{pd.Timestamp.now()}] New interaction detected...")

with tab3:
    st.header("Financial Performance")
    # Mocking revenue data based on your analytics logic
    chart_data = pd.DataFrame({
        'Date': pd.date_range(start='2023-01-01', periods=7),
        'Revenue ($)': [450, 780, 610, 1200, 1100, 1500, 2100]
    })
    st.line_chart(chart_data.set_index('Date'))
    st.metric("Total Monthly Revenue", "$7,740", "+12%")
