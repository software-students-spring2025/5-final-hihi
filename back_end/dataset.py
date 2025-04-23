import pandas as pd
import re
import ast


# Load the CSV
df = pd.read_csv('RAW_recipes.csv')

# Columns to check
columns_to_check = ['name', 'minutes', 'tags', 'nutrition', 'steps', 'description', 'ingredients']

# Drop rows with any missing (NaN) or empty string in those columns
filtered_df = df.dropna(subset=columns_to_check)
filtered_df = filtered_df[~(filtered_df[columns_to_check] == '').any(axis=1)]

# Convert to list of dicts
recipes_list = filtered_df[columns_to_check].to_dict(orient='records')

nutrition_fields = [
    "calories",         # in absolute number
    "total_fat",        # % Daily Value (PDV)
    "sugar",            # % Daily Value (PDV)
    "sodium",           # % Daily Value (PDV)
    "protein",          # % Daily Value (PDV)
    "saturated_fat",    # % Daily Value (PDV)
    "carbohydrates"     # % Daily Value (PDV)
]

for recipe in recipes_list:
    nutrition_values = ast.literal_eval(recipe['nutrition'])
    nutrition_dict = dict(zip(nutrition_fields, nutrition_values))
    recipe['nutrition'] = nutrition_dict

    recipe_tags = ast.literal_eval(recipe['tags'])
    recipe['tags'] = recipe_tags

    recipe_step = ast.literal_eval(recipe['steps'])
    recipe['steps'] = recipe_step

    recipe_ingredient = ast.literal_eval(recipe['ingredients'])
    recipe['ingredients'] = recipe_ingredient


print(recipes_list[0])