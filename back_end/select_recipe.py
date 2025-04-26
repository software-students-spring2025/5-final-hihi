def recommend_recipes(user_preferences):
    """
    Algorithm to recommend recipes based on user preferences.
    
    Parameters:
    - user_preferences: Dictionary containing user survey responses
    
    Returns:
    - List of recommended recipes for each selected meal
    """
    # 1. Extract preferences from survey responses
    diet_allergies = extract_diet_allergies(user_preferences.get('question1', []))
    calorie_intake = extract_calorie_intake(user_preferences.get('question2', 7))  # Default: No specific
    prep_time = extract_prep_time(user_preferences.get('question3', 6))  # Default: No specific
    cuisines = extract_cuisines(user_preferences.get('question4', [15]))  # Default: No specific
    cooking_experience = extract_cooking_experience(user_preferences.get('question5', 1))  # Default: Beginner
    meal_types = extract_meal_types(user_preferences.get('question6', []))
    dish_types = extract_dish_types(user_preferences.get('question7', []))
    
    # 2. Create base query for recipe filtering
    base_query = {}
    
    # 3. Apply strict dietary restrictions and allergies (highest priority)
    if diet_allergies:
        base_query.update(build_dietary_query(diet_allergies))
    
    # 4. Add cuisine preferences if specified
    if cuisines != [15]:  # If not "No specific requirement"
        base_query.update(build_cuisine_query(cuisines))
    
    # 5. Calculate per-meal calorie distribution if specified
    meal_calorie_ranges = calculate_meal_calories(calorie_intake, meal_types)
    
    # 6. Initialize results dictionary
    recommendations = {meal: [] for meal in meal_types}
    
    # 7. Generate recommendations for each selected meal
    for meal in meal_types:
        meal_query = base_query.copy()
        meal_query['type'] = meal.lower()
        
        # Add meal-specific constraints
        if prep_time != 6:  # If time constraint specified
            meal_query['time'] = {'$lte': convert_time_preference_to_minutes(prep_time)}
        
        if meal_calorie_ranges[meal]:  # If calorie constraint specified
            meal_query.update(build_calorie_query(meal_calorie_ranges[meal]))
        
        # For lunch and dinner, handle different dish types
        if meal.lower() in ['lunch', 'dinner']:
            for dish_type in dish_types:
                dish_query = meal_query.copy()
                dish_query['tags'] = {'$in': [convert_dish_type_to_tag(dish_type)]}
                
                # Find recipes matching criteria
                matching_recipes = find_recipes(dish_query, limit=2)  # Get 2 recipes per dish type
                recommendations[meal].extend(matching_recipes)
        else:
            # For breakfast and brunch, just get recipes of that type
            matching_recipes = find_recipes(meal_query, limit=5)  # Get 5 recipes for breakfast/brunch
            recommendations[meal].extend(matching_recipes)
    
    # 8. Apply randomness to ensure variety
    for meal in recommendations:
        shuffle(recommendations[meal])
        
    # 9. Check if calorie constraints are met for the whole day
    if calorie_intake != 7:  # If specific calorie intake was requested
        adjust_for_calorie_target(recommendations, calorie_intake)
    
    return recommendations

def extract_diet_allergies(selections):
    """Convert diet/allergy survey selections to query constraints"""
    diet_constraints = {}
    
    # Map selections to database fields
    diet_mapping = {
        1: {'vegetarian': True},
        2: {'vegan': True},
        3: {'dietary': True},
        4: {'gluten_free': True},
        5: {'kosher': True},
        6: {'lactose': True},
        7: {'eggs_dairy': False},  # Allergy
        8: {'seafood': False},     # Allergy
        9: {'nuts': False}         # Allergy
    }
    
    for selection in selections:
        if selection == 10:  # No specific requirement
            return {}
        diet_constraints.update(diet_mapping.get(selection, {}))
    
    return diet_constraints

def extract_calorie_intake(selection):
    """Convert calorie intake selection to calorie range"""
    calorie_mapping = {
        1: (1200, 1400),
        2: (1400, 1600),
        3: (1600, 1800),
        4: (1800, 2200),
        5: (2200, 2500),
        6: (2500, 3000),
        7: None  # No specific requirement
    }
    return calorie_mapping.get(selection, None)

def calculate_meal_calories(calorie_range, meal_types):
    """Distribute calorie intake across selected meals"""
    if not calorie_range:
        return {meal: None for meal in meal_types}
    
    # Default distribution percentages
    distribution = {
        'Breakfast': 0.25,
        'Brunch': 0.35,
        'Lunch': 0.30,
        'Dinner': 0.45
    }
    
    # Adjust distribution based on selected meals
    total_percentage = sum(distribution[meal] for meal in meal_types)
    adjusted_distribution = {meal: distribution[meal] / total_percentage for meal in meal_types}
    
    # Calculate calorie ranges for each meal
    min_cal, max_cal = calorie_range
    meal_calories = {}
    
    for meal in meal_types:
        meal_min = int(min_cal * adjusted_distribution[meal])
        meal_max = int(max_cal * adjusted_distribution[meal])
        meal_calories[meal] = (meal_min, meal_max)
    
    return meal_calories

def find_recipes(query, limit=5):
    """Query database for recipes matching criteria"""
    # This is a placeholder for the actual database query
    # In a real implementation, this would use mongoengine's find method
    return Recipe.objects(__raw__=query).limit(limit)

def convert_dish_type_to_tag(dish_type):
    """Convert dish type selection to recipe tag"""
    mapping = {
        1: "main dish",
        2: "side dish",
        3: "dessert",
        4: "appetizer",
        5: "soup",
        6: "beverage"
    }
    return mapping.get(dish_type, "main dish")

def convert_time_preference_to_minutes(time_selection):
    """Convert time preference to maximum minutes"""
    time_mapping = {
        1: 30,    # Less than 30 minutes
        2: 60,    # 30 minutes to 1 hour
        3: 90,    # 1 hour to 1.5 hours
        4: 120,   # 1.5 hours to 2 hours
        5: 9999,  # More than 2 hours
        6: None   # No specific requirement
    }
    return time_mapping.get(time_selection, None)

def build_dietary_query(diet_allergies):
    """Build MongoDB query for dietary restrictions"""
    query = {}
    
    # Handle vegetarian/vegan requirements
    if diet_allergies.get('vegetarian'):
        query['tags'] = {'$in': ['vegetarian']}
    if diet_allergies.get('vegan'):
        query['tags'] = {'$in': ['vegan']}
    
    # Handle allergies (ingredients to exclude)
    exclude_ingredients = []
    if diet_allergies.get('eggs_dairy') is False:
        exclude_ingredients.extend(['egg', 'milk', 'cheese', 'cream', 'butter', 'yogurt'])
    if diet_allergies.get('seafood') is False:
        exclude_ingredients.extend(['fish', 'shrimp', 'lobster', 'crab', 'clam', 'mussel', 'oyster'])
    if diet_allergies.get('nuts') is False:
        exclude_ingredients.extend(['peanut', 'almond', 'walnut', 'cashew', 'pecan', 'hazelnut', 'pistachio'])
    
    if exclude_ingredients:
        # Create regex pattern to match any of the excluded ingredients
        pattern = '|'.join(exclude_ingredients)
        query['ingredients'] = {'$not': {'$regex': pattern, '$options': 'i'}}
    
    # Add other dietary restrictions
    if diet_allergies.get('gluten_free'):
        query['tags'] = {'$in': ['gluten-free']}
    if diet_allergies.get('kosher'):
        query['tags'] = {'$in': ['kosher']}
    if diet_allergies.get('lactose'):
        query['tags'] = {'$in': ['lactose-free']}
    
    return query

def build_cuisine_query(cuisine_selections):
    """Build MongoDB query for cuisine preferences"""
    cuisine_mapping = {
        1: "north american",
        2: "european",
        3: "asian",
        4: "italian",
        5: "mexican",
        6: "canadian",
        7: "australian",
        8: "midwestern",
        9: "african",
        10: "indian",
        11: "greek",
        12: "french",
        13: "middle eastern",
        14: "chinese"
    }
    
    cuisine_tags = [cuisine_mapping.get(selection) for selection in cuisine_selections if selection != 15]
    if not cuisine_tags:
        return {}
    
    return {'tags': {'$in': cuisine_tags}}

def build_calorie_query(calorie_range):
    """Build query for calorie constraints"""
    min_cal, max_cal = calorie_range
    
    # Assumes nutrition info is stored in a format like "calories: 350"
    return {
        'nutrition': {
            '$regex': f'calories: ({min_cal}|[{min_cal}-{max_cal}])',
            '$options': 'i'
        }
    }

def adjust_for_calorie_target(recommendations, calorie_target):
    """Adjust recommendations to meet overall calorie target"""
    min_calories, max_calories = calorie_target
    
    # Calculate current total calories
    total_calories = 0
    for meal, recipes in recommendations.items():
        for recipe in recipes:
            # Extract calories from nutrition info
            # This is a placeholder for the actual extraction logic
            total_calories += extract_calories_from_recipe(recipe)
    
    # If total is outside target range, adjust by replacing recipes
    if total_calories < min_calories or total_calories > max_calories:
        # Find recipes to replace based on calorie content
        adjust_recipes_to_meet_calorie_target(recommendations, total_calories, calorie_target)

def extract_calories_from_recipe(recipe):
    """Extract calorie information from recipe nutrition data"""
    # This is a placeholder for the actual extraction logic
    for item in recipe.nutrition:
        if 'calories' in item.lower():
            # Extract numeric value from string like "calories: 350"
            match = re.search(r'calories:\s*(\d+)', item.lower())
            if match:
                return int(match.group(1))
    return 0

def adjust_recipes_to_meet_calorie_target(recommendations, current_calories, target_range):
    """Replace recipes to meet calorie target"""
    min_calories, max_calories = target_range
    
    if current_calories < min_calories:
        # Replace some recipes with higher-calorie alternatives
        deficit = min_calories - current_calories
        replace_recipes_to_adjust_calories(recommendations, deficit, increase=True)
    
    elif current_calories > max_calories:
        # Replace some recipes with lower-calorie alternatives
        excess = current_calories - max_calories
        replace_recipes_to_adjust_calories(recommendations, excess, increase=False)

def replace_recipes_to_adjust_calories(recommendations, calorie_difference, increase=True):
    """Replace recipes to adjust total calories"""
    # This is a placeholder for the recipe replacement logic
    # In a real implementation, this would find alternative recipes with more/less calories
    # while still matching other criteria
    pass

def shuffle(recipes):
    """Add randomness to recipe selection"""
    # This is a placeholder for random shuffling
    # In a real implementation, this would use random.shuffle or similar
    import random
    random.shuffle(recipes)