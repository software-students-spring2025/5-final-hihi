from mongoengine import Document, StringField, IntField, EmailField, MapField, BooleanField, ReferenceField, DateField, FloatField, ListField
from datetime import datetime
import re
import random
import json
from bson import ObjectId

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
    cooking_experience = extract_cooking_experience(user_preferences.get('question5', 2))  # Default: Skilled
    meal_types = extract_meal_types(user_preferences.get('question6', []))
    dish_types = extract_dish_types(user_preferences.get('question7', []))
    
    # 2. Create base query for recipe filtering
    base_query = {}
    
    # 3. Apply beginner cook mode if selected (look for "beginner-cook" or "easy" tags)
    if cooking_experience == 1:  # Beginner
        base_query['tags'] = {'$in': ['beginner-cook', 'easy', 'kid-friendly']}
    
    # 4. Apply strict dietary restrictions and allergies (highest priority)
    if diet_allergies:
        base_query.update(build_dietary_query(diet_allergies))
    
    # 5. Add cuisine preferences if specified
    if cuisines != [15]:  # If not "No specific requirement"
        base_query.update(build_cuisine_query(cuisines))
    
    # 6. Calculate per-meal calorie distribution if specified
    meal_calorie_ranges = calculate_meal_calories(calorie_intake, meal_types)
    
    # 7. Initialize results dictionary
    recommendations = {meal.lower(): [] for meal in meal_types}
    
    # 8. Generate recommendations for each selected meal
    for meal in meal_types:
        meal_lower = meal.lower()
        meal_query = base_query.copy()
        
        # Add meal tag to query
        if meal_lower in ['breakfast', 'brunch']:
            if 'tags' in meal_query and '$in' in meal_query['tags']:
                meal_query['tags']['$in'].append(meal_lower)
            else:
                meal_query['tags'] = {'$in': [meal_lower]}
        
        # Add time constraint if specified
        if prep_time != 6:  # If time constraint specified
            max_minutes = convert_time_preference_to_minutes(prep_time)
            meal_query['minutes'] = {'$lte': max_minutes}
        
        # Add calorie constraint if specified
        if meal_calorie_ranges[meal] and calorie_intake != 7:
            min_cal, max_cal = meal_calorie_ranges[meal]
            meal_query['nutrition.calories'] = {'$gte': min_cal, '$lte': max_cal}
        
        # For lunch and dinner, handle different dish types
        if meal_lower in ['lunch', 'dinner']:
            # Track recipes we've already added to avoid duplicates
            added_recipe_ids = set()
            
            for dish_type in dish_types:
                dish_query = meal_query.copy()
                dish_tag = convert_dish_type_to_tag(dish_type)
                
                # Add dish type to query tags
                if 'tags' in dish_query and '$in' in dish_query['tags']:
                    dish_query['tags']['$in'].append(dish_tag)
                else:
                    dish_query['tags'] = {'$in': [dish_tag]}
                
                # Exclude already added recipes
                if added_recipe_ids:
                    dish_query['_id'] = {'$nin': list(added_recipe_ids)}
                
                # Find recipes matching criteria
                matching_recipes = find_recipes(dish_query, limit=1)  # Get 1 recipe per dish type
                
                # If no recipes found, try relaxing constraints while maintaining dietary requirements
                if not matching_recipes:
                    matching_recipes = find_recipes_with_relaxed_constraints(
                        dish_query, 
                        diet_allergies,
                        dish_tag,
                        strict_cuisine=(cuisines != [15]),
                        limit=1,
                        exclude_ids=added_recipe_ids
                    )
                
                # Add recipes to recommendations and track their IDs
                for recipe in matching_recipes:
                    recommendations[meal_lower].append(recipe)
                    added_recipe_ids.add(recipe.id)
        else:
            # For breakfast and brunch, just get recipes of that type
            matching_recipes = find_recipes(meal_query, limit=2)  # Get 2 recipes for breakfast/brunch
            
            # If no recipes found, try relaxing constraints while maintaining dietary requirements
            if not matching_recipes:
                matching_recipes = find_recipes_with_relaxed_constraints(
                    meal_query, 
                    diet_allergies,
                    meal_type=meal_lower,
                    strict_cuisine=(cuisines != [15]),
                    limit=2
                )
            
            # Add recipes to recommendations
            recommendations[meal_lower].extend(matching_recipes)
        
        # Ensure we don't have duplicates within a meal
        seen_ids = set()
        unique_recipes = []
        for recipe in recommendations[meal_lower]:
            if recipe.id not in seen_ids:
                seen_ids.add(recipe.id)
                unique_recipes.append(recipe)
        recommendations[meal_lower] = unique_recipes
    
    # 9. Apply randomness to ensure variety
    for meal in recommendations:
        random.shuffle(recommendations[meal])
        
    # 10. Check if calorie constraints are met for the whole day
    if calorie_intake != 7:  # If specific calorie intake was requested
        adjust_for_calorie_target(recommendations, calorie_intake)
    
    # 11. Record recommendations in history for future reference
    record_recommendations(recommendations, user_preferences)
    
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

def extract_prep_time(selection):
    """Convert time preference selection to time range"""
    return selection

def extract_cuisines(selections):
    """Convert cuisine selections to list of cuisine types"""
    return selections

def extract_cooking_experience(selection):
    """Extract cooking experience level"""
    return selection

def extract_meal_types(selections):
    """Convert meal type selections to list of meal types"""
    meal_mapping = {
        1: 'Breakfast',
        2: 'Brunch',
        3: 'Lunch',
        4: 'Dinner'
    }
    return [meal_mapping.get(selection) for selection in selections]

def extract_dish_types(selections):
    """Convert dish type selections to list of dish types"""
    return selections

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

def convert_dish_type_to_tag(dish_type):
    """Convert dish type selection to recipe tag"""
    mapping = {
        1: "main-dish",
        2: "side-dish",
        3: "dessert",
        4: "appetizer",
        5: "soup",
        6: "beverage"
    }
    return mapping.get(dish_type, "main-dish")

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
    tag_conditions = []
    ingredients_to_exclude = []
    
    # Handle vegetarian/vegan requirements
    if diet_allergies.get('vegetarian'):
        tag_conditions.append('vegetarian')
    if diet_allergies.get('vegan'):
        tag_conditions.append('vegan')
    if diet_allergies.get('gluten_free'):
        tag_conditions.append('gluten-free')
    if diet_allergies.get('kosher'):
        tag_conditions.append('kosher')
    if diet_allergies.get('lactose'):
        tag_conditions.append('lactose-free')
    
    # Add tag conditions to query
    if tag_conditions:
        query['tags'] = {'$all': tag_conditions}
    
    # Handle allergies (ingredients to exclude)
    if diet_allergies.get('eggs_dairy') is False:
        ingredients_to_exclude.extend(['egg', 'milk', 'cheese', 'cream', 'butter', 'yogurt'])
    if diet_allergies.get('seafood') is False:
        ingredients_to_exclude.extend(['fish', 'shrimp', 'lobster', 'crab', 'clam', 'mussel', 'oyster'])
    if diet_allergies.get('nuts') is False:
        ingredients_to_exclude.extend(['peanut', 'almond', 'walnut', 'cashew', 'pecan', 'hazelnut', 'pistachio'])
    
    if ingredients_to_exclude:
        # Create regex pattern to exclude ingredients
        regex_pattern = '|'.join(ingredients_to_exclude)
        ingredients_query = {
            'ingredients': {'$not': {'$regex': regex_pattern, '$options': 'i'}}
        }
        
        # Combine with existing query
        if query:
            query = {'$and': [query, ingredients_query]}
        else:
            query = ingredients_query
    
    return query

def build_cuisine_query(cuisine_selections):
    """Build MongoDB query for cuisine preferences"""
    cuisine_mapping = {
        1: "north-american",
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
        13: "middle-eastern",
        14: "chinese"
    }
    
    cuisine_tags = [cuisine_mapping.get(selection) for selection in cuisine_selections if selection != 15]
    if not cuisine_tags:
        return {}
    
    # Try to match any of the selected cuisines
    return {'tags': {'$in': cuisine_tags}}

def find_recipes(query, limit=5):
    """Query database for recipes matching criteria"""
    try:
        # In a real system, this would query the MongoDB collection
        # For demonstration, we'll simulate with a simple filter function
        recipes = Recipe.objects(__raw__=query).limit(limit)
        return list(recipes)
    except Exception as e:
        print(f"Error querying database: {e}")
        return []

def find_recipes_with_relaxed_constraints(original_query, diet_allergies, dish_tag=None, 
                                         meal_type=None, strict_cuisine=False, limit=5,
                                         exclude_ids=None):
    """Find recipes by gradually relaxing non-essential constraints"""
    # Clone the original query to avoid modifying it
    query = original_query.copy()
    
    # Exclude already selected recipes
    if exclude_ids:
        if '_id' in query and '$nin' in query['_id']:
            query['_id']['$nin'].extend(list(exclude_ids))
        else:
            query['_id'] = {'$nin': list(exclude_ids)}
    
    # Priority levels for relaxing constraints (from least to most important)
    # 1. Relax time constraints
    if 'minutes' in query:
        relaxed_query = query.copy()
        del relaxed_query['minutes']
        recipes = find_recipes(relaxed_query, limit)
        if recipes:
            return recipes
    
    # 2. Relax calorie constraints
    if 'nutrition.calories' in query:
        relaxed_query = query.copy()
        del relaxed_query['nutrition.calories']
        recipes = find_recipes(relaxed_query, limit)
        if recipes:
            return recipes
    
    # 3. Relax cuisine constraints if not strict
    if not strict_cuisine and 'tags' in query and '$in' in query['tags']:
        relaxed_query = query.copy()
        
        # Keep dietary tags and meal/dish type tags
        essential_tags = []
        
        # Extract essential tags based on diet
        if diet_allergies.get('vegetarian'):
            essential_tags.append('vegetarian')
        if diet_allergies.get('vegan'):
            essential_tags.append('vegan')
        if diet_allergies.get('gluten_free'):
            essential_tags.append('gluten-free')
        if diet_allergies.get('kosher'):
            essential_tags.append('kosher')
        if diet_allergies.get('lactose'):
            essential_tags.append('lactose-free')
        
        # Add meal or dish tag
        if dish_tag:
            essential_tags.append(dish_tag)
        if meal_type:
            essential_tags.append(meal_type)
        
        if essential_tags:
            relaxed_query['tags'] = {'$all': essential_tags}
        else:
            del relaxed_query['tags']
            
        recipes = find_recipes(relaxed_query, limit)
        if recipes:
            return recipes
    
    # 4. Last resort: Keep only allergy restrictions and meal/dish type
    minimal_query = {}
    
    # Keep exclusion of already added recipes
    if exclude_ids:
        minimal_query['_id'] = {'$nin': list(exclude_ids)}
    
    # Extract ingredients to exclude from allergies
    ingredients_to_exclude = []
    if diet_allergies.get('eggs_dairy') is False:
        ingredients_to_exclude.extend(['egg', 'milk', 'cheese', 'cream', 'butter', 'yogurt'])
    if diet_allergies.get('seafood') is False:
        ingredients_to_exclude.extend(['fish', 'shrimp', 'lobster', 'crab', 'clam', 'mussel', 'oyster'])
    if diet_allergies.get('nuts') is False:
        ingredients_to_exclude.extend(['peanut', 'almond', 'walnut', 'cashew', 'pecan', 'hazelnut', 'pistachio'])
    
    if ingredients_to_exclude:
        regex_pattern = '|'.join(ingredients_to_exclude)
        minimal_query['ingredients'] = {'$not': {'$regex': regex_pattern, '$options': 'i'}}
    
    # Add essential diet tags
    diet_tags = []
    if diet_allergies.get('vegetarian'):
        diet_tags.append('vegetarian')
    if diet_allergies.get('vegan'):
        diet_tags.append('vegan')
    
    # Add meal or dish type tag
    type_tags = []
    if dish_tag:
        type_tags.append(dish_tag)
    if meal_type:
        type_tags.append(meal_type)
    
    all_tags = diet_tags + type_tags
    if all_tags:
        minimal_query['tags'] = {'$all': all_tags}
    
    return find_recipes(minimal_query, limit)

def extract_calories_from_recipe(recipe):
    """Extract calorie information from recipe"""
    # Based on the sample data structure
    if hasattr(recipe, 'nutrition') and isinstance(recipe.nutrition, dict) and 'calories' in recipe.nutrition:
        return float(recipe.nutrition['calories'])
    return 0

def calculate_total_calories(recommendations):
    """Calculate total calories across all recommended recipes"""
    total = 0
    for meal, recipes in recommendations.items():
        for recipe in recipes:
            total += extract_calories_from_recipe(recipe)
    return total

def adjust_for_calorie_target(recommendations, calorie_target):
    """Adjust recommendations to meet overall calorie target"""
    min_calories, max_calories = calorie_target
    
    # Calculate current total calories
    total_calories = calculate_total_calories(recommendations)
    
    # If total is within target range, no adjustment needed
    if min_calories <= total_calories <= max_calories:
        return
    
    # If outside range, adjust by replacing recipes
    if total_calories < min_calories:
        # Increase calories
        calorie_deficit = min_calories - total_calories
        adjust_recipe_calories(recommendations, calorie_deficit, increase=True)
    else:
        # Decrease calories
        calorie_excess = total_calories - max_calories
        adjust_recipe_calories(recommendations, calorie_excess, increase=False)

def adjust_recipe_calories(recommendations, calorie_difference, increase=True):
    """Replace recipes to adjust total calories"""
    # Sort meals by priority for adjustment
    priority_order = ['dinner', 'lunch', 'brunch', 'breakfast']
    remaining_difference = calorie_difference
    
    for meal in priority_order:
        if meal not in recommendations or not recommendations[meal]:
            continue
        
        # Sort recipes by calorie content
        recipes = recommendations[meal]
        recipes.sort(key=extract_calories_from_recipe, 
                     reverse=(not increase))  # Highest first if decreasing, lowest first if increasing
        
        # Attempt to replace recipes
        for i, recipe in enumerate(recipes):
            current_calories = extract_calories_from_recipe(recipe)
            
            # Calculate target calories for replacement
            target_calories = current_calories + remaining_difference if increase else current_calories - remaining_difference
            
            # Find a replacement recipe with appropriate calorie content
            replacement = find_replacement_recipe(
                recipe, 
                target_calories, 
                tolerance=0.2,  # Allow 20% tolerance
                increase=increase
            )
            
            if replacement:
                # Calculate actual calorie difference
                replacement_calories = extract_calories_from_recipe(replacement)
                actual_difference = replacement_calories - current_calories
                
                # Update recipe and remaining difference
                recipes[i] = replacement
                remaining_difference -= abs(actual_difference)
                
                # If target reached, exit
                if remaining_difference <= 0:
                    return
    
    # If we get here, we've adjusted as much as possible
    print(f"Could not fully adjust calorie content. Remaining difference: {remaining_difference}")

def find_replacement_recipe(original_recipe, target_calories, tolerance=0.2, increase=True):
    """Find a replacement recipe with similar characteristics but different calorie content"""
    # Extract key characteristics to match
    tags = original_recipe.tags
    
    # Calculate calorie range
    min_cal = target_calories * (1 - tolerance)
    max_cal = target_calories * (1 + tolerance)
    
    # Construct query to find similar recipes
    query = {
        'tags': {'$in': tags},
        '_id': {'$ne': original_recipe.id}  # Exclude original recipe
    }
    
    # Add calorie constraint
    query['nutrition.calories'] = {'$gte': min_cal, '$lte': max_cal}
    
    # Find potential replacements
    potential_replacements = find_recipes(query, limit=10)
    
    # If no exact matches, find closest match
    if not potential_replacements:
        # Remove calorie constraint
        del query['nutrition.calories']
        potential_replacements = find_recipes(query, limit=20)
        
        if potential_replacements:
            # Sort by closest calorie content
            potential_replacements.sort(
                key=lambda r: abs(extract_calories_from_recipe(r) - target_calories)
            )
            return potential_replacements[0]
        return None
    
    # Return random replacement from filtered list
    return random.choice(potential_replacements) if potential_replacements else None

def record_recommendations(recommendations, user_preferences):
    """Record recommendations in history for future reference"""
    # In a real application, this would save to the database
    # For this example, just print a summary
    total_recipes = sum(len(recipes) for recipes in recommendations.values())
    print(f"Generated {total_recipes} recipe recommendations across {len(recommendations)} meals")


# Sample Recipe class to match the provided data format
class Recipe(Document):
    meta = {'collection': 'recipes'}
    
    name = StringField(required=True)
    minutes = IntField(min_value=0)
    tags = ListField(StringField())
    nutrition = MapField(FloatField())  # Changed to MapField for nutrition values
    steps = ListField(StringField())
    description = StringField()
    ingredients = ListField(StringField())
    
    @classmethod
    def from_json(cls, json_data):
        """Create Recipe instance from JSON data"""
        recipe = cls()
        recipe.name = json_data.get('name', '')
        recipe.minutes = json_data.get('minutes', {}).get('$numberInt', 0)
        recipe.tags = json_data.get('tags', [])
        
        # Parse nutrition data
        nutrition_data = json_data.get('nutrition', {})
        recipe.nutrition = {}
        for key, value in nutrition_data.items():
            if isinstance(value, dict) and '$numberDouble' in value:
                recipe.nutrition[key] = float(value['$numberDouble'])
            else:
                recipe.nutrition[key] = float(value)
        
        recipe.steps = json_data.get('steps', [])
        recipe.description = json_data.get('description', '')
        recipe.ingredients = json_data.get('ingredients', [])
        
        # Set an ID if provided
        if '_id' in json_data and '$oid' in json_data['_id']:
            recipe.id = ObjectId(json_data['_id']['$oid'])
        
        return recipe


# Function to run the recommendation algorithm with the provided sample data
def test_recommendation_algorithm():
    """Test the recommendation algorithm with sample data"""
    # Create sample recipes from the provided JSON data
    sample_recipes = [
        Recipe.from_json({
            "_id": {"$oid": "68095ec2221ef4f19ef99030"},
            "name": "a bit different breakfast pizza",
            "minutes": {"$numberInt": "30"},
            "tags": ["30-minutes-or-less", "time-to-make", "course", "main-ingredient", 
                    "cuisine", "preparation", "occasion", "north-american", "breakfast", 
                    "main-dish", "pork", "american", "oven", "easy", "kid-friendly", 
                    "pizza", "dietary", "northeastern-united-states", "meat", "equipment"],
            "nutrition": {
                "calories": {"$numberDouble": "173.4"},
                "total_fat": {"$numberDouble": "18.0"},
                "sugar": {"$numberDouble": "0.0"},
                "sodium": {"$numberDouble": "17.0"},
                "protein": {"$numberDouble": "22.0"},
                "saturated_fat": {"$numberDouble": "35.0"},
                "carbohydrates": {"$numberDouble": "1.0"}
            },
            "steps": ["preheat oven to 425 degrees f", "press dough into the bottom and sides of a 12 inch pizza pan", 
                    "bake for 5 minutes until set but not browned", "cut sausage into small pieces", 
                    "whisk eggs and milk in a bowl until frothy", "spoon sausage over baked crust and sprinkle with cheese", 
                    "pour egg mixture slowly over sausage and cheese", "s& p to taste", 
                    "bake 15-20 minutes or until eggs are set and crust is brown"],
            "description": "this recipe calls for the crust to be prebaked a bit before adding ingredients. feel free to change sausage to ham or bacon. this warms well in the microwave for those late risers.",
            "ingredients": ["prepared pizza crust", "sausage patty", "eggs", "milk", "salt and pepper", "cheese"]
        }),
        Recipe.from_json({
            "_id": {"$oid": "68095ec2221ef4f19ef99042"},
            "name": "cream of spinach soup vegan",
            "minutes": {"$numberInt": "55"},
            "tags": ["60-minutes-or-less", "time-to-make", "course", "main-ingredient", 
                    "preparation", "occasion", "bisques-cream-soups", "main-dish", 
                    "soups-stews", "vegetables", "vegan", "vegetarian", "stove-top", 
                    "dietary", "one-dish-meal", "low-cholesterol", "low-saturated-fat", 
                    "low-calorie", "comfort-food", "low-in-something", "taste-mood", "equipment"],
            "nutrition": {
                "calories": {"$numberDouble": "64.8"},
                "total_fat": {"$numberDouble": "3.0"},
                "sugar": {"$numberDouble": "13.0"},
                "sodium": {"$numberDouble": "54.0"},
                "protein": {"$numberDouble": "4.0"},
                "saturated_fat": {"$numberDouble": "2.0"},
                "carbohydrates": {"$numberDouble": "3.0"}
            },
            "steps": ["in a 3 qt saucepan over medium high heat , saute the onions and scallions in the apple juice and oil for 5 minutes , stirring frequently", 
                    "add the spinach , parsley and celery", 
                    "cook for 5-7 minutes , stirring occasionally add the broth , oats , salt , thyme and pepper", 
                    "bring to a boil , then lower the heat to medium", 
                    "cover and simmer for 20 minutes", 
                    "remove from the heat", 
                    "let the soup cool for 10 minutes", 
                    "working in batches , puree in a blender until thick and smooth", 
                    "return to the pot", 
                    "reheat and serve"],
            "description": "thickened with a mix of cooked oats and vegies, this soup has all the flavor of the original with a fraction of the fat stuff. low in cholestorol too!",
            "ingredients": ["onion", "scallion", "apple juice", "olive oil", "spinach", 
                            "fresh parsley", "celery", "broth", "rolled oats", "salt", 
                            "dried thyme", "white pepper"]
        }),
        Recipe.from_json({
            "_id": {"$oid": "68095ec2221ef4f19ef9905d"},
            "name": "jiffy extra moist carrot cake",
            "minutes": {"$numberInt": "50"},
            "tags": ["60-minutes-or-less", "time-to-make", "course", "main-ingredient", 
                    "preparation", "occasion", "desserts", "eggs-dairy", "fruit", 
                    "vegetables", "oven", "easy", "kid-friendly", "picnic", "cakes", 
                    "nuts", "eggs", "dietary", "comfort-food", "inexpensive", 
                    "tropical-fruit", "pineapple", "taste-mood", "to-go", "equipment"],
            "nutrition": {
                "calories": {"$numberDouble": "612.1"},
                "total_fat": {"$numberDouble": "49.0"},
                "sugar": {"$numberDouble": "170.0"},
                "sodium": {"$numberDouble": "25.0"},
                "protein": {"$numberDouble": "15.0"},
                "saturated_fat": {"$numberDouble": "39.0"},
                "carbohydrates": {"$numberDouble": "25.0"}
            },
            "steps": ["preheat oven to 350 degrees", 
                     "mix together the cake mix , pudding , nutmeg and cinnamon", 
                     "add eggs , oil and water to this mixture", 
                     "mix on medium speed for 1 minute", 
                     "add the pineapple , carrots , pecans and coconut", 
                     "blend well", 
                     "pour into a greased 9 inch round cake pan", 
                     "bake 25 to 30 minutes , until tooth pick inserted in the center comes out clean"],
            "description": "this is a very tasty, moist, carrot cake. a nice sized cake for 2 or 3 people.",
            "ingredients": ["yellow cake mix", "vanilla instant pudding mix", "nutmeg", 
                            "cinnamon", "eggs", "oil", "water", "crushed pineapple", 
                            "carrot", "pecans", "coconut"]
        })
    ]
    
    # Mock the database query function to return sample recipes
    # In a real implementation, this would query the actual database
    def mock_find_recipes(query, limit=5):
        """Mock function to simulate database queries using the sample data"""
        results = []
        
        # Apply filters based on query
        for recipe in sample_recipes:
            match = True
            
            # Check tags (either $in or $all)
            if 'tags' in query:
                if '$in' in query['tags']:
                    # Match any of the specified tags
                    tag_match = False
                    for tag in query['tags']['$in']:
                        if tag in recipe.tags:
                            tag_match = True
                            break
                    match = tag_match
                elif '$all' in query['tags']:
                    # Match all of the specified tags
                    for tag in query['tags']['$all']:
                        if tag not in recipe.tags:
                            match = False
                            break
            
            # Check ingredients exclusion
            if 'ingredients' in query and '$not' in query['ingredients'] and '$regex' in query['ingredients']['$not']:
                pattern = query['ingredients']['$not']['$regex']
                for ingredient in recipe.ingredients:
                    if re.search(pattern, ingredient, re.IGNORECASE):
                        match = False
                        break
            
            # Check minutes constraint
            if 'minutes' in query and '$lte' in query['minutes']:
                if int(recipe.minutes) > query['minutes']['$lte']:
                    match = False
            
            # Check calories constraint
            if 'nutrition.calories' in query:
                calories = extract_calories_from_recipe(recipe)
                if '$gte' in query['nutrition.calories'] and calories < query['nutrition.calories']['$gte']:
                    match = False
                if '$lte' in query['nutrition.calories'] and calories > query['nutrition.calories']['$lte']:
                    match = False
            
            if match:
                results.append(recipe)
        
        # Apply limit
        return results[:limit]
    
    # Replace the actual find_recipes function with our mock
    global find_recipes
    find_recipes = mock_find_recipes
    
    # Test case: Vegan breakfast with easy recipes
    # Test case: Vegan breakfast with easy recipes
    test_preferences = {
        'question1': [2],  # Vegan
        'question2': 3,    # Moderate calories (1600-1800)
        'question3': 2,    # 30 min to 1 hour
        'question4': [3],  # Asian cuisine
        'question5': 1,    # Beginner cook
        'question6': [1, 3],  # Breakfast and Lunch
        'question7': [1, 3, 5]  # Main dish, Desserts, Soups
    }
    
    # Run the recommendation algorithm
    recommendations = recommend_recipes(test_preferences)
    
    # Display results
    print("\nRECOMMENDATION RESULTS:")
    print("=======================")
    for meal, recipes in recommendations.items():
        print(f"\n{meal.upper()}:")
        if not recipes:
            print("  No recipes found meeting all criteria.")
        for i, recipe in enumerate(recipes, 1):
            print(f"  {i}. {recipe.name}")
            print(f"     Time: {recipe.minutes} minutes")
            print(f"     Calories: {extract_calories_from_recipe(recipe)}")
            print(f"     Tags: {', '.join(recipe.tags[:5])}...")
            print(f"     Description: {recipe.description[:100]}...")
    
    return recommendations

# Execute demonstration
if __name__ == "__main__":
    test_recommendation_algorithm()