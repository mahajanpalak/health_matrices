# user_profile.py
import streamlit as st
import pandas as pd
from database import save_user_profile, load_user_profile

def create_or_edit_profile():
    st.header("👤 Your Profile")

    # Predefined options
    ALLERGY_OPTIONS = ["None", "Gluten", "Dairy", "Nuts", "Soy", "Seafood"]
    INJURY_OPTIONS = ["None", "Core", "Back", "Shoulder", "Arms", "Neck", "Upper Body", "Lower Body", "Full Body"]

    # Load existing profile from database
    profile_data = load_user_profile(st.session_state.user_id)
    
    if profile_data:
        profile = profile_data
        st.success("📋 Editing your existing profile")
    else:
        profile = {}
        st.info("🆕 Create your new profile to get started!")

    # --- Basic info ---
    name = st.text_input("Name", profile.get("Name", ""))
    age = st.number_input("Age", min_value=10, max_value=120, value=int(profile.get("Age", 25)))
    height = st.number_input("Height (cm)", min_value=50, max_value=250, value=int(profile.get("Height", 170)))
    weight = st.number_input("Weight (kg)", min_value=20, max_value=300, value=int(profile.get("Weight", 65)))
    gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(profile.get("Gender", "Male")))
    goal = st.selectbox("Goal", ["Lose", "Maintain", "Gain"], index=["Lose", "Maintain", "Gain"].index(profile.get("Goal", "Maintain")))

    # --- Diet Preference ---
    diet_pref = profile.get("Diet Preference", "Mixed")
    if isinstance(diet_pref, list):
        diet_pref = diet_pref[0] if diet_pref else "Mixed"
    diet_pref = st.selectbox("Diet Preference", ["Veg", "Non-Veg", "Mixed"], index=["Veg", "Non-Veg", "Mixed"].index(diet_pref))

    # --- Multi-select fields ---
    allergies = st.multiselect("Allergies", options=ALLERGY_OPTIONS, default=profile.get("Allergies", ["None"]))
    injuries = st.multiselect("Injuries", options=INJURY_OPTIONS, default=profile.get("Injuries", ["None"]))

    # --- Lifestyle ---
    lifestyle = st.selectbox(
        "Lifestyle",
        ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"],
        index=["Sedentary", "Lightly Active", "Moderately Active", "Very Active"].index(profile.get("Lifestyle", "Moderately Active"))
    )

    # --- Save button ---
# user_profile.py - Update the save button section
# --- Save button ---
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("💾 Save Profile", use_container_width=True):
            if not name:
                st.error("❌ Please enter your name")
            else:
                updated_profile = {
                    "Name": name,
                    "Age": age,
                    "Height": height,
                    "Weight": weight,
                    "Gender": gender,
                    "Goal": goal,
                    "Diet Preference": diet_pref,
                    "Allergies": allergies,
                    "Injuries": injuries,
                    "Lifestyle": lifestyle
                }
                save_user_profile(st.session_state.user_id, updated_profile)
                st.success("✅ Profile saved successfully!")
                st.balloons()
                
                # Clear cache and force refresh
                st.cache_data.clear()
                
                # Add a button to go back to dashboard to see updated data
                if st.button("🏠 Go to Dashboard to See Updates", use_container_width=True):
                    st.session_state.current_page = "dashboard"
                    st.rerun()