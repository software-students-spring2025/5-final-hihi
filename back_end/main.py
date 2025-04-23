from dataset import recipes_list
import re
import random
import itertools

allergy = "egg"
cook_time = 120 
calories_requirement = 600
types = ['Appetizers and Snacks', 'Breakfast and Brunch', 'Drinks Recipes', 'Main Dishes']

def extract_number_and_unit(value):
    if not value:
        return 0.0
    match = re.search(r'(\d+\.?\d*)\s*(mg|g)?', value.lower())
    if not match:
        return 0.0
    num = float(match.group(1))
    unit = match.group(2)
    if unit == 'mg':
        return num / 1000  # convert to grams
    return num  # already in grams

def estimate_calories(nutrition_dict):
    fat_g = extract_number_and_unit(nutrition_dict.get('Fat'))
    carb_g = extract_number_and_unit(nutrition_dict.get('Carbohydrate'))
    fiber_g = extract_number_and_unit(nutrition_dict.get('Dietary Fiber'))
    protein_g = extract_number_and_unit(nutrition_dict.get('Protein'))

    # Estimate digestible carbs
    digestible_carb_g = max(carb_g - fiber_g, 0)

    calories = (
        fat_g * 9 +
        digestible_carb_g * 4 +
        fiber_g * 2 +
        protein_g * 4
    )

    return round(calories)

for recipe in recipes_list:
    nutrition = {key: recipe['nutrition'].get(key) for key in [
        'Fat', 'Carbohydrate', 'Dietary Fiber', 'Protein'
    ]}
    recipe['calories'] = estimate_calories(nutrition)


def is_allergy_safe(ingredients, allergy_word):
    return allergy_word.lower() not in ingredients.lower()

# Step 1: Filter valid recipes per type
valid_by_type = {}
for t in types:
    filtered = [
        r for r in recipes_list
        if r.get('cuisine_type') == t
        and is_allergy_safe(r.get('ingredients', ''), allergy)
        and isinstance(r.get('total_time'), (int, float))
        and r['total_time'] <= cook_time
        and isinstance(r.get('calories'), (int, float))
    ]
    random.shuffle(filtered)  # Add randomization here
    valid_by_type[t] = filtered

# Step 2: Generate all combinations (random order)
type_recipe_lists = [valid_by_type[t] for t in types]

if all(type_recipe_lists):
    all_combinations = list(itertools.product(*type_recipe_lists))
    random.shuffle(all_combinations)  # Shuffle combinations to randomize selection

    for combo in all_combinations:
        total_calories = sum(r['calories'] for r in combo)
        if total_calories <= calories_requirement:
            selected_recipes = list(combo)
            break
    else:
        selected_recipes = []  # No valid combo found
else:
    selected_recipes = []

# Step 3: Output result
if selected_recipes:
    print(f"Randomized selection (Total calories: {sum(r['calories'] for r in selected_recipes)}):\n")
    for r in selected_recipes:
        print(f"- {r['recipe_name']} ({r['cuisine_type']}): {r['calories']} cal, {r['total_time']} mins")
else:
    print("No valid combination found under calorie limit.")