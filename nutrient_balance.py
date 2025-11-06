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
                suggestion_text = f"⚠️ {nutrient} is HIGH.\n👉 Culprit: **{culprit_food}** in {meal_name}.\n💡 Consider replacing with a lighter option."
            else:
                replacement_df = foods_df[(foods_df["Meal"].str.contains(meal_name, case=False)) &
                                          (foods_df[nutrient] > culprit["Value"]) &
                                          (~foods_df["Food Item"].isin(used_foods))]
                suggestion_text = f"⚠️ {nutrient} is LOW.\n👉 {culprit_food} is not enough.\n💡 Consider replacing with a richer option."

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
# Show balance - SIMPLIFIED VERSION WITHOUT BUTTONS
# ------------------------------
def show_balance_and_actions(totals, ranges, meals, foods_df):
    st.subheader("⚖️ Nutrient Balance Check")
    
    suggestions = suggest_balance(totals, ranges, meals, foods_df)

    has_suggestions = False
    
    for i, sug in enumerate(suggestions):
        st.markdown(sug["text"])
        
        # Show automatic recommendations without buttons
        if sug["replacement"] or sug["culprit"]:
            has_suggestions = True
            if sug["replacement"]:
                st.info(f"💡 **Recommendation:** Try adding **{sug['replacement']['Food Item']}** to balance your {sug['nutrient']} intake.")
        
        # Add some space between suggestions
        st.write("")

    # Show completion message with happy meal message only once at the end
    if has_suggestions:
        st.success("🍽️ Have a happy meal! 😊")
        st.success("✅ Nutrient analysis completed! Enjoy your meal planning! 🎉")
    else:
        st.success("✅ Your meal plan is perfectly balanced! 🍽️ Have a happy meal! 😊")