# exercise.py
import streamlit as st
import pandas as pd

exercises = pd.read_csv("data/exercises.csv")

def search_exercise_ui():
    st.header("🏋️ Exercise Search")
    search_input = st.text_input("Type an exercise name:")

    if search_input:
        matches = exercises[exercises['Exercise Name'].str.contains(search_input, case=False, na=False)]
        if not matches.empty:
            selected_ex = st.selectbox("Select an exercise:", matches['Exercise Name'].tolist())
            ex_info = exercises[exercises['Exercise Name'] == selected_ex].iloc[0]

            st.markdown(f"**{ex_info['Exercise Name']}**")
            st.markdown(f"Category: {ex_info.get('Category','N/A')}")
            st.markdown(f"Intensity: {ex_info.get('Intensity','N/A')}")
            st.markdown(f"Calories/10min: {ex_info.get('Calories/10min','N/A')} kcal")
            st.markdown(f"Equipment: {ex_info.get('Equipment','N/A')}")
            st.markdown(f"Body Focus: {ex_info.get('Body Focus','N/A')}")
        else:
            st.warning("❌ No matches found.")
