import streamlit as st
import pandas as pd

# ------------------------------
# Check nutrient balance
# ------------------------------
def check_nutrient_balance(totals, ranges, tolerance=0.15):
    status = {}
    for nutrient in ["Calories", "Protein", "Carbs", "Fats"]:
        target_low, target_high = ranges[nutrient]
        avg_target = (target_low + target_high) / 2
        low_bound = avg_target * (1 - tolerance)
        high_bound = avg_target * (1 + tolerance)
        if totals[nutrient] < low_bound:
            status[nutrient] = "Low"
        elif totals[nutrient] > high_bound:
            status[nutrient] = "High"
        else:
            status[nutrient] = "OK"
    return status

# ------------------------------
# Suggest replacements or additions
# ------------------------------
def suggest_balance(totals, ranges, meals, foods_df, tolerance=0.15):
    statuses = check_nutrient_balance(totals, ranges, tolerance)
    suggestions = []

    used_foods = {item["Food Item"] for meal_items in meals.values() for item in meal_items}

    for nutrient, state in statuses.items():
        if state == "OK":
            continue

        # Compute contribution of each food
        contribs = []
        for meal, items in meals.items():
            for item in items:
                qty = item["Quantity"]
                factor = qty / 100.0
                contrib_val = item[nutrient] * factor
                contribs.append((meal, item["Food Item"], contrib_val))

        df_contrib = pd.DataFrame(contribs, columns=["Meal", "Food", "Value"])
        if not df_contrib.empty:
            df_contrib["Share"] = df_contrib["Value"] / df_contrib["Value"].sum()
        else:
            df_contrib["Share"] = []

        # Find culprit if any (>40% share)
        culprit_row = df_contrib[df_contrib["Share"] > 0.4].sort_values("Share", ascending=False)
        if not culprit_row.empty:
            culprit = culprit_row.iloc[0]
            meal_name = culprit["Meal"]
            culprit_food = culprit["Food"]

            if state == "High":
                replacement_df = foods_df[(foods_df["Meal"].str.contains(meal_name, case=False)) &
                                          (foods_df[nutrient] < culprit["Value"]) &
                                          (~foods_df["Food Item"].isin(used_foods))]
                suggestion_text = f"⚠️ {nutrient} is HIGH.\n👉 Culprit: **{culprit_food}** in {meal_name}.\n💡 Suggest replacing with a lighter option."
            else:
                replacement_df = foods_df[(foods_df["Meal"].str.contains(meal_name, case=False)) &
                                          (foods_df[nutrient] > culprit["Value"]) &
                                          (~foods_df["Food Item"].isin(used_foods))]
                suggestion_text = f"⚠️ {nutrient} is LOW.\n👉 {culprit_food} is not enough.\n💡 Suggest replacing with a richer option."

            replacement = replacement_df.sample(1).iloc[0].to_dict() if not replacement_df.empty else None

            suggestions.append({
                "text": suggestion_text,
                "nutrient": nutrient,
                "meal": meal_name,
                "culprit": culprit_food,
                "replacement": replacement
            })
        else:
            # No single culprit → suggest a specific food for this nutrient
            candidate_df = foods_df[(foods_df[nutrient].notnull()) & (foods_df[nutrient] > 0) &
                                    (~foods_df["Food Item"].isin(used_foods))]
            replacement = candidate_df.sample(1).iloc[0].to_dict() if not candidate_df.empty else None
            if state == "Low":
                suggestion_text = f"⚠️ {nutrient} is LOW.\n💡 Suggested food: **{replacement['Food Item']}**" if replacement else f"⚠️ {nutrient} is LOW. No suitable food found."
            else:
                suggestion_text = f"⚠️ {nutrient} is HIGH.\n💡 Consider reducing portion or replacing with lower {nutrient} food: **{replacement['Food Item']}**" if replacement else f"⚠️ {nutrient} is HIGH. No suitable food found."

            suggestions.append({
                "text": suggestion_text,
                "nutrient": nutrient,
                "meal": None,
                "culprit": None,
                "replacement": replacement
            })

    if not suggestions:
        suggestions.append({
            "text": "✅ Balanced! Nice plan 🎉",
            "nutrient": None,
            "meal": None,
            "culprit": None,
            "replacement": None
        })

    return suggestions

# ------------------------------
# Show balance and handle user actions
# ------------------------------
def show_balance_and_actions(totals, ranges, meals, foods_df):
    if "suggestion_actions" not in st.session_state:
        st.session_state["suggestion_actions"] = {}

    suggestions = suggest_balance(totals, ranges, meals, foods_df)
    all_handled = True

    st.subheader("⚖️ Nutrient Balance Check")

    for i, sug in enumerate(suggestions):
        st.markdown(sug["text"])
        if sug["replacement"] or sug["culprit"]:
            all_handled = all_handled and (i in st.session_state["suggestion_actions"])
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button(f"Accept", key=f"accept_{i}"):
                    st.session_state["suggestion_actions"][i] = ("accept", sug["replacement"])

            with col2:
                if st.button(f"No, I'm good", key=f"reject_{i}"):
                    st.session_state["suggestion_actions"][i] = ("reject", None)

            with col3:
                if st.button(f"New alternative", key=f"alt_{i}"):
                    # Suggest a new food alternative safely
                    nutrient = sug["nutrient"]
                    if nutrient and nutrient in foods_df.columns:
                        alt_df = foods_df[(foods_df[nutrient].notnull()) & (foods_df[nutrient] > 0) &
                                          (~foods_df["Food Item"].isin(
                                              [item["Food Item"] for meal_items in meals.values() for item in meal_items]
                                          ))]
                        if not alt_df.empty:
                            new_food = alt_df.sample(1).iloc[0].to_dict()
                            st.session_state["suggestion_actions"][i] = ("alternative", new_food)

    # Apply accepted/alternative suggestions after all handled
    if all_handled and suggestions:
        applied = False
        for i, (action, food) in st.session_state["suggestion_actions"].items():
            sug = suggestions[i]
            if action in ["accept", "alternative"] and food and sug["culprit"]:
                # Replace culprit food in the meal plan
                meal_name = sug["meal"]
                if meal_name in meals:
                    for idx, item in enumerate(meals[meal_name]):
                        if item["Food Item"] == sug["culprit"]:
                            meals[meal_name][idx].update(food)
                            applied = True
            elif action in ["accept", "alternative"] and food and not sug["culprit"]:
                # If no culprit, append the suggested food to first meal
                first_meal = list(meals.keys())[0]
                meals[first_meal].append(food)
                applied = True

        if applied:
            st.success("✅ All accepted/alternative suggestions applied. Totals updated.")
