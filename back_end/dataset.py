import pandas as pd
import re

# Load the CSV
df = pd.read_csv('recipes.csv')

# Columns to check
columns_to_check = ['recipe_name', 'cuisine_path', 'total_time', 'ingredients', 'directions', 'nutrition', 'img_src']

# Drop rows with any missing (NaN) or empty string in those columns
filtered_df = df.dropna(subset=columns_to_check)
filtered_df = filtered_df[~(filtered_df[columns_to_check] == '').any(axis=1)]

# Convert to list of dicts
recipes_list = filtered_df[columns_to_check].to_dict(orient='records')

# Example
print(recipes_list[0]["total_time"])


def convert_time_to_minutes(time_str):
    if not time_str or not isinstance(time_str, str):
        return None
    time_str = time_str.lower()
    hours = re.search(r'(\d+)\s*hr', time_str)
    minutes = re.search(r'(\d+)\s*min', time_str)

    total = 0
    if hours:
        total += int(hours.group(1)) * 60
    if minutes:
        total += int(minutes.group(1))
    return total if total > 0 else None

def parse_nutrition(nutrition_str):
    if not nutrition_str or not isinstance(nutrition_str, str):
        return {
            'Fat': None,
            'Cholesterol': None,
            'Sodium': None,
            'Carbohydrate': None,
            'Dietary Fiber': None,
            'Protein': None,
            'Vitamin C': None,
            'Calcium': None,
            'Iron': None,
            'Potassium': None
        }

    nutrients = {
        'Fat': r'Total Fat (\d+\.?\d*\s*g)',
        'Cholesterol': r'Cholesterol (\d+\.?\d*\s*mg)',
        'Sodium': r'Sodium (\d+\.?\d*\s*mg)',
        'Carbohydrate': r'Total Carbohydrate (\d+\.?\d*\s*g)',
        'Dietary Fiber': r'Dietary Fiber (\d+\.?\d*\s*g)',
        'Protein': r'Protein (\d+\.?\d*\s*g)',
        'Vitamin C': r'Vitamin C (\d+\.?\d*\s*mg)',
        'Calcium': r'Calcium (\d+\.?\d*\s*mg)',
        'Iron': r'Iron (\d+\.?\d*\s*mg)',
        'Potassium': r'Potassium (\d+\.?\d*\s*mg)'
    }

    result = {}
    for key, pattern in nutrients.items():
        match = re.search(pattern, nutrition_str)
        result[key] = match.group(1).strip() if match else None

    return result


def extract_cuisine_type(cuisine_path):
    if not cuisine_path or not isinstance(cuisine_path, str):
        return None
    parts = cuisine_path.strip('/').split('/')
    return parts[0] if parts else None


# Apply to your recipe dictionary list
for recipe in recipes_list:
    time_str = recipe.get('total_time', '')
    recipe['total_time'] = convert_time_to_minutes(time_str)

    nutrition_str = recipe.get('nutrition', '')
    nutrition_data = parse_nutrition(nutrition_str)
    recipe["nutrition"]= nutrition_data

    cuisine_path = recipe.get('cuisine_path', '')
    recipe['cuisine_type'] = extract_cuisine_type(cuisine_path)
    recipe.pop('cuisine_path', None)

# Example check
# print(recipes_list[0])
unique_cuisine_types = set()

for recipe in recipes_list:
    cuisine = recipe.get('cuisine_type')
    if cuisine:
        unique_cuisine_types.add(cuisine)

# print(sorted(unique_cuisine_types))

