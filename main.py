from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter, FuzzyCompleter
import pandas as pd

# --- Load datasets ---
foods = pd.read_csv("data/foods.csv")
print("Foods dataset loaded successfully!")

# --- Function to get food info ---
def search_food(food_name):
    """Return exact food info if found."""
    result = foods[foods['Food Item'].str.lower() == food_name.lower()]
    if not result.empty:
        return result.to_dict(orient="records")[0]
    else:
        return None

# --- Autocomplete setup with fuzzy search ---
food_completer = FuzzyCompleter(
    WordCompleter(
        foods['Food Item'].tolist(),
        ignore_case=True,
        match_middle=True
    )
)

# --- Interactive Loop ---
while True:
    user_food = prompt(
        "\nEnter a food name (or 'exit' to quit): ",
        completer=food_completer,
        complete_while_typing=True  # Suggestions appear as you type
    )
    
    if user_food.lower() == "exit":
        print("Goodbye! 👋")
        break

    food_info = search_food(user_food)
    if food_info:
        print(f"\n✅ Found {user_food}:")
        print(f"Calories: {food_info['Calories']} kcal")
        print(f"Protein: {food_info['Protein']} g")
        print(f"Carbs:   {food_info['Carbs']} g")
        print(f"Fats:    {food_info['Fats']} g")
    else:
        print("❌ No exact match found. Make sure to select from the suggestions.")
