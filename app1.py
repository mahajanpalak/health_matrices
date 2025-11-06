import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import os

import database as db  
from user_profile import create_or_edit_profile
from food import search_food_ui
from exercise import search_exercise_ui
from food_recommender import food_recommender_ui
from full_day_meal_planner import full_day_meal_planner_ui
from workout_generator import workout_generator_ui
from utils import load_profile, save_profile
from routine_optimizer import routine_optimizer_ui

# Import authentication and database
import auth
from database import load_user_profile as load_user_profile_db

# Page configuration
st.set_page_config(
    page_title="Health Matrices",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# PREMIUM MEDICAL DARK THEME COLOR PALETTE
# ENHANCED MEDICAL COLOR PALETTE (Based on your screenshots)
COLORS = {
    # Background Colors
    "dark_navy": "#0a1128",
    "deep_blue": "#1a2035",
    "surface": "#1e2436",
    "card_bg": "#2a3142",
    
    # Vibrant Medical Accents
    "medical_cyan": "#00e0ff",
    "medical_teal": "#2a9d8f",
    "health_amber": "#e9c46a",
    "medical_coral": "#f4a261",
    "medical_red": "#e76f51",
    "wellness_green": "#2a9d8f",
    
    # Text Hierarchy
    "text_primary": "#ffffff",
    "text_secondary": "#e2e8f0",
    "text_labels": "#94a3b8",
    
    # Status Colors
    "success": "#2a9d8f",
    "warning": "#e9c46a",
    "error": "#e76f51",
    "info": "#00e0ff"
}

# PREMIUM MEDICAL DARK THEME CSS
st.markdown(f"""
<style>
    /* Global Styles */
    .stApp {{
        background: linear-gradient(135deg, {COLORS['dark_navy']} 0%, {COLORS['deep_blue']} 100%);
        color: {COLORS['text_primary']};
    }}

    /* Fix Navigation text visibility */
    .sidebar-header h2 {{
        color: #ffffff !important;
    }}
    
    .sidebar-header p {{
        color: #e2e8f0 !important;
    }}
    
    /* Fix navigation buttons text */
    .nav-button {{
        color: #ffffff !important;
    }}

    /* FIX ALL TEXT VISIBILITY ISSUES */
    
    /* Fix all input placeholders to be visible */
    .stTextInput input::placeholder, 
    .stNumberInput input::placeholder, 
    .stTextArea textarea::placeholder,
    .stSelectbox select::placeholder {{
        color: #94a3b8 !important;
        opacity: 1 !important;
    }}

    /* Fix select dropdown text and options */
    .stSelectbox [data-baseweb="select"] {{
        color: #ffffff !important;
    }}
    
    /* Fix dropdown options background and text */
    [data-baseweb="popover"] [role="listbox"] {{
        background-color: {COLORS['surface']} !important;
        color: #ffffff !important;
    }}
    
    [data-baseweb="popover"] [role="option"] {{
        color: #ffffff !important;
        background-color: {COLORS['surface']} !important;
    }}
    
    [data-baseweb="popover"] [role="option"]:hover {{
        background-color: {COLORS['card_bg']} !important;
        color: #ffffff !important;
    }}

    /* Fix multi-select text and options */
    .stMultiSelect [data-baseweb="select"] {{
        color: #ffffff !important;
    }}
    
    .stMultiSelect [data-baseweb="select"] span {{
        color: #ffffff !important;
    }}

    /* Fix radio button labels */
    .stRadio label {{
        color: #ffffff !important;
        font-weight: 500 !important;
    }}

    /* Fix checkbox labels */
    .stCheckbox label {{
        color: #ffffff !important;
        font-weight: 500 !important;
    }}

    /* Fix sidebar section headers */
    .sidebar .stMarkdown h3 {{
        color: #ffffff !important;
    }}

    /* Fix text colors for form inputs and labels */
    .stTextInput label, .stNumberInput label, .stSelectbox label, .stTextArea label {{
        color: #ffffff !important;
        font-weight: 500 !important;
    }}

    .stTextInput input, .stNumberInput input, .stSelectbox select, .stTextArea textarea {{
        color: #ffffff !important;
        background-color: {COLORS['surface']} !important;
        border: 1px solid {COLORS['card_bg']} !important;
    }}

    .stTextInput input:focus, .stNumberInput input:focus, .stSelectbox select:focus, .stTextArea textarea:focus {{
        border-color: {COLORS['medical_cyan']} !important;
        box-shadow: 0 0 0 2px rgba(0, 224, 255, 0.2) !important;
    }}

    /* Fix all text elements to be visible */
    .stMarkdown, .stText, .stHeader, .stSubheader, .stTitle {{
        color: #ffffff !important;
    }}

    /* Specific fixes for common text sizes */
    p, div, span {{
        color: #e2e8f0 !important;
    }}

    /* Fix for "How are you feeling right now?" and similar texts */
    .stRadio label, .stCheckbox label {{
        color: #ffffff !important;
        font-weight: 500 !important;
    }}

    /* Fix for form container backgrounds */
    .stForm {{
        background-color: {COLORS['surface']} !important;
        border: 1px solid {COLORS['card_bg']} !important;
        border-radius: 10px !important;
        padding: 1.5rem !important;
    }}

    /* Fix for profile section specifically */
    .profile-section {{
        background: {COLORS['surface']} !important;
        padding: 2rem !important;
        border-radius: 12px !important;
        border: 1px solid {COLORS['card_bg']} !important;
    }}

    /* Fix for metric values and labels */
    .stMetric {{
        color: #ffffff !important;
    }}

    .stMetric label {{
        color: {COLORS['text_labels']} !important;
    }}

    .stMetric value {{
        color: #ffffff !important;
    }}

    /* Fix for expander headers */
    .streamlit-expanderHeader {{
        color: #ffffff !important;
        background-color: {COLORS['surface']} !important;
        border: 1px solid {COLORS['card_bg']} !important;
    }}

    .streamlit-expanderContent {{
        background-color: {COLORS['surface']} !important;
        color: {COLORS['text_secondary']} !important;
    }}

    /* Fix for dataframes */
    .dataframe {{
        color: #ffffff !important;
    }}

    /* Fix for tabs */
    .stTabs [data-baseweb="tab"] {{
        color: {COLORS['text_secondary']} !important;
    }}

    .stTabs [aria-selected="true"] {{
        color: {COLORS['dark_navy']} !important;
    }}

    /* Fix for buttons text */
    .stButton button {{
        color: {COLORS['dark_navy']} !important;
    }}

    /* Fix for success/warning/error messages */
    .stAlert {{
        color: #ffffff !important;
    }}

    .stSuccess {{
        background-color: rgba(42, 157, 143, 0.2) !important;
        border-color: {COLORS['wellness_green']} !important;
    }}

    .stWarning {{
        background-color: rgba(233, 196, 106, 0.2) !important;
        border-color: {COLORS['health_amber']} !important;
    }}

    .stError {{
        background-color: rgba(231, 111, 81, 0.2) !important;
        border-color: {COLORS['medical_red']} !important;
    }}

    .stInfo {{
        background-color: rgba(0, 224, 255, 0.2) !important;
        border-color: {COLORS['medical_cyan']} !important;
    }}

    /* Fix for slider labels */
    .stSlider label {{
        color: #ffffff !important;
    }}

    /* Fix for file uploader */
    .stFileUploader label {{
        color: #ffffff !important;
    }}

    /* Fix for progress bars */
    .stProgress .st-bo {{
        color: #ffffff !important;
    }}
    
    /* Additional fixes for dropdown selected values */
    [data-baseweb="select"] div {{
        color: #ffffff !important;
    }}
    
    /* Fix for multiselect selected items */
    [data-baseweb="tag"] {{
        background-color: {COLORS['card_bg']} !important;
        color: #ffffff !important;
    }}
    
    /* Fix for date input */
    .stDateInput input {{
        color: #ffffff !important;
    }}
    
    .stDateInput label {{
        color: #ffffff !important;
    }}

    /* NEW: Fix placeholder text color specifically for form inputs */
    .stTextInput input::placeholder {{
        color: #94a3b8 !important;
        opacity: 0.8 !important;
    }}

    .stNumberInput input::placeholder {{
        color: #94a3b8 !important;
        opacity: 0.8 !important;
    }}

    .stTextArea textarea::placeholder {{
        color: #94a3b8 !important;
        opacity: 0.8 !important;
    }}

    .stSelectbox select::placeholder {{
        color: #94a3b8 !important;
        opacity: 0.8 !important;
    }}

    /* Fix for text input placeholder when typing */
    .stTextInput input:not(:focus):placeholder-shown {{
        color: #94a3b8 !important;
    }}

    .stNumberInput input:not(:focus):placeholder-shown {{
        color: #94a3b8 !important;
    }}

    .stTextArea textarea:not(:focus):placeholder-shown {{
        color: #94a3b8 !important;
    }}

    /* Fix for select box placeholder text */
    [data-baseweb="select"] [aria-live="polite"] {{
        color: #94a3b8 !important;
    }}

    /* Fix for empty select box state */
    [data-baseweb="select"]:empty {{
        color: #94a3b8 !important;
    }}
    /* Fix ALL placeholder text visibility - COMPREHENSIVE FIX */
    ::placeholder {{
        color: #94a3b8 !important;
        opacity: 0.8 !important;
    }}
    
    /* Specific fixes for Streamlit components */
    .stSelectbox [data-baseweb="select"] div,
    .stSelectbox [data-baseweb="select"] span {{
        color: #94a3b8 !important;
    }}
    
    .stSelectbox [data-baseweb="select"]:has(div:empty)::before {{
        content: attr(placeholder);
        color: #94a3b8 !important;
        opacity: 0.8 !important;
    }}
    
    /* Fix for dropdown selected value when empty */
    [data-baseweb="select"] div:empty::before {{
        color: #94a3b8 !important;
        opacity: 0.8 !important;
    }}
    
    /* Fix for all input text */
    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea,
    .stSelectbox select {{
        color: #94a3b8 !important;
    }}
    
    /* When input is focused, change text color to white */
    .stTextInput input:focus,
    .stNumberInput input:focus,
    .stTextArea textarea:focus,
    .stSelectbox select:focus {{
        color: #ffffff !important;
    }}

    /* Specific fix for workout generator form placeholders */
    .workout-form input::placeholder,
    .workout-form textarea::placeholder {{
        color: #94a3b8 !important;
        opacity: 0.8 !important;
    }}

    /* Fix all input placeholders to be visible */
    .stTextInput input::placeholder, 
    .stNumberInput input::placeholder, 
    .stTextArea textarea::placeholder,
    .stSelectbox select::placeholder {{
        color: #94a3b8 !important;
        opacity: 1 !important;
    }}

        /* Main Header */
    .main-header {{
        font-size: 2.8rem;
        color: {COLORS['text_primary']};
        background: linear-gradient(135deg, {COLORS['surface']} 0%, {COLORS['card_bg']} 100%);
        padding: 2.5rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 700;
        box-shadow: 0 12px 30px rgba(10, 17, 40, 0.6);
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        border: 1px solid {COLORS['medical_cyan']}33;
        position: relative;
        overflow: hidden;
        animation: fadeInUp 0.8s ease-out;
    }}
    
    .main-header::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, {COLORS['medical_cyan']}, {COLORS['wellness_green']});
        animation: shimmer 2s infinite;
    }}
    
    /* Metric Cards with Hover Animations */
    .metric-card {{
        background: linear-gradient(135deg, {COLORS['surface']} 0%, {COLORS['card_bg']} 100%);
        padding: 1.8rem;
        border-radius: 12px;
        color: {COLORS['text_primary']};
        text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.4);
        margin: 0.5rem;
        border: 1px solid {COLORS['medical_cyan']}33;
        transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        position: relative;
        overflow: hidden;
        animation: slideInUp 0.6s ease-out;
    }}
    
    .metric-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, {COLORS['medical_cyan']}, {COLORS['wellness_green']});
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }}
    
    .metric-card:hover {{
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 15px 40px rgba(0, 225, 255, 0.3);
    }}
    
    .metric-card:hover::before {{
        transform: scaleX(1);
    }}
    
    .metric-card h3 {{
        font-size: 0.95rem;
        margin: 0 0 0.8rem 0;
        opacity: 0.9;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        color: {COLORS['text_labels']};
    }}
    
    .metric-card h2 {{
        font-size: 2.2rem;
        margin: 0.5rem 0;
        font-weight: 700;
        background: linear-gradient(135deg, {COLORS['medical_cyan']}, {COLORS['wellness_green']});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    
    .metric-card p {{
        margin: 0;
        font-size: 0.9rem;
        opacity: 0.9;
        font-weight: 500;
        color: {COLORS['text_secondary']};
    }}
    
    /* Specialized Metric Cards */
    .metric-card-bmi {{
        background: linear-gradient(135deg, {COLORS['surface']} 0%, {COLORS['card_bg']} 100%);
        border-left: 4px solid {COLORS['medical_cyan']};
    }}
    
    .metric-card-age {{
        background: linear-gradient(135deg, {COLORS['surface']} 0%, {COLORS['card_bg']} 100%);
        border-left: 4px solid {COLORS['wellness_green']};
    }}
    
    .metric-card-weight {{
        background: linear-gradient(135deg, {COLORS['surface']} 0%, {COLORS['card_bg']} 100%);
        border-left: 4px solid {COLORS['health_amber']};
    }}
    
    .metric-card-height {{
        background: linear-gradient(135deg, {COLORS['surface']} 0%, {COLORS['card_bg']} 100%);
        border-left: 4px solid {COLORS['medical_red']};
    }}
    
    /* Insight Cards */
    .insight-card {{
        background: {COLORS['surface']};
        padding: 2rem;
        border-radius: 12px;
        border-left: 4px solid {COLORS['medical_cyan']};
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        margin: 1.5rem 0;
        border: 1px solid {COLORS['card_bg']};
        transition: all 0.3s ease;
        animation: fadeIn 0.8s ease-out;
    }}
    
    .insight-card:hover {{
        box-shadow: 0 12px 35px rgba(0, 225, 255, 0.2);
        transform: translateY(-3px);
    }}
    
    /* Feature Cards */
    .feature-card {{
        background: {COLORS['surface']};
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid {COLORS['card_bg']};
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        margin: 1.5rem 0;
        transition: all 0.4s ease;
        min-height: 200px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        position: relative;
        overflow: hidden;
        animation: slideInLeft 0.6s ease-out;
    }}
    
    .feature-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, {COLORS['medical_cyan']}, {COLORS['wellness_green']});
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }}
    
    .feature-card:hover::before {{
        transform: scaleX(1);
    }}
    
    .feature-card:hover {{
        transform: translateY(-8px);
        box-shadow: 0 15px 40px rgba(0, 225, 255, 0.25);
        border-color: {COLORS['medical_cyan']}33;
    }}
    
    /* Sidebar Styling */
    .sidebar-header {{
        background: linear-gradient(135deg, {COLORS['surface']} 0%, {COLORS['card_bg']} 100%);
        padding: 2rem;
        border-radius: 0 0 15px 15px;
        color: {COLORS['text_primary']};
        text-align: center;
        margin-bottom: 1.5rem;
        box-shadow: 0 6px 20px rgba(0,0,0,0.4);
        position: relative;
        overflow: hidden;
    }}
    
    .sidebar-header::before {{
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, {COLORS['medical_cyan']}, {COLORS['wellness_green']});
    }}
    
    .user-welcome {{
        background: {COLORS['surface']};
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid {COLORS['medical_cyan']};
        margin: 1.5rem 0;
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        border: 1px solid {COLORS['card_bg']};
        animation: pulse 2s infinite;
    }}
    
    /* Button Styling */
    .stButton button {{
        background: linear-gradient(135deg, {COLORS['medical_cyan']} 0%, {COLORS['wellness_green']} 100%);
        color: {COLORS['dark_navy']};
        border: none;
        padding: 0.9rem 1.8rem;
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        box-shadow: 0 6px 20px rgba(0, 225, 255, 0.3);
        position: relative;
        overflow: hidden;
    }}
    
    .stButton button:hover {{
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 10px 30px rgba(0, 225, 255, 0.5);
    }}
    
    .stButton button::before {{
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        transition: left 0.5s;
    }}
    
    .stButton button:hover::before {{
        left: 100%;
    }}
    
    /* Section Headers */
    .section-header {{
        color: {COLORS['text_primary']};
        border-bottom: 2px solid {COLORS['medical_cyan']};
        padding-bottom: 1rem;
        margin: 3rem 0 2rem 0;
        font-size: 1.6rem;
        font-weight: 700;
        position: relative;
        animation: fadeIn 0.8s ease-out;
    }}
    
    .section-header::after {{
        content: '';
        position: absolute;
        bottom: -2px;
        left: 0;
        width: 50px;
        height: 2px;
        background: {COLORS['wellness_green']};
        animation: expandWidth 1s ease-out;
    }}
    
    /* Progress Bars */
    .progress-container {{
        background: {COLORS['card_bg']};
        border-radius: 10px;
        margin: 1rem 0;
        padding: 0.4rem;
        box-shadow: inset 0 2px 8px rgba(0,0,0,0.3);
        border: 1px solid {COLORS['surface']};
    }}
    
    .progress-fill {{
        background: linear-gradient(90deg, {COLORS['medical_cyan']} 0%, {COLORS['wellness_green']} 100%);
        height: 22px;
        border-radius: 8px;
        text-align: center;
        color: {COLORS['dark_navy']};
        font-size: 0.85rem;
        line-height: 22px;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(0, 225, 255, 0.4);
        position: relative;
        overflow: hidden;
        transition: width 1.5s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    }}
    
    .progress-fill::before {{
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
        animation: shimmer 2s infinite;
    }}
    
    /* Navigation Buttons */
    .nav-button {{
        background: {COLORS['surface']} !important;
        color: {COLORS['text_primary']} !important;
        border: 1px solid {COLORS['card_bg']} !important;
        padding: 1rem !important;
        border-radius: 10px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        margin: 0.3rem 0 !important;
        text-align: left !important;
    }}
    
    .nav-button:hover {{
        background: linear-gradient(135deg, {COLORS['surface']} 0%, {COLORS['card_bg']} 100%) !important;
        border-color: {COLORS['medical_cyan']} !important;
        transform: translateX(8px) !important;
        box-shadow: 0 6px 20px rgba(0, 225, 255, 0.3) !important;
    }}
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 2px;
        background: {COLORS['surface']};
        padding: 0.5rem;
        border-radius: 10px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background-color: {COLORS['card_bg']};
        border-radius: 8px;
        padding: 1rem 1.5rem;
        border: none;
        font-weight: 500;
        color: {COLORS['text_secondary']};
        transition: all 0.3s ease;
    }}
    
    .stTabs [aria-selected="true"] {{
        background-color: {COLORS['medical_cyan']} !important;
        color: {COLORS['dark_navy']} !important;
        box-shadow: 0 4px 15px rgba(0, 225, 255, 0.4) !important;
        transform: translateY(-2px);
    }}
    
    /* Animations */
    @keyframes fadeInUp {{
        from {{
            opacity: 0;
            transform: translateY(30px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}
    
    @keyframes slideInUp {{
        from {{
            opacity: 0;
            transform: translateY(50px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}
    
    @keyframes slideInLeft {{
        from {{
            opacity: 0;
            transform: translateX(-50px);
        }}
        to {{
            opacity: 1;
            transform: translateX(0);
        }}
    }}
    
    @keyframes fadeIn {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}
    
    @keyframes shimmer {{
        0% {{ transform: translateX(-100%); }}
        100% {{ transform: translateX(100%); }}
    }}
    
    @keyframes pulse {{
        0%, 100% {{ transform: scale(1); }}
        50% {{ transform: scale(1.02); }}
    }}
    
    @keyframes expandWidth {{
        from {{ width: 0; }}
        to {{ width: 50px; }}
    }}
    
    /* Streamlit Element Overrides */
    .stMetric {{
        background: {COLORS['surface']};
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid {COLORS['card_bg']};
    }}
    
    .stAlert {{
        background: {COLORS['surface']};
        border: 1px solid {COLORS['card_bg']};
        border-radius: 10px;
    }}
    
    /* Login Page Specific Styles */
    .login-container {{
        background: linear-gradient(135deg, {COLORS['surface']} 0%, {COLORS['card_bg']} 100%);
        border-radius: 20px;
        padding: 3rem;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
        border: 1px solid {COLORS['medical_cyan']}33;
        position: relative;
        overflow: hidden;
    }}
    
    .login-container::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, {COLORS['medical_cyan']}, {COLORS['wellness_green']});
    }}
    
    .floating-input {{
        background: {COLORS['dark_navy']};
        border: 1px solid {COLORS['card_bg']};
        border-radius: 10px;
        padding: 1rem;
        color: {COLORS['text_primary']};
        transition: all 0.3s ease;
        margin-bottom: 1rem;
    }}
    
    .floating-input:focus {{
        border-color: {COLORS['medical_cyan']};
        box-shadow: 0 0 0 2px {COLORS['medical_cyan']}33;
        transform: translateY(-2px);
    }}
    
    /* Number Counting Animation */
    @keyframes countUp {{
        from {{ --num: 0; }}
        to {{ --num: var(--target); }}
    }}
    
    .counting-number {{
        animation: countUp 2s ease-out;
        counter-reset: num var(--num);
        font-variant-numeric: tabular-nums;
    }}
    
    .counting-number::after {{
        content: counter(num);
    }}
</style>
""", unsafe_allow_html=True)


# Check authentication - STOP HERE if not logged in
if not auth.check_auth():
    # Enhanced Login Page with Medical Theme
    st.markdown("""
    <div style='display: flex; justify-content: center; align-items: center; min-height: 100vh;'>
        <div class='login-container' style='max-width: 450px; width: 100%;'>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h1 style='color: {COLORS["text_primary"]}; font-size: 2.5rem; margin-bottom: 0.5rem;'>🏥</h1>
            <h2 style='color: {COLORS["text_primary"]}; margin-bottom: 0.5rem;'>Health Matrices </h2>
            <p style='color: {COLORS["text_labels"]}; font-size: 1.1rem;'>Premium Health Intelligence</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Animated gradient border
        st.markdown("""
        <div style='
            background: linear-gradient(135deg, #00e0ff, #00c9a7);
            padding: 2px;
            border-radius: 12px;
            margin-bottom: 2rem;
            animation: pulse 2s infinite;
        '>
            <div style='
                background: #0a1128;
                padding: 1.5rem;
                border-radius: 10px;
                text-align: center;
            '>
                <h3 style='color: #ffffff; margin-bottom: 0.5rem;'>Your Health Journey Starts Here</h3>
                <p style='color: #94a3b8; margin: 0;'>Transform Your Wellness</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    auth.show_login_signup()
    st.markdown("</div></div>", unsafe_allow_html=True)
    st.stop()

# ... (Keep all your existing functions exactly the same - load_user_profile, create_bmi_gauge, create_nutrient_chart, create_health_timeline)

def load_user_profile():
    """Load user data from database with proper error handling - NO CACHING"""
    try:
        # Try to load from database first
        if st.session_state.user_id:
            profile_data = load_user_profile_db(st.session_state.user_id)
            
            if profile_data and profile_data.get('Name') and profile_data.get('Name') != 'Guest User':
                # Extract and convert basic metrics
                name = profile_data.get('Name', 'Guest User')
                age = int(profile_data.get('Age', 25))
                height = float(profile_data.get('Height', 170))
                weight = float(profile_data.get('Weight', 65))
                gender = profile_data.get('Gender', 'Not specified')
                goal = profile_data.get('Goal', 'Maintain')
                
                # Calculate BMI
                height_m = height / 100
                bmi = round(weight / (height_m ** 2), 1)
                
                # Determine BMI category
                if bmi < 18.5:
                    bmi_category = "Underweight"
                    bmi_color = COLORS['medical_cyan']
                elif bmi < 25:
                    bmi_category = "Healthy"
                    bmi_color = COLORS['wellness_green']
                elif bmi < 30:
                    bmi_category = "Overweight"
                    bmi_color = COLORS['health_amber']
                else:
                    bmi_category = "Obese"
                    bmi_color = COLORS['medical_red']
                
                # Calculate daily calorie needs (simplified Harris-Benedict)
                if gender.lower() == "male":
                    bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
                else:
                    bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
                
                # Activity multiplier
                activity_multipliers = {
                    "Sedentary": 1.2,
                    "Lightly Active": 1.375,
                    "Moderately Active": 1.55,
                    "Very Active": 1.725
                }
                lifestyle = profile_data.get('Lifestyle', 'Moderately Active')
                activity_multiplier = activity_multipliers.get(lifestyle, 1.55)
                
                daily_calories = round(bmr * activity_multiplier)
                
                # Goal adjustment
                if goal.lower() == "lose":
                    daily_calories -= 500
                elif goal.lower() == "gain":
                    daily_calories += 500
                
                return {
                    'name': name,
                    'age': age,
                    'height': height,
                    'weight': weight,
                    'bmi': bmi,
                    'bmi_category': bmi_category,
                    'bmi_color': bmi_color,
                    'gender': gender,
                    'goal': goal,
                    'lifestyle': lifestyle,
                    'daily_calories': daily_calories,
                    'diet_preference': profile_data.get('Diet Preference', 'Mixed'),
                    'allergies': profile_data.get('Allergies', []),
                    'injuries': profile_data.get('Injuries', [])
                }
            
    except Exception as e:
        st.sidebar.error(f"Error loading profile: {str(e)}")
    
    # Return demo data if profile loading fails
    return {
        'name': 'Guest User',
        'age': 25,
        'height': 170,
        'weight': 65,
        'bmi': 22.5,
        'bmi_category': 'Healthy',
        'bmi_color': COLORS['wellness_green'],
        'gender': 'Not specified',
        'goal': 'Maintain',
        'lifestyle': 'Moderately Active',
        'daily_calories': 2200,
        'diet_preference': 'Mixed',
        'allergies': [],
        'injuries': []
    }

def create_bmi_gauge(bmi_value):
    """Create a BMI gauge chart with premium medical styling - FIXED COLOR ISSUE"""
    # Use solid colors without alpha transparency for Plotly
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=bmi_value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "BMI Score", 'font': {'size': 24, 'color': COLORS['text_primary'], 'family': "Arial"}},
        delta={'reference': 22, 'increasing': {'color': COLORS['medical_red']}, 'decreasing': {'color': COLORS['wellness_green']}},
        gauge={
            'axis': {'range': [None, 40], 'tickwidth': 2, 'tickcolor': COLORS['text_primary']},
            'bar': {'color': COLORS['medical_cyan'], 'thickness': 0.75},
            'bgcolor': COLORS['surface'],
            'borderwidth': 2,
            'bordercolor': COLORS['medical_cyan'],
            'steps': [
                {'range': [0, 18.5], 'color': '#4cc9f0'},      # Light blue for underweight
                {'range': [18.5, 25], 'color': '#2a9d8f'},    # Teal for healthy
                {'range': [25, 30], 'color': '#e9c46a'},      # Amber for overweight
                {'range': [30, 40], 'color': '#e76f51'}       # Coral for obese
            ],
            'threshold': {
                'line': {'color': COLORS['text_primary'], 'width': 4},
                'thickness': 0.75,
                'value': bmi_value
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=50, r=50, t=80, b=50),
        font={'color': COLORS['text_primary'], 'family': "Arial"},
        paper_bgcolor=COLORS['surface'],
        plot_bgcolor=COLORS['surface']
    )
    
    return fig


def create_nutrient_chart(user_data):
    """Create nutrient distribution chart using meal planner logic"""
    # Calculate ranges using the same logic as meal planner
    ranges = calculate_daily_ranges(user_data)
    
    # Use the midpoint of each range for display
    calories_mid = sum(ranges['Calories']) / 2
    protein_mid = sum(ranges['Protein']) / 2
    carbs_mid = sum(ranges['Carbs']) / 2
    fats_mid = sum(ranges['Fats']) / 2
    
    # Calculate percentages
    total_nutrient_cals = (protein_mid * 4) + (carbs_mid * 4) + (fats_mid * 9)
    
    protein_ratio = (protein_mid * 4) / total_nutrient_cals * 100
    carb_ratio = (carbs_mid * 4) / total_nutrient_cals * 100
    fat_ratio = (fats_mid * 9) / total_nutrient_cals * 100
    
    data = {
        'Nutrient': ['Protein', 'Carbs', 'Fats'],
        'Grams': [round(protein_mid), round(carbs_mid), round(fats_mid)],
        'Percentage': [round(protein_ratio, 1), round(carb_ratio, 1), round(fat_ratio, 1)],
        'Color': [COLORS['medical_cyan'], COLORS['health_amber'], COLORS['medical_red']]
    }
    
    df = pd.DataFrame(data)
    
    fig = px.pie(df, values='Percentage', names='Nutrient', 
                 color='Nutrient', color_discrete_map={
                     'Protein': COLORS['medical_cyan'],
                     'Carbs': COLORS['health_amber'],
                     'Fats': COLORS['medical_red']
                 })
    
    fig.update_traces(textposition='inside', textinfo='percent+label', 
                      marker=dict(line=dict(color=COLORS['surface'], width=2)))
    fig.update_layout(
        height=300,
        showlegend=False,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor=COLORS['surface'],
        font=dict(color=COLORS['text_primary'], family="Arial")
    )
    
    return fig, data

def create_health_timeline(user_data):
    """Create a mock health progress timeline with medical styling"""
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    weights = user_data['weight'] + np.random.normal(0, 0.5, 30).cumsum()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates, y=weights,
        mode='lines+markers',
        name='Weight Trend',
        line=dict(color=COLORS['medical_cyan'], width=4),
        marker=dict(size=6, color=COLORS['wellness_green'])
    ))
    
    fig.update_layout(
        title='30-Day Weight Trend',
        xaxis_title='Date',
        yaxis_title='Weight (kg)',
        height=300,
        plot_bgcolor=COLORS['surface'],
        paper_bgcolor=COLORS['surface'],
        font=dict(color=COLORS['text_primary'], family="Arial"),
        hoverlabel=dict(bgcolor=COLORS['card_bg'], font_size=12)
    )
    
    return fig


def calculate_daily_ranges(user_data):
    """Calculate daily nutrient ranges - SAME LOGIC AS MEAL PLANNER"""
    weight, height, age = user_data['weight'], user_data['height'], user_data['age']
    goal, lifestyle = user_data['goal'], user_data['lifestyle']
    gender = user_data['gender']
    
    # Calculate BMR (same as meal planner)
    if gender.lower() == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    
    # Activity multipliers (same as meal planner)
    multipliers = {
        "Sedentary": 1.2,
        "Lightly Active": 1.375, 
        "Moderately Active": 1.55,
        "Very Active": 1.725
    }
    
    tdee = bmr * multipliers.get(lifestyle, 1.55)
    
    # Goal adjustment (same as meal planner)
    if goal.lower() == "lose":
        tdee_range = (tdee - 500, tdee - 300)
    elif goal.lower() == "gain":
        tdee_range = (tdee + 300, tdee + 500)
    else:  # maintain
        tdee_range = (tdee - 200, tdee + 200)
    
    # Calculate nutrient ranges (same as meal planner)
    protein_range = (0.8 * weight, 1.8 * weight)
    carbs_range = (0.4 * tdee / 4, 0.6 * tdee / 4)
    fats_range = (0.2 * tdee / 9, 0.35 * tdee / 9)
    
    return {
        "Calories": tdee_range,
        "Protein": protein_range,
        "Carbs": carbs_range,
        "Fats": fats_range
    }

def get_daily_progress_targets(user_data):
    """Get daily progress targets that match meal planner ranges"""
    ranges = calculate_daily_ranges(user_data)
    
    # Use upper bound for targets to be more permissive
    calorie_target = ranges['Calories'][1]  # Use upper bound
    protein_target = ranges['Protein'][1]   # Use upper bound  
    carbs_target = ranges['Carbs'][1]       # Use upper bound
    fats_target = ranges['Fats'][1]         # Use upper bound
    
    return {
        "Calories": round(calorie_target),
        "Protein": round(protein_target),
        "Carbs": round(carbs_target),
        "Fats": round(fats_target),
        "Water": max(round(user_data['weight'] * 0.035), 2),  # Minimum 2L
        "Exercise": 60  # 60 minutes exercise target
    }

def get_todays_progress(user_id):
    """Get today's actual progress from database or session state"""
    # Try to get from session state first
    if 'daily_progress' in st.session_state:
        return st.session_state.daily_progress
    
    # Default progress (you can replace this with database calls)
    return {
        "Calories": 0,
        "Protein": 0,
        "Carbs": 0,
        "Fats": 0,
        "Water": 0,
        "Exercise": 0
    }

def update_progress(nutrient, amount):
    """Update progress for a specific nutrient with validation"""
    if 'daily_progress' not in st.session_state:
        st.session_state.daily_progress = get_todays_progress(st.session_state.user_id)
    
    # Get current targets
    user_data = load_user_profile()
    targets = get_daily_progress_targets(user_data)
    
    current_value = st.session_state.daily_progress.get(nutrient, 0)
    target_value = targets.get(nutrient, 0)
    
    # Calculate new value
    new_value = current_value + amount
    
    # Validate limits
    if new_value > target_value * 1.2:  # Allow 20% over target with warning
        st.warning(f"⚠️ {nutrient} intake ({new_value:.0f}) exceeds your target ({target_value:.0f}) by more than 20%!")
        # Cap at 120% of target
        st.session_state.daily_progress[nutrient] = target_value * 1.2
    elif new_value > target_value:
        st.info(f"ℹ️ {nutrient} intake ({new_value:.0f}) exceeds your target ({target_value:.0f})")
        st.session_state.daily_progress[nutrient] = new_value
    else:
        st.session_state.daily_progress[nutrient] = new_value

def get_progress_status(nutrient, current, target):
    """Get status and color for progress display"""
    if target == 0:
        return "No target", COLORS['text_labels']
    
    percentage = (current / target) * 100
    
    if percentage <= 80:
        return "Below Target", COLORS['medical_cyan']
    elif percentage <= 100:
        return "On Target", COLORS['wellness_green']
    elif percentage <= 120:
        return "Slightly Over", COLORS['health_amber']
    else:
        return "Significantly Over", COLORS['medical_red']

def create_progress_display(user_data):
    """Create progress display with proper validation"""
    # Get targets and current progress
    targets = get_daily_progress_targets(user_data)
    current = get_todays_progress(st.session_state.user_id)
    
    progress_data = [
        ("Calories", current["Calories"], targets["Calories"], "kcal"),
        ("Protein", current["Protein"], targets["Protein"], "g"),
        ("Carbs", current["Carbs"], targets["Carbs"], "g"), 
        ("Fats", current["Fats"], targets["Fats"], "g"),
        ("Water", current["Water"], targets["Water"], "L"),
        ("Exercise", current["Exercise"], targets["Exercise"], "min")
    ]
    
    for label, current_val, target_val, unit in progress_data:
        # Get status and color
        status, color = get_progress_status(label, current_val, target_val)
        
        # Calculate progress percentage (capped at 120% for display)
        progress_pct = min(current_val / target_val, 1.2) if target_val > 0 else 0
        display_pct = min(progress_pct, 1.0)  # Cap at 100% for bar display
        
        st.write(f"**{label}** - *{status}*")
        
        # Progress bar (shows up to 100%, but text shows actual)
        progress_html = f"""
        <div class="progress-container">
            <div class="progress-fill" style="width: {display_pct * 100}%; background: {color};">
                {current_val:.0f}/{target_val:.0f} {unit} ({min(progress_pct * 100, 120):.0f}%)
            </div>
        </div>
        """
        st.markdown(progress_html, unsafe_allow_html=True)
        
        # Show warning if significantly over target
        if progress_pct > 1.0:
            overage_pct = (progress_pct - 1.0) * 100
            if overage_pct > 20:
                st.error(f"🚨 {label} is {overage_pct:.0f}% over target!")
            elif overage_pct > 0:
                st.warning(f"⚠️ {label} is {overage_pct:.0f}% over target")

def reset_daily_progress():
    """Reset daily progress with confirmation"""
    if st.button("🔄 Start New Day", use_container_width=True):
        st.session_state.daily_progress = {
            "Calories": 0,
            "Protein": 0,
            "Carbs": 0, 
            "Fats": 0,
            "Water": 0,
            "Exercise": 0
        }
        st.success("✅ Daily progress reset! Ready for a new day.")
        st.rerun()

def sync_meal_planner_progress(selected_meals):
    """Sync progress from meal planner selections with validation"""
    if 'daily_progress' not in st.session_state:
        st.session_state.daily_progress = get_todays_progress(st.session_state.user_id)
    
    total_calories = 0
    total_protein = 0
    total_carbs = 0
    total_fats = 0
    
    # Calculate totals from selected meals
    for meal, items in selected_meals.items():
        for item in items:
            qty = item.get('Quantity', 100)
            total_calories += item['Calories'] * qty / 100
            total_protein += item['Protein'] * qty / 100
            total_carbs += item['Carbs'] * qty / 100
            total_fats += item['Fats'] * qty / 100
    
    # Get current targets for validation
    user_data = load_user_profile()
    targets = get_daily_progress_targets(user_data)
    
    # Validate and update progress
    nutrients_to_update = {
        "Calories": total_calories,
        "Protein": total_protein, 
        "Carbs": total_carbs,
        "Fats": total_fats
    }
    
    over_target_nutrients = []
    
    for nutrient, value in nutrients_to_update.items():
        target = targets.get(nutrient, 0)
        if value > target * 1.2:
            # Cap at 120% of target
            st.session_state.daily_progress[nutrient] = target * 1.2
            over_target_nutrients.append(f"{nutrient} ({value:.0f} vs target {target:.0f})")
        elif value > target:
            st.session_state.daily_progress[nutrient] = value
            over_target_nutrients.append(f"{nutrient} ({value:.0f} vs target {target:.0f})")
        else:
            st.session_state.daily_progress[nutrient] = value
    
    # Show summary warnings
    if over_target_nutrients:
        st.warning(f"⚠️ The following nutrients exceed targets: {', '.join(over_target_nutrients)}")
# Initialize session state for navigation
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"

# Initialize daily progress tracking
if 'daily_progress' not in st.session_state:
    st.session_state.daily_progress = get_todays_progress(st.session_state.user_id if 'user_id' in st.session_state else None)

# Load data
@st.cache_data
def load_food_data():
    return pd.read_csv("data/foods.csv")

# Load user data
user = load_user_profile()
foods = load_food_data()

# Premium Medical Sidebar Navigation
with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-header">
        <h2 style="color: {COLORS['text_primary']}; margin: 0; font-size: 1.6rem; font-weight: 700;">🏥 Health Matrices</h2>
        <p style="opacity: 0.9; margin: 0.5rem 0 0 0; color: {COLORS['text_labels']}; font-size: 0.9rem; font-weight: 500;">
        Premium Health Intelligence</p>
    </div>
    """, unsafe_allow_html=True)
    
    # User info section with pulsing animation
    st.markdown(f"""
    <div class="user-welcome">
        <h4 style="margin: 0 0 0.8rem 0; color: {COLORS['text_primary']}; font-size: 1.1rem; font-weight: 600;">
        👋 Welcome, {user['name']}!</h4>
        <p style="margin: 0.3rem 0; color: {COLORS['text_secondary']}; font-size: 0.85rem; font-weight: 500;">
        <strong>BMI:</strong> {user['bmi']} ({user['bmi_category']})</p>
        <p style="margin: 0.3rem 0; color: {COLORS['text_secondary']}; font-size: 0.85rem; font-weight: 500;">
        <strong>Goal:</strong> {user['goal']} • <strong>Lifestyle:</strong> {user['lifestyle']}</p>
    </div>
    """, unsafe_allow_html=True)    

    # Logout button
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.rerun()
    
    st.markdown("---")
    
    # Premium Navigation
    st.markdown("### 🧭 Navigation")

    nav_options = {
        "🏠 Dashboard": "dashboard",
        "👤 Profile": "profile", 
        "🍽 Nutrition Hub": "nutrition_hub",
        "💪 Exercise & Fitness": "exercise_fitness",
        "📅 Routine Optimizer": "routine_optimizer",
        "🤖 Health Assistant": "health_assistant_page",  # Changed from "health_assistant"
        "⭐ Pro Features": "pro_features",
        "🔧 Admin": "admin"
    }

    for display_name, page_key in nav_options.items():
        if st.button(display_name, key=f"nav_btn_{page_key}", use_container_width=True):
            st.session_state.current_page = page_key

# Dashboard Page with Enhanced Medical Theme
if st.session_state.current_page == "dashboard":
    # Header with medical theme
    st.markdown('<h1 class="main-header">Health Matrices</h1>', unsafe_allow_html=True)
    
    # Welcome message
    if user['name'] == 'Guest User':
        st.warning("""
        ⚠ *Complete Your Profile* - You are viewing demo data. 
        Please create or update your profile in the Profile section to unlock personalized health insights and recommendations!
        """)
    else:
        st.success(f"""
        🎉 *Welcome back, {user['name']}!* Ready to continue your health journey?
        Today's Focus: {user['goal']} weight • Lifestyle: {user['lifestyle']}
        """)
    
    # Health Metrics Overview - Enhanced Medical Cards
    st.markdown(f'<h2 class="section-header">📊 Your Health Overview</h2>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card metric-card-bmi">
            <h3>🏥 BMI Score</h3>
            <h2 style="color: {user['bmi_color']};">{user['bmi']}</h2>
            <p>{user['bmi_category']}</p>
            <div style="margin-top: 0.8rem; padding: 0.4rem 0.8rem; background: rgba(255,255,255,0.1); border-radius: 8px; font-size: 0.8rem; color: {COLORS['text_labels']};">
                📈 Health Indicator
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card metric-card-age">
            <h3>🎂 Age</h3>
            <h2>{user['age']}</h2>
            <p>Years</p>
            <div style="margin-top: 0.8rem; padding: 0.4rem 0.8rem; background: rgba(255,255,255,0.1); border-radius: 8px; font-size: 0.8rem; color: {COLORS['text_labels']};">
                👤 Demographic
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card metric-card-weight">
            <h3>⚖ Weight</h3>
            <h2>{user['weight']}</h2>
            <p>kg</p>
            <div style="margin-top: 0.8rem; padding: 0.4rem 0.8rem; background: rgba(255,255,255,0.1); border-radius: 8px; font-size: 0.8rem; color: {COLORS['text_labels']};">
                🎯 {user['goal'].title()} Goal
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card metric-card-height">
            <h3>📏 Height</h3>
            <h2>{user['height']}</h2>
            <p>cm</p>
            <div style="margin-top: 0.8rem; padding: 0.4rem 0.8rem; background: rgba(255,255,255,0.1); border-radius: 8px; font-size: 0.8rem; color: {COLORS['text_labels']};">
                📊 Anthropometry
            </div>
        </div>
        """, unsafe_allow_html=True)    
    
    # Health Insights Section with Enhanced Visualizations
    st.markdown(f'<h2 class="section-header">💡 Advanced Health Analytics</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # BMI Gauge Chart
        st.markdown("""
        <div class="insight-card">
            <h4 style="color: #ffffff; margin-bottom: 1.5rem; font-size: 1.3rem;">📈 BMI Analysis</h4>
        """, unsafe_allow_html=True)
        
        bmi_gauge = create_bmi_gauge(user['bmi'])
        st.plotly_chart(bmi_gauge, use_container_width=True)
        
        # BMI Status with color coding
        bmi_status_config = {
            "Underweight": ("🔵", "info", "Consider nutritional consultation"),
            "Healthy": ("🟢", "success", "Excellent! Maintain your lifestyle"),
            "Overweight": ("🟡", "warning", "Consider lifestyle adjustments"),
            "Obese": ("🔴", "error", "Consult healthcare provider")
        }
        
        icon, status_type, message = bmi_status_config.get(user['bmi_category'], ("⚪", "info", ""))
        if status_type == "success":
            st.success(f"{icon} {user['bmi_category']} - {message}")
        elif status_type == "warning":
            st.warning(f"{icon} {user['bmi_category']} - {message}")
        elif status_type == "error":
            st.error(f"{icon} {user['bmi_category']} - {message}")
        else:
            st.info(f"{icon} {user['bmi_category']} - {message}")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Health Timeline
        st.markdown("""
        <div class="insight-card">
            <h4 style="color: #ffffff; margin-bottom: 1.5rem; font-size: 1.3rem;">📅 Health Progress</h4>
        """, unsafe_allow_html=True)
        
        timeline_chart = create_health_timeline(user)
        st.plotly_chart(timeline_chart, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        # Nutrient Distribution
        st.markdown("""
        <div class="insight-card">
            <h4 style="color: #ffffff; margin-bottom: 1.5rem; font-size: 1.3rem;">🍽 Daily Nutrition Plan</h4>
        """, unsafe_allow_html=True)
        
        nutrient_chart, nutrient_data = create_nutrient_chart(user)
        st.plotly_chart(nutrient_chart, use_container_width=True)
        
        # Display nutrient details with animated progress
        st.write("*Daily Targets:*")
        for nutrient in nutrient_data['Nutrient']:
            idx = nutrient_data['Nutrient'].index(nutrient)
            st.write(f"• *{nutrient}:* {nutrient_data['Grams'][idx]}g ({nutrient_data['Percentage'][idx]:.1f}%)")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Calorie Goals with animated progress
        st.markdown("""
        <div class="insight-card">
            <h4 style="color: #ffffff; margin-bottom: 1.5rem; font-size: 1.3rem;">🎯 Daily Calorie Target</h4>
        """, unsafe_allow_html=True)
        
        # Get consistent targets that match meal planner FIRST
        progress_targets = get_daily_progress_targets(user)
        
        # Get today's actual progress
        todays_progress = get_todays_progress(st.session_state.user_id)
        
        st.metric("Recommended Daily Intake", f"{progress_targets['Calories']} kcal", 
                 f"For {user['goal']} goal • {user['lifestyle']}")
        
        # Today's Progress with proper validation
        st.write("*Today's Progress:*")

        # Use the new progress display function
        create_progress_display(user)
        
        # Add quick update buttons for manual tracking
        st.write("**Quick Update:**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🍽 Add Meal", use_container_width=True):
                # This would ideally come from your meal planner
                # For now, using sample values
                update_progress("Calories", 500)
                update_progress("Protein", 25)
                update_progress("Carbs", 60)
                update_progress("Fats", 15)
                st.rerun()
        
        with col2:
            if st.button("💧 Add Water", use_container_width=True):
                update_progress("Water", 1)  # 1 liter
                st.rerun()
        
        with col3:
            if st.button("🏃 Add Exercise", use_container_width=True):
                update_progress("Exercise", 30)  # 30 minutes
                st.rerun()
        
        # Reset button for new day
        # Reset progress with the new function
        reset_daily_progress()
    
    # Quick Access Features with Enhanced Cards
    st.markdown(f'<h2 class="section-header">🚀 Quick Access</h2>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="feature-card">
            <div>
                <h4 style="color: {COLORS['text_primary']}; margin-bottom: 1rem; font-size: 1.3rem;">🍽 Nutrition Hub</h4>
                <p style="color: {COLORS['text_secondary']}; margin: 0; line-height: 1.6;">All food-related features in one place: search foods, get recommendations, and plan full-day meals.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Explore Nutrition →", key="goto_nutrition", use_container_width=True):
            st.session_state.current_page = "nutrition_hub"
            st.rerun()
        
        st.markdown(f"""
        <div class="feature-card">
            <div>
                <h4 style="color: {COLORS['text_primary']}; margin-bottom: 1rem; font-size: 1.3rem;">💪 Exercise & Fitness</h4>
                <p style="color: {COLORS['text_secondary']}; margin: 0; line-height: 1.6;">Smart exercise recommendations based on your performance, mood, and health data.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Start Your Workout →", key="goto_exercise", use_container_width=True):
            st.session_state.current_page = "exercise_fitness"
            st.rerun()
    
    with col2:
        st.markdown(f"""
        <div class="feature-card">
            <div>
                <h4 style="color: {COLORS['text_primary']}; margin-bottom: 1rem; font-size: 1.3rem;">📅 Routine Optimizer</h4>
                <p style="color: {COLORS['text_secondary']}; margin: 0; line-height: 1.6;">Optimize your free time with AI-powered scheduling for meals, exercise, and rest.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Optimize Your Day →", key="goto_routine", use_container_width=True):
            st.session_state.current_page = "routine_optimizer"
            st.rerun()
        
        st.markdown(f"""
        <div class="feature-card">
            <div>
                <h4 style="color: {COLORS['text_primary']}; margin-bottom: 1rem; font-size: 1.3rem;">🤖 Health Assistant</h4>
                <p style="color: {COLORS['text_secondary']}; margin: 0; line-height: 1.6;">Chat with our AI health assistant for personalized support and guidance.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Chat with Assistant →", key="goto_assistant", use_container_width=True):
            st.session_state.current_page = "health_assistant"
            st.rerun()

# Profile Page
elif st.session_state.current_page == "profile":
    st.markdown('<h1 class="main-header">👤 Profile Management</h1>', unsafe_allow_html=True)
    create_or_edit_profile()

# Nutrition Hub - Combined Food Features
elif st.session_state.current_page == "nutrition_hub":
    st.markdown('<h1 class="main-header">🍽 Nutrition Hub</h1>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🔍 Food Search", "💡 Food Recommender", "📅 Full-Day Planner"])
    
    with tab1:
        search_food_ui()
    
    with tab2:
        food_recommender_ui(st, foods)
    
    with tab3:
        if user['name'] == 'Guest User':
            st.warning("⚠ Please create or load your profile first to use the meal planner.")
            if st.button("Go to Profile →", use_container_width=True):
                st.session_state.current_page = "profile"
                st.rerun()
        else:
            compatible_user = {
                'Weight': user['weight'],
                'Height': user['height'], 
                'Age': user['age'],
                'Goal': user['goal'],
                'Lifestyle': user['lifestyle'],
                'Gender': user['gender'],
                'Diet Preference': user['diet_preference'],
                'Allergies': user['allergies']
            }
            # Call meal planner and sync progress
            full_day_meal_planner_ui(compatible_user, foods)
            
            # Sync progress when meal plan is created
            if 'selected_meals' in st.session_state and st.session_state['selected_meals']:
                sync_meal_planner_progress(st.session_state['selected_meals'])

# Exercise & Fitness Page
elif st.session_state.current_page == "exercise_fitness":
    st.markdown('<h1 class="main-header">💪 Exercise & Fitness</h1>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🎯 Quick Workout Generator", "🔍 Exercise Database"])
    
    with tab1:
        workout_generator_ui()
    
    with tab2:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("🏋 Exercise Database")
            search_exercise_ui()
        
        with col2:
            st.subheader("🎯 Smart Recommendations")
            st.info("AI-powered exercise suggestions based on your profile!")
            
            # Load user data for recommendations
            user = load_user_profile()
            st.write("*Based on your profile:*")
            st.write(f"• Goal: {user['goal']}")
            st.write(f"• Lifestyle: {user['lifestyle']}")
            st.write(f"• BMI: {user['bmi']} ({user['bmi_category']})")
            
            if user['goal'].lower() == 'lose':
                st.success("💡 Recommended: Cardio exercises + Strength training")
                st.write("• 30-45 min cardio sessions")
                st.write("• Full body strength workouts")
            elif user['goal'].lower() == 'gain':
                st.success("💡 Recommended: Strength training + High-protein diet")
                st.write("• Heavy compound exercises")
                st.write("• Progressive overload")
            else:
                st.success("💡 Recommended: Balanced workout routine")
                st.write("• Mix of cardio and strength")
                st.write("• Flexibility training")

# Routine Optimizer Page

elif st.session_state.current_page == "routine_optimizer":
    st.markdown('<h1 class="main-header">📅 Routine Optimizer</h1>', unsafe_allow_html=True)
    routine_optimizer_ui(user)


# Health Assistant Page  
elif st.session_state.current_page == "health_assistant_page":
    st.markdown('<h1 class="main-header">🤖 Health Assistant</h1>', unsafe_allow_html=True)
    
    # Clear any corrupted session state
    if 'health_assistant' in st.session_state:
        # Check if it's a widget conflict and clear it
        if not hasattr(st.session_state.health_assistant, 'process_message'):
            del st.session_state.health_assistant
    
    # Import and render the health assistant
    try:
        from health_assistant import show_health_assistant
        show_health_assistant()
    except Exception as e:
        st.error(f"Error loading health assistant: {str(e)}")
        st.info("Please try refreshing the page or use the reset button below.")
        
        if st.button("Reset Health Assistant", key="reset_assistant_btn"):
            keys_to_clear = ['health_assistant', 'health_chat_history', 'show_health_initial_greeting']
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
            

# Pro Features Page
elif st.session_state.current_page == "pro_features":
    st.markdown('<h1 class="main-header">⭐ Pro Features</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🚀 Premium Benefits")
        
        features = [
            ("🎯 Personalized Coaching", "AI-powered daily coaching sessions"),
            ("📊 Advanced Analytics", "Deep health insights and trends"),
            ("🍽 Custom Meal Plans", "Weekly customized nutrition plans"),
            ("💪 Workout Programs", "Personalized exercise regimens"),
            ("📱 Priority Support", "24/7 dedicated assistance"),
            ("📈 Progress Tracking", "Detailed performance analytics")
        ]
        
        for feature, description in features:
            with st.expander(feature):
                st.write(description)
    
    with col2:
        st.subheader("Upgrade to Pro")
        
        st.info("Unlock the full potential of your health journey!")
        
        st.write("*Pro Membership Includes:*")
        st.write("• AI Health Coach")
        st.write("• Advanced Workout Plans") 
        st.write("• Custom Nutrition Strategies")
        st.write("• Priority Feature Access")
        
        st.warning("Pro features coming soon!")
        
        # Placeholder for upgrade button
        if st.button("🚀 Upgrade to Pro", use_container_width=True, disabled=True):
            st.success("Welcome to Health Matrices Pro!")

# Admin Page
elif st.session_state.current_page == "admin":
    st.markdown('<h1 class="main-header">🔧 Admin Panel</h1>', unsafe_allow_html=True)
    
    import sqlite3
    
    # SIMPLE ADMIN CHECK - Only specific usernames can access
    ADMIN_USERS = ["admin", "Palak"]  
    if st.session_state.username in ADMIN_USERS:
        st.success(f"✅ Welcome, {st.session_state.username}!")
        
        # Show user statistics
        stats = db.get_user_stats()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Users", stats.get('total_users', 0))
        with col2:
            st.metric("Total Profiles", stats.get('total_profiles', 0))
        with col3:
            st.metric("Latest User", stats.get('latest_user', 'None'))
        
        tab1, tab2 = st.tabs(["👥 All Users", "📊 User Profiles"])
        
        with tab1:
            st.subheader("All Registered Users")
            try:
                users = db.get_all_users()
                if users:
                    users_data = []
                    for user in users:
                        users_data.append({
                            'ID': user[0],
                            'Username': user[1],
                            'Email': user[2] or 'Not provided',
                            'Signup Date': user[3],
                            'Has Profile': '✅' if user[4] else '❌'
                        })
                    
                    users_df = pd.DataFrame(users_data)
                    st.dataframe(users_df, use_container_width=True)
                    
                    st.info(f"*Total registered users: {len(users)}*")
                    
                    csv = users_df.to_csv(index=False)
                    st.download_button(
                        "📥 Download Users List", 
                        csv, 
                        "registered_users.csv",
                        use_container_width=True
                    )
                else:
                    st.info("No users found in the system.")
                    
            except Exception as e:
                st.error(f"Error loading users: {str(e)}")
        
        with tab2:
            st.subheader("All User Profiles")
            try:
                conn = sqlite3.connect('health_app.db')
                profiles_df = pd.read_sql_query('''
                    SELECT u.username, up.name, up.age, up.gender, up.goal, 
                           up.lifestyle, up.diet_preference, up.created_at
                    FROM user_profiles up 
                    JOIN users u ON up.user_id = u.id
                    ORDER BY up.created_at DESC
                ''', conn)
                conn.close()
                
                if not profiles_df.empty:
                    st.dataframe(profiles_df, use_container_width=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total Profiles", len(profiles_df))
                    with col2:
                        if 'age' in profiles_df.columns:
                            avg_age = profiles_df['age'].mean()
                            st.metric("Average Age", f"{avg_age:.1f} years")
                    
                    csv = profiles_df.to_csv(index=False)
                    st.download_button(
                        "📥 Download Profiles", 
                        csv, 
                        "user_profiles.csv",
                        use_container_width=True
                    )
                else:
                    st.info("No user profiles found.")
                    
            except Exception as e:
                st.error(f"Error loading profiles: {str(e)}")
    
    else:
        st.error("🚫 Access Denied - Admin Privileges Required")
        st.info("This section is only accessible to administrators.")
        
        if st.session_state.logged_in:
            st.write(f"Current user: {st.session_state.username}")
        else:
            st.write("Please log in with an admin account.")
        
        if st.button("🔙 Go Back to Dashboard", use_container_width=True):
            st.session_state.current_page = "dashboard"
            st.rerun()

# Enhanced Footer
st.markdown("---")
st.markdown(
    f"<div style='text-align: center; color: {COLORS['text_primary']}; padding: 3rem; background: {COLORS['surface']}; border-radius: 15px; margin-top: 3rem; border: 1px solid {COLORS['card_bg']};'>"
    "<p style='margin: 0; font-size: 1rem; font-weight: 600;'>🏥 Health Matrices • Your Health Journey Starts Here • Transform Your Wellness</p>"
    "<p style='margin: 0.5rem 0 0 0; font-size: 0.9rem; color: #94a3b8;'>Premium Health Intelligence Platform</p>"
    "</div>",
    unsafe_allow_html=True
)