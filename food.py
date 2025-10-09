# food.py
import streamlit as st
import pandas as pd

foods = pd.read_csv("data/foods.csv")

def search_food_ui():
    st.header("🍎 Food Search")
    search_input = st.text_input("Type a food name:")

    if search_input:
        matches = foods[foods['Food Item'].str.contains(search_input, case=False, na=False)]
        if not matches.empty:
            selected_food = st.selectbox("Select a food from suggestions:", matches['Food Item'].tolist())
            food_info = foods[foods['Food Item'] == selected_food].iloc[0]

            st.markdown(f"**{food_info['Food Item']}**")
            st.markdown(f"Calories: {food_info['Calories']} kcal | Protein: {food_info['Protein']} g | Carbs: {food_info['Carbs']} g | Fats: {food_info['Fats']} g")
        else:
            st.warning("❌ No matches found.")
