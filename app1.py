import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import os

from user_profile import create_or_edit_profile
from food import search_food_ui
from exercise import search_exercise_ui
from food_recommender import food_recommender_ui
from full_day_meal_planner import full_day_meal_planner_ui
from utils import load_profile, save_profile

# Page configuration
st.set_page_config(
    page_title="Health Matrices Pro",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Medical Color Palette
COLORS = {
    "dark_blue": "#131a2f",
    "medium_blue": "#264493", 
    "light_blue": "#11a2d7",
    "light_bg": "#e5f3fa",
    "white": "#ffffff",
    "off_white": "#f8fafc",
    "light_green": "#10b981",
    "pink": "#ec4899",
    "yellow": "#f59e0b",
    "purple": "#8b5cf6"
}

# Custom CSS for medical professional styling
st.markdown(f"""
<style>
    .main-header {{
        font-size: 2.8rem;
        color: #ffffff;
        background: linear-gradient(135deg, {COLORS['dark_blue']} 0%, {COLORS['medium_blue']} 100%);
        padding: 2.5rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 800;
        box-shadow: 0 8px 25px rgba(19, 26, 47, 0.3);
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }}
    .metric-card {{ 
        background: linear-gradient(135deg, {COLORS['medium_blue']} 0%, {COLORS['light_blue']} 100%);
        padding: 2rem;
        border-radius: 16px;
        color: white;
        text-align: center;
        box-shadow: 0 6px 20px rgba(38, 68, 147, 0.4);
        margin: 0.5rem;
        border: 2px solid {COLORS['light_blue']};
        transition: transform 0.3s ease;
    }}
    .metric-card:hover {{
        transform: translateY(-5px);
    }}
    .metric-card-age {{
        background: linear-gradient(135deg, {COLORS['light_green']} 0%, #34d399 100%);
        padding: 2rem;
        border-radius: 16px;
        color: white;
        text-align: center;
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
        margin: 0.5rem;
        border: 2px solid #34d399;
        transition: transform 0.3s ease;
    }}
    .metric-card-weight {{
        background: linear-gradient(135deg, {COLORS['pink']} 0%, #f472b6 100%);
        padding: 2rem;
        border-radius: 16px;
        color: white;
        text-align: center;
        box-shadow: 0 6px 20px rgba(236, 72, 153, 0.4);
        margin: 0.5rem;
        border: 2px solid #f472b6;
        transition: transform 0.3s ease;
    }}
    .metric-card-height {{
        background: linear-gradient(135deg, {COLORS['yellow']} 0%, #fbbf24 100%);
        padding: 2rem;
        border-radius: 16px;
        color: white;
        text-align: center;
        box-shadow: 0 6px 20px rgba(245, 158, 11, 0.4);
        margin: 0.5rem;
        border: 2px solid #fbbf24;
        transition: transform 0.3s ease;
    }}
    .metric-card h3 {{
        font-size: 1.1rem;
        margin: 0 0 1rem 0;
        opacity: 0.95;
        font-weight: 600;
        letter-spacing: 0.5px;
    }}
    .metric-card h2 {{
        font-size: 2.5rem;
        margin: 1rem 0;
        font-weight: 800;
    }}
    .metric-card p {{
        margin: 0;
        font-size: 1rem;
        opacity: 0.95;
        font-weight: 500;
    }}
    .insight-card {{
        background: {COLORS['white']};
        padding: 2rem;
        border-radius: 16px;
        border-left: 6px solid {COLORS['light_blue']};
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        margin: 1.5rem 0;
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
    }}
    .insight-card:hover {{
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }}
    .feature-card {{
        background: {COLORS['white']};
        padding: 2rem;
        border-radius: 16px;
        border: 2px solid #e2e8f0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        margin: 1.5rem 0;
        transition: all 0.3s ease;
        min-height: 220px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }}
    .feature-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
        border-color: {COLORS['light_blue']};
    }}
    .sidebar-header {{
        background: linear-gradient(135deg, {COLORS['dark_blue']} 0%, {COLORS['medium_blue']} 100%);
        padding: 2rem;
        border-radius: 0 0 20px 20px;
        color: white;
        text-align: center;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }}
    .user-welcome {{
        background: {COLORS['light_bg']};
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid {COLORS['light_blue']};
        margin: 1.5rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }}
    .stButton button {{
        background: linear-gradient(135deg, {COLORS['medium_blue']} 0%, {COLORS['light_blue']} 100%);
        color: white;
        border: none;
        padding: 1rem 2rem;
        border-radius: 12px;
        font-weight: 700;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(30, 64, 175, 0.3);
    }}
    .stButton button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(17, 162, 215, 0.4);
    }}
    .section-header {{
        color: {COLORS['dark_blue']};
        border-bottom: 3px solid {COLORS['light_blue']};
        padding-bottom: 1rem;
        margin: 3rem 0 2rem 0;
        font-size: 1.8rem;
        font-weight: 700;
    }}
    .progress-container {{
        background: {COLORS['light_bg']};
        border-radius: 12px;
        margin: 1rem 0;
        padding: 0.5rem;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
    }}
    .progress-fill {{
        background: linear-gradient(90deg, {COLORS['light_blue']} 0%, {COLORS['medium_blue']} 100%);
        height: 25px;
        border-radius: 8px;
        text-align: center;
        color: white;
        font-size: 0.9rem;
        line-height: 25px;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(17, 162, 215, 0.3);
    }}
</style>
""", unsafe_allow_html=True)

def load_user_profile():
    """Load user data from profile.csv with proper error handling"""
    try:
        # Try multiple methods to load the profile
        profile_df = load_profile()
        
        if not profile_df.empty and 'Name' in profile_df.columns:
            user_data = profile_df.iloc[0].to_dict()
            
            # Extract and convert basic metrics
            name = user_data.get('Name', 'Guest User')
            age = int(user_data.get('Age', 25))
            height = float(user_data.get('Height', 170))
            weight = float(user_data.get('Weight', 65))
            gender = user_data.get('Gender', 'Not specified')
            goal = user_data.get('Goal', 'Maintain')
            
            # Calculate BMI
            height_m = height / 100
            bmi = round(weight / (height_m ** 2), 1)
            
            # Determine BMI category
            if bmi < 18.5:
                bmi_category = "Underweight"
                bmi_color = "#60a5fa"  # Blue
            elif bmi < 25:
                bmi_category = "Healthy"
                bmi_color = "#34d399"  # Green
            elif bmi < 30:
                bmi_category = "Overweight"
                bmi_color = "#fbbf24"  # Yellow
            else:
                bmi_category = "Obese"
                bmi_color = "#f87171"  # Red
            
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
            lifestyle = user_data.get('Lifestyle', 'Moderately Active')
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
                'diet_preference': user_data.get('Diet Preference', 'Mixed'),
                'allergies': user_data.get('Allergies', []),
                'injuries': user_data.get('Injuries', [])
            }
        else:
            st.sidebar.warning("Profile file is empty or has incorrect format")
            
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
        'bmi_color': '#34d399',
        'gender': 'Not specified',
        'goal': 'Maintain',
        'lifestyle': 'Moderately Active',
        'daily_calories': 2200,
        'diet_preference': 'Mixed',
        'allergies': [],
        'injuries': []
    }

def create_bmi_gauge(bmi_value):
    """Create a BMI gauge chart"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = bmi_value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "BMI Score", 'font': {'size': 24, 'color': COLORS['dark_blue']}},
        delta = {'reference': 22, 'increasing': {'color': COLORS['pink']}, 'decreasing': {'color': COLORS['light_green']}},
        gauge = {
            'axis': {'range': [None, 40], 'tickwidth': 2, 'tickcolor': COLORS['dark_blue']},
            'bar': {'color': COLORS['medium_blue'], 'thickness': 0.75},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': COLORS['light_blue'],
            'steps': [
                {'range': [0, 18.5], 'color': '#dbeafe'},
                {'range': [18.5, 25], 'color': '#dcfce7'},
                {'range': [25, 30], 'color': '#fef3c7'},
                {'range': [30, 40], 'color': '#fee2e2'}
            ],
            'threshold': {
                'line': {'color': COLORS['dark_blue'], 'width': 4},
                'thickness': 0.75,
                'value': bmi_value
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=50, r=50, t=80, b=50),
        font={'color': COLORS['dark_blue'], 'family': "Arial"},
        paper_bgcolor=COLORS['light_bg']
    )
    
    return fig

def create_nutrient_chart(user_data):
    """Create nutrient distribution chart"""
    # Calculate macronutrient distribution based on user goals
    calories = user_data['daily_calories']
    
    if user_data['goal'].lower() == 'lose':
        protein_ratio, carb_ratio, fat_ratio = 0.35, 0.40, 0.25
    elif user_data['goal'].lower() == 'gain':
        protein_ratio, carb_ratio, fat_ratio = 0.30, 0.50, 0.20
    else:  # maintain
        protein_ratio, carb_ratio, fat_ratio = 0.25, 0.45, 0.30
    
    protein_cals = calories * protein_ratio
    carb_cals = calories * carb_ratio
    fat_cals = calories * fat_ratio
    
    # Convert to grams
    protein_grams = round(protein_cals / 4)
    carb_grams = round(carb_cals / 4)
    fat_grams = round(fat_cals / 9)
    
    data = {
        'Nutrient': ['Protein', 'Carbs', 'Fats'],
        'Grams': [protein_grams, carb_grams, fat_grams],
        'Percentage': [protein_ratio*100, carb_ratio*100, fat_ratio*100],
        'Color': [COLORS['light_blue'], COLORS['light_green'], COLORS['yellow']]
    }
    
    df = pd.DataFrame(data)
    
    fig = px.pie(df, values='Percentage', names='Nutrient', 
                 color='Nutrient', color_discrete_map={
                     'Protein': COLORS['light_blue'],
                     'Carbs': COLORS['light_green'],
                     'Fats': COLORS['yellow']
                 })
    
    fig.update_traces(textposition='inside', textinfo='percent+label', 
                      marker=dict(line=dict(color=COLORS['white'], width=2)))
    fig.update_layout(
        height=300,
        showlegend=False,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor=COLORS['light_bg']
    )
    
    return fig, data

def create_health_timeline(user_data):
    """Create a mock health progress timeline"""
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    weights = user_data['weight'] + np.random.normal(0, 0.5, 30).cumsum()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates, y=weights,
        mode='lines+markers',
        name='Weight Trend',
        line=dict(color=COLORS['light_blue'], width=4),
        marker=dict(size=6, color=COLORS['medium_blue'])
    ))
    
    fig.update_layout(
        title='30-Day Weight Trend',
        xaxis_title='Date',
        yaxis_title='Weight (kg)',
        height=300,
        plot_bgcolor=COLORS['light_bg'],
        paper_bgcolor=COLORS['white'],
        font=dict(color=COLORS['dark_blue'])
    )
    
    return fig

# Initialize session state for navigation
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"

# Load data
@st.cache_data
def load_food_data():
    return pd.read_csv("data/foods.csv")

# Load user data
user = load_user_profile()
foods = load_food_data()

# Sidebar Navigation
with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-header">
        <h2 style="color: {COLORS['off_white']}; margin: 0; font-size: 1.8rem;">🏥 Health Matrices Pro</h2>
        <p style="opacity: 0.95; margin: 0.5rem 0 0 0; color: {COLORS['off_white']}; font-size: 1rem;">
        Your Personal Health Companion</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Refresh button
    if st.button("🔄 Refresh Profile Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    # User welcome section
    st.markdown(f"""
    <div class="user-welcome">
        <h4 style="margin: 0 0 0.8rem 0; color: {COLORS['dark_blue']}; font-size: 1.2rem;">
        👋 Welcome, {user['name']}!</h4>
        <p style="margin: 0.3rem 0; color: {COLORS['medium_blue']}; font-size: 0.95rem;">
        <strong>BMI:</strong> {user['bmi']} ({user['bmi_category']})</p>
        <p style="margin: 0.3rem 0; color: {COLORS['medium_blue']}; font-size: 0.95rem;">
        <strong>Goal:</strong> {user['goal']} • <strong>Lifestyle:</strong> {user['lifestyle']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation
    st.markdown("### 🧭 Navigation")
    
    nav_options = {
        "🏠 Dashboard": "dashboard",
        "👤 Profile": "profile", 
        "🍎 Food Search": "food_search",
        "💡 Food Recommender": "food_recommender",
        "🏋️ Exercise": "exercise",
        "📅 Full-Day Planner": "planner"
    }
    
    for display_name, page_key in nav_options.items():
        if st.button(display_name, key=page_key, use_container_width=True):
            st.session_state.current_page = page_key

# Dashboard Page
if st.session_state.current_page == "dashboard":
    # Header
    st.markdown('<h1 class="main-header">Health Matrices Pro</h1>', unsafe_allow_html=True)
    
    # Welcome message
    if user['name'] == 'Guest User':
        st.warning("""
        ⚠️ **Complete Your Profile** - You are viewing demo data. 
        Please create or update your profile in the Profile section to unlock personalized health insights and recommendations!
        """)
    else:
        st.success(f"""
        🎉 **Welcome back, {user['name']}!** Ready to continue your health journey?
        Today's Focus: {user['goal']} weight • Lifestyle: {user['lifestyle']}
        """)
    
    # Health Metrics Overview
    st.markdown(f'<h2 class="section-header">📊 Your Health Overview</h2>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>BMI</h3>
            <h2>{user['bmi']}</h2>
            <p>{user['bmi_category']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card-age">
            <h3>Age</h3>
            <h2>{user['age']}</h2>
            <p>Years</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card-weight">
            <h3>Weight</h3>
            <h2>{user['weight']}</h2>
            <p>kg</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card-height">
            <h3>Height</h3>
            <h2>{user['height']}</h2>
            <p>cm</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Health Insights Section with Visualizations
    st.markdown(f'<h2 class="section-header">💡 Advanced Health Analytics</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # BMI Gauge Chart
        st.markdown("""
        <div class="insight-card">
            <h4 style="color: #131a2f; margin-bottom: 1.5rem; font-size: 1.3rem;">📈 BMI Analysis</h4>
        """, unsafe_allow_html=True)
        
        bmi_gauge = create_bmi_gauge(user['bmi'])
        st.plotly_chart(bmi_gauge, use_container_width=True)
        
        # BMI Status
        if user['bmi_category'] == "Underweight":
            st.error(f"🔵 {user['bmi_category']} - Consider nutritional consultation")
        elif user['bmi_category'] == "Healthy":
            st.success(f"🟢 {user['bmi_category']} - Excellent! Maintain your lifestyle")
        elif user['bmi_category'] == "Overweight":
            st.warning(f"🟡 {user['bmi_category']} - Consider lifestyle adjustments")
        else:
            st.error(f"🔴 {user['bmi_category']} - Consult healthcare provider")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Health Timeline
        st.markdown("""
        <div class="insight-card">
            <h4 style="color: #131a2f; margin-bottom: 1.5rem; font-size: 1.3rem;">📅 Health Progress</h4>
        """, unsafe_allow_html=True)
        
        timeline_chart = create_health_timeline(user)
        st.plotly_chart(timeline_chart, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        # Nutrient Distribution
        st.markdown("""
        <div class="insight-card">
            <h4 style="color: #131a2f; margin-bottom: 1.5rem; font-size: 1.3rem;">🍽️ Daily Nutrition Plan</h4>
        """, unsafe_allow_html=True)
        
        nutrient_chart, nutrient_data = create_nutrient_chart(user)
        st.plotly_chart(nutrient_chart, use_container_width=True)
        
        # Display nutrient details
        st.write("**Daily Targets:**")
        for nutrient in nutrient_data['Nutrient']:
            idx = nutrient_data['Nutrient'].index(nutrient)
            st.write(f"• **{nutrient}:** {nutrient_data['Grams'][idx]}g ({nutrient_data['Percentage'][idx]:.1f}%)")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Calorie Goals
        st.markdown("""
        <div class="insight-card">
            <h4 style="color: #131a2f; margin-bottom: 1.5rem; font-size: 1.3rem;">🎯 Daily Calorie Target</h4>
        """, unsafe_allow_html=True)
        
        st.metric("Recommended Daily Intake", f"{user['daily_calories']} kcal", 
                 f"For {user['goal']} goal • {user['lifestyle']}")
        
        # Progress bars for daily tracking
        st.write("**Today's Progress:**")
        
        progress_data = [
            ("Calories", 1450, user['daily_calories'], COLORS['light_blue']),
            ("Protein", 55, nutrient_data['Grams'][0], COLORS['light_green']),
            ("Water", 6, 8, COLORS['medium_blue']),
            ("Exercise", 45, 60, COLORS['purple'])
        ]
        
        for label, current, target, color in progress_data:
            progress = min(current / target, 1.0)
            st.write(f"**{label}**")
            progress_html = f"""
            <div class="progress-container">
                <div class="progress-fill" style="width: {progress * 100}%; background: {color};">
                    {current}/{target}
                </div>
            </div>
            """
            st.markdown(progress_html, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Quick Access Features
    st.markdown(f'<h2 class="section-header">🚀 Quick Access</h2>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="feature-card">
            <div>
                <h4 style="color: {COLORS['dark_blue']}; margin-bottom: 1rem; font-size: 1.3rem;">🍎 Food Search</h4>
                <p style="color: #64748b; margin: 0; line-height: 1.6;">Search through our extensive food database with detailed nutritional information and make informed dietary choices.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Explore Food Database →", key="goto_food", use_container_width=True):
            st.session_state.current_page = "food_search"
        
        st.markdown(f"""
        <div class="feature-card">
            <div>
                <h4 style="color: {COLORS['dark_blue']}; margin-bottom: 1rem; font-size: 1.3rem;">💡 Food Recommender</h4>
                <p style="color: #64748b; margin: 0; line-height: 1.6;">Get AI-powered food recommendations based on your health goals, preferences, and nutritional needs.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Get Smart Recommendations →", key="goto_recommender", use_container_width=True):
            st.session_state.current_page = "food_recommender"
    
    with col2:
        st.markdown(f"""
        <div class="feature-card">
            <div>
                <h4 style="color: {COLORS['dark_blue']}; margin-bottom: 1rem; font-size: 1.3rem;">🏋️ Exercise Tracking</h4>
                <p style="color: #64748b; margin: 0; line-height: 1.6;">Browse exercises, create workout routines, and track your fitness progress with detailed analytics.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Start Your Workout →", key="goto_exercise", use_container_width=True):
            st.session_state.current_page = "exercise"
        
        st.markdown(f"""
        <div class="feature-card">
            <div>
                <h4 style="color: {COLORS['dark_blue']}; margin-bottom: 1rem; font-size: 1.3rem;">📅 Full-Day Planner</h4>
                <p style="color: #64748b; margin: 0; line-height: 1.6;">Plan your complete day of meals and activities for optimal health and wellness management.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Create Daily Plan →", key="goto_planner", use_container_width=True):
            st.session_state.current_page = "planner"

# Other Pages (Your existing functionality)
elif st.session_state.current_page == "profile":
    st.markdown('<h1 class="main-header">👤 Profile Management</h1>', unsafe_allow_html=True)
    create_or_edit_profile()

elif st.session_state.current_page == "food_search":
    st.markdown('<h1 class="main-header">🍎 Food Search</h1>', unsafe_allow_html=True)
    search_food_ui()

elif st.session_state.current_page == "food_recommender":
    st.markdown('<h1 class="main-header">💡 Food Recommender</h1>', unsafe_allow_html=True)
    food_recommender_ui(st, foods)

elif st.session_state.current_page == "exercise":
    st.markdown('<h1 class="main-header">🏋️ Exercise Tracking</h1>', unsafe_allow_html=True)
    search_exercise_ui()

elif st.session_state.current_page == "planner":
    st.markdown('<h1 class="main-header">📅 Full-Day Meal Planner</h1>', unsafe_allow_html=True)
    if user['name'] == 'Guest User':
        st.warning("⚠️ Please create or load your profile first to use the meal planner.")
        if st.button("Go to Profile →", use_container_width=True):
            st.session_state.current_page = "profile"
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
        full_day_meal_planner_ui(compatible_user, foods)

# Footer
st.markdown("---")
st.markdown(
    f"<div style='text-align: center; color: {COLORS['medium_blue']}; padding: 3rem; background: {COLORS['light_bg']}; border-radius: 15px; margin-top: 3rem;'>"
    "<p style='margin: 0; font-size: 1rem; font-weight: 600;'>🏥 Health Matrices Pro •  Your Health Journey Starts Here • Transform Your Wellness</p>"
    "</div>",
    unsafe_allow_html=True
)