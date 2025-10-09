import streamlit as st
import pandas as pd
import random
from nutrient_balance import show_balance_and_actions


# --- Meal categories (beverage first) ---
MEAL_CATEGORIES = {
    "Breakfast": ["Beverages", "Fruits", "Grains", "Breads", "Dairy & Alternatives"],
    "Lunch": ["Beverages", "Salads", "Cooked Meals", "Pulses", "Roti", "Vegetables", "Meats & Seafood", "Dairy & Alternatives"],
    "Dinner": ["Beverages", "Salads", "Cooked Meals", "Pulses", "Roti", "Vegetables", "Meats & Seafood", "Dairy & Alternatives"],
    "Snack": ["Beverages", "Fruits", "Nuts", "Snacks & Street Foods", "Dairy & Alternatives"]
}

# --- Realistic portion limits ---
REALISTIC_PORTIONS = {
    "Breads": (30, 80),
    "Grains": (50, 150),
    "Fruits": (50, 200),
    "Vegetables": (50, 200),
    "Dairy & Alternatives": (50, 200),
    "Cooked Meals": (100, 250),
    "Pulses": (50, 150),
    "Meats & Seafood": (50, 200),
    "Nuts": (20, 50),
    "Snacks & Street Foods": (30, 100),
    "Beverages": (150, 300),  # in ml
    "Others": (50, 150)
}

# --- Daily requirement calculation ---
def calculate_daily_ranges(user):
    weight, height, age, goal, lifestyle = user['Weight'], user['Height'], user['Age'], user['Goal'], user['Lifestyle']
    bmr = 10*weight + 6.25*height - 5*age + (5 if user['Gender']=="Male" else -161)
    multipliers = {"Sedentary":1.2,"Lightly Active":1.375,"Moderately Active":1.55,"Very Active":1.725}
    tdee = bmr * multipliers.get(lifestyle, 1.55)
    
    if goal=="Lose": tdee_range = (tdee-500, tdee-300)
    elif goal=="Gain": tdee_range = (tdee+300, tdee+500)
    else: tdee_range = (tdee-200, tdee+200)
    
    protein = (0.8*weight, 1.8*weight)
    carbs = (0.4*tdee/4, 0.6*tdee/4)
    fats = (0.2*tdee/9, 0.35*tdee/9)
    water = (weight*0.03, weight*0.04)
    sleep = (7,9)
    
    return {"Calories": tdee_range, "Protein": protein, "Carbs": carbs, "Fats": fats, "Water(L)": water, "Sleep(Hours)": sleep}

# --- Meal calorie distribution ---
def get_meal_calories_distribution(tdee):
    return {
        "Breakfast": tdee*0.25,
        "Lunch": tdee*0.35,
        "Dinner": tdee*0.30,
        "Snack": tdee*0.10
    }

# --- Compute realistic quantity per item ---
def compute_realistic_quantity(item, meal_calories_target):
    cat = item['Category']
    min_q, max_q = REALISTIC_PORTIONS.get(cat, REALISTIC_PORTIONS['Others'])
    cal_per_100 = item['Calories']
    
    if cal_per_100 <= 0:  # for beverages with zero calories
        return min_q
    
    ideal_qty = meal_calories_target / 3 / cal_per_100 * 100
    qty = max(min_q, min(max_q, ideal_qty))
    
    # Beverages are measured in ml
    if cat == "Beverages":
        return round(qty)
    return round(qty)

# --- Filter foods for user ---
def filter_foods(user, foods_df, meal, exclude_items=set()):
    df = foods_df.copy()
    df = df[df['Meal'].str.contains(meal, case=False, na=False)]
    df = df[df['Junk/Healthy']=="Healthy"]
    if user['Diet Preference'] != "Mixed":
        df = df[df['Veg/Non-Veg']==user['Diet Preference']]
    for allergen in user['Allergies']:
        if allergen != "None":
            df = df[~df['Allergens'].str.contains(allergen, case=False, na=False)]
    selected_in_meal = {i['Food Item'] for i in st.session_state['selected_meals'].get(meal, [])}

    # --- exclude items already in current pool ---
    pool_in_meal = {i['Food Item'] for i in st.session_state['meal_pools'].get(meal, [])}

    df = df[~df['Food Item'].isin(exclude_items.union(selected_in_meal).union(pool_in_meal))]
    return df

# --- Generate 3 options per meal ---
def generate_meal_options_improved(user, foods_df, meal):
    used_items = st.session_state['used_items']
    df = filter_foods(user, foods_df, meal, exclude_items=used_items)

    if not df.empty:
        sampled = df.sample(min(3, len(df)))
        return [row for _, row in sampled.iterrows()]
    return []

# --- Select & Skip callbacks ---
def select_item(meal, idx, item, user, tdee, foods_df):
    meal_calories = get_meal_calories_distribution(tdee)[meal]
    qty = compute_realistic_quantity(item, meal_calories)
    item_copy = item.copy()
    item_copy['Quantity'] = qty

    # add to selected meals
    st.session_state['selected_meals'][meal].append(item_copy)

    # mark it as used
    st.session_state['used_items'].add(item['Food Item'])
    st.session_state['highlighted_buttons'].add(f"{meal}_{item['Food Item']}")

    # --- replace slot with new item ---
    new_item = filter_foods(user, foods_df, meal, exclude_items=st.session_state['used_items'])
    if not new_item.empty:
        st.session_state['meal_pools'][meal][idx] = new_item.sample(1).iloc[0]

def skip_item(meal, idx, user, foods_df):
    st.session_state['used_items'].add(st.session_state['meal_pools'][meal][idx]['Food Item'])

    # replace slot with new item
    new_item = filter_foods(user, foods_df, meal, exclude_items=st.session_state['used_items'])
    if not new_item.empty:
        st.session_state['meal_pools'][meal][idx] = new_item.sample(1).iloc[0]

# --- Full-day meal planner UI ---
def full_day_meal_planner_ui(user, foods_df):
    st.header("🍴 Full-Day Personalized Meal Planner")
    
    tdee = sum(calculate_daily_ranges(user)['Calories'])/2
    ranges = calculate_daily_ranges(user)
    
    st.subheader("Daily Requirement Ranges")
    for key, val in ranges.items():
        st.write(f"{key}: {round(val[0],1)} - {round(val[1],1)}")
    
    # --- Initialize session state in correct order ---
    if 'selected_meals' not in st.session_state:
        st.session_state['selected_meals'] = {meal: [] for meal in MEAL_CATEGORIES.keys()}
    if 'used_items' not in st.session_state:
        st.session_state['used_items'] = set()
    if 'highlighted_buttons' not in st.session_state:
        st.session_state['highlighted_buttons'] = set()
    if 'meal_pools' not in st.session_state:
        st.session_state['meal_pools'] = {}

    # --- Only now generate the meal pools ---
    if not st.session_state['meal_pools']:
        st.session_state['meal_pools'] = {
            meal: generate_meal_options_improved(user, foods_df, meal)
            for meal in MEAL_CATEGORIES.keys()
        }
    
    # --- Show meal options ---
    for meal in MEAL_CATEGORIES.keys():
        st.subheader(meal)

        # --- Show selected items clearly ---
        if st.session_state['selected_meals'][meal]:
            st.markdown("**✅ Selected items:**")
            for sel in st.session_state['selected_meals'][meal]:
                qty_unit = "ml" if "Beverages" in sel['Category'] else "g"
                st.write(
                    f"- {sel['Food Item']} ({sel['Quantity']} {qty_unit}) "
                    f"Calories: {sel['Calories']*sel['Quantity']/100:.1f}, "
                    f"Protein: {sel['Protein']*sel['Quantity']/100:.1f}g, "
                    f"Carbs: {sel['Carbs']*sel['Quantity']/100:.1f}g, "
                    f"Fats: {sel['Fats']*sel['Quantity']/100:.1f}g"
                )

        # --- Show available options ---
        pool = st.session_state['meal_pools'][meal]
        for idx, item in enumerate(pool):
            key = f"{meal}_{item['Food Item']}_{idx}"
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(
                    f"**{item['Food Item']}** ({item['Category']}) - "
                    f"Calories: {item['Calories']}, Protein: {item['Protein']}g, "
                    f"Carbs: {item['Carbs']}g, Fats: {item['Fats']}g"
                )
            with col2:
                if key in st.session_state['highlighted_buttons']:
                    st.button("Selected ✅", key=f"selected_{key}", disabled=True)
                else:
                    st.button("Select", key=f"select_{key}",
                            on_click=select_item, args=(meal, idx, item, user, tdee, foods_df))
                    st.button("Skip", key=f"skip_{key}",
                            on_click=skip_item, args=(meal, idx, user, foods_df))
    
    # --- Final plan summary ---
    if st.button("Take up the plan"):
        st.subheader("✅ Your Final Plan")

        # Initialize totals
        total_cal, total_protein, total_carbs, total_fats = 0, 0, 0, 0

        for meal, items in st.session_state['selected_meals'].items():
            if items:
                st.write(f"**{meal}:**")
                for item in items:
                    cal = item['Calories'] * item['Quantity'] / 100
                    prot = item['Protein'] * item['Quantity'] / 100
                    carb = item['Carbs'] * item['Quantity'] / 100
                    fat = item['Fats'] * item['Quantity'] / 100

                    total_cal += cal
                    total_protein += prot
                    total_carbs += carb
                    total_fats += fat

                    st.write(
                        f"- {item['Food Item']} ({item['Quantity']} g/ml) → "
                        f"Calories: {cal:.1f}, Protein: {prot:.1f}g, "
                        f"Carbs: {carb:.1f}g, Fats: {fat:.1f}g"
                    )

        # Show totals
        st.write(f"**Total Calories:** {total_cal:.1f} kcal")
        st.write(f"**Total Protein:** {total_protein:.1f} g")
        st.write(f"**Total Carbs:** {total_carbs:.1f} g")
        st.write(f"**Total Fats:** {total_fats:.1f} g")
        st.write(f"**Recommended Water Intake:** {round(user['Weight']*0.03,2)} L")

        # Prepare totals dictionary
        totals = {
            "Calories": total_cal,
            "Protein": total_protein,
            "Carbs": total_carbs,
            "Fats": total_fats,
        }
        ranges = calculate_daily_ranges(user)

        show_balance_and_actions(totals, ranges, st.session_state['selected_meals'], foods_df)

        # Recalculate totals if suggestions applied
        if "suggestion_actions" in st.session_state and st.session_state["suggestion_actions"]:
            total_cal, total_protein, total_carbs, total_fats = 0, 0, 0, 0
            for meal, items in st.session_state['selected_meals'].items():
                for item in items:
                    qty = item['Quantity']
                    total_cal += item['Calories']*qty/100
                    total_protein += item['Protein']*qty/100
                    total_carbs += item['Carbs']*qty/100
                    total_fats += item['Fats']*qty/100

            st.write("### 🔄 Updated Totals After Accepted Suggestions")
            st.write(f"**Total Calories:** {total_cal:.1f} kcal")
            st.write(f"**Total Protein:** {total_protein:.1f} g")
            st.write(f"**Total Carbs:** {total_carbs:.1f} g")
            st.write(f"**Total Fats:** {total_fats:.1f} g")
            st.write(f"**Recommended Water Intake:** {round(user['Weight']*0.03,2)} L")

