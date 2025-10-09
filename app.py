# app.py
import streamlit as st
import pandas as pd

# --- Load dataset ---
foods = pd.read_csv("data/foods.csv")
exercises = pd.read_csv("data/exercises.csv")


st.title("🍎 Health Matrices Food Search")
# --- Tabs for Food & Exercise ---
tab1, tab2 = st.tabs(["Food Search 🍎", "Exercise Search 🏋️"])

# --- FOOD SEARCH TAB ---
with tab1:
    search_input = st.text_input("Type a food name:", key="food")
    
    if search_input:
        matches = foods[foods['Food Item'].str.contains(search_input, case=False, na=False)]
        if not matches.empty:
            selected_food = st.selectbox("Select a food from suggestions:", matches['Food Item'].tolist(), key="food_select")
            food_info = foods[foods['Food Item'] == selected_food].iloc[0]
            st.markdown(f"**{food_info['Food Item']}**")
            st.markdown(f"Calories: {food_info['Calories']} kcal | Protein: {food_info['Protein']} g | Carbs: {food_info['Carbs']} g | Fats: {food_info['Fats']} | Veg/Non-Veg: {food_info['Veg/Non-Veg']} g")
        else:
            st.warning("❌ No matches found. Try a different food name.")



# --- EXERCISE SEARCH TAB ---
with tab2:
    search_input_ex = st.text_input("Type an exercise name:", key="exercise")
    
    if search_input_ex:
        # Filter exercises with partial match (case-insensitive)
        matches_ex = exercises[exercises['Exercise Name'].str.contains(search_input_ex, case=False, na=False)]
        
        if not matches_ex.empty:
            # Autocomplete-like selection
            selected_exercise = st.selectbox(
                "Select an exercise from suggestions:", 
                matches_ex['Exercise Name'].tolist(), 
                key="exercise_select"
            )
            
            # Show only required columns
            exercise_info = exercises[exercises['Exercise Name'] == selected_exercise].iloc[0]
            st.markdown(f"**{exercise_info['Exercise Name']}**")
            st.markdown(f"Category: {exercise_info.get('Category', 'N/A')}")
            st.markdown(f"Intensity: {exercise_info.get('Intensity', 'N/A')}")
            st.markdown(f"Calories/10min: {exercise_info.get('Calories/10min', 'N/A')} kcal")
            st.markdown(f"Equipment: {exercise_info.get('Equipment', 'N/A')}")
            st.markdown(f"Body Focus: {exercise_info.get('Body Focus', 'N/A')}")
        else:
            st.warning("❌ No matches found. Try a different exercise name.")
