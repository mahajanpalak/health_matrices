import streamlit as st
import pandas as pd
import os
from database import load_user_profile

# Load foods dataset from data/ folder
foods = pd.read_csv(os.path.join("data", "foods.csv"))

def get_food_suggestions(goal, meal, foods, n=3, exclude=[], user_id=None):
    df = foods.copy()
    
    # --- Get user diet preference from profile ---
    diet_preference = "Mixed"  # default
    if user_id:
        profile = load_user_profile(user_id)
        if profile and "Diet Preference" in profile:
            diet_preference = profile["Diet Preference"]
    
    # --- Filter by diet preference ---
    if diet_preference == "Veg":
        df = df[df['Veg/Non-Veg'] == 'Veg']
    elif diet_preference == "Non-Veg":
        df = df[df['Veg/Non-Veg'] == 'Non-Veg']
    # If "Mixed", no filtering needed
    
    # --- Filter by meal (supports multiple comma-separated values) ---
    df = df[df['Meal'].str.contains(meal, case=False, na=False)]
    
    # --- Goal-specific filters ---
    if goal == "Lose":
        df = df[(df['Calories'] <= 250) & (df['Protein'] >= 8) & (df['Fats'] <= 10)]
    elif goal == "Gain":
        df = df[(df['Calories'] >= 350) & (df['Protein'] >= 10)]
    elif goal == "Maintain":
        df = df[(df['Calories'].between(200, 450)) & (df['Protein'] >= 5)]
    elif goal == "High Protein":
        df = df[(df['Protein'] >= 20)]
    elif goal == "Low Carb":
        df = df[(df['Carbs'] <= 20) & (df['Protein'] >= 10)]
    elif goal == "Pre-Workout":
        df = df[(df['Carbs'].between(25, 50)) & (df['Protein'].between(8, 20)) & (df['Fats'] <= 8)]
    elif goal == "Post-Workout":
        df = df[(df['Protein'] >= 20) & (df['Carbs'].between(20, 50)) & (df['Fats'] <= 10)]
    elif goal == "Pre-Bed":
        df = df[(df['Protein'].between(10, 25)) & (df['Carbs'] <= 15) & (df['Fats'] <= 12)]
    
    # --- Remove already shown options ---
    if exclude:
        df = df[~df['Food Item'].isin(exclude)]
    
    # --- Pick N random items (avoid empty crash) ---
    if df.empty:
        return pd.DataFrame()
    return df.sample(min(n, len(df)))


def food_recommender_ui(st, foods):
    st.header("🍽 Food Recommendation")
    
    # Get user_id from session state
    user_id = st.session_state.get('user_id', None)
    
    goal = st.selectbox("Select your Goal", [
        "Lose", "Maintain", "Gain", "High Protein", "Low Carb", "Pre-Workout", "Post-Workout", "Pre-Bed"
    ])
    
    meal = st.selectbox("Select Meal Time", ["Breakfast", "Snack", "Lunch", "Dinner", "Pre-Workout", "Post-Workout", "Pre-Bed"])
    
    # Show user's diet preference if available
    if user_id:
        profile = load_user_profile(user_id)
        if profile and "Diet Preference" in profile:
            diet_pref = profile["Diet Preference"]
            st.info(f"🍽 Your diet preference: **{diet_pref}** (Non-veg items will be filtered out if set to Veg)")
    
    if st.button("Get Suggestions"):
        st.session_state['shown_foods'] = []
        st.session_state['goal'] = goal
        st.session_state['meal'] = meal
        st.session_state['current_options'] = get_food_suggestions(
            goal, meal, foods, 3, 
            user_id=user_id
        )
    
    if 'current_options' in st.session_state:
        options = st.session_state['current_options']
        if not options.empty:
            st.subheader("Suggested Options")
            
            for _, row in options.iterrows():
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.write(f"**{row['Food Item']}**")
                    st.write(f"Calories: {row['Calories']} | Protein: {row['Protein']}g | Carbs: {row['Carbs']}g | Fats: {row['Fats']}g")
                    st.write(f"Type: {row['Veg/Non-Veg']} | Category: {row['Category']}")
                with col2:
                    if st.button(f"Select {row['Food Item']}", key=row['Food Item']):
                        st.success(f"You selected {row['Food Item']}")
                        # TODO: log selection into user profile
                st.divider()
            
            if st.button("Show me different options"):
                st.session_state['shown_foods'].extend(options['Food Item'].tolist())
                st.session_state['current_options'] = get_food_suggestions(
                    st.session_state['goal'],
                    st.session_state['meal'],
                    foods,
                    3,
                    exclude=st.session_state['shown_foods'],
                    user_id=user_id
                )
        else:
            st.warning("⚠️ No foods found for this goal and meal. Try a different combination.")
