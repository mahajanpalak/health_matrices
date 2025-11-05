import streamlit as st
import pandas as pd
import os

# Load foods dataset from data/ folder
foods = pd.read_csv(os.path.join("data", "foods.csv"))

def get_food_suggestions(goal, meal, foods, n=3, exclude=[]):
    df = foods.copy()

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

    goal = st.selectbox("Select your Goal", [
        "Lose", "Maintain", "Gain", "High Protein", "Low Carb", "Pre-Workout", "Post-Workout", "Pre-Bed"
    ])

    meal = st.selectbox("Select Meal Time", ["Breakfast", "Snack", "Lunch", "Dinner", "Pre-Workout", "Post-Workout", "Pre-Bed"])

    if st.button("Get Suggestions"):
        st.session_state['shown_foods'] = []
        st.session_state['goal'] = goal
        st.session_state['meal'] = meal
        st.session_state['current_options'] = get_food_suggestions(goal, meal, foods, 3)

    if 'current_options' in st.session_state:
        options = st.session_state['current_options']
        if not options.empty:
            st.subheader("Suggested Options")

            for _, row in options.iterrows():
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.write(f"**{row['Food Item']}**")
                    st.write(f"Calories: {row['Calories']} | Protein: {row['Protein']}g | Carbs: {row['Carbs']}g | Fats: {row['Fats']}g")
                with col2:
                    if st.button(f"Select {row['Food Item']}"):
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
                    exclude=st.session_state['shown_foods']
                )
        else:
            st.warning("⚠️ No foods found for this goal and meal. Try a different combination.")
