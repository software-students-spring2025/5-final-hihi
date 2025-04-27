import random

def recommend_recipes(user_preferences, database):
    # 1. Extract user preferences directly
    
    # Extract diet & allergy preferences (question1)
    diet_selections = user_preferences.get('question1', [10])  # Default: No specific requirement
    
    # Build dietary constraints directly
    diet_requirements = {}
    allergy_tags_to_exclude = []
    diet_tags_to_include = []
    
    # Map diet selections to tags and allergies
    for selection in diet_selections:
        if selection == 1:  # Vegetarian
            diet_tags_to_include.append('vegetarian')
        elif selection == 2:  # Vegan
            diet_tags_to_include.append('vegan')
        elif selection == 3:  # Dietary
            diet_tags_to_include.append('dietary')
        elif selection == 4:  # Gluten-free
            diet_tags_to_include.append('gluten-free')
        elif selection == 5:  # Kosher
            diet_tags_to_include.append('kosher')
        elif selection == 6:  # Lactose-free
            diet_tags_to_include.append('lactose-free')
        elif selection == 7:  # Eggs/dairy allergy
            allergy_tags_to_exclude.append('eggs_dairy')
        elif selection == 8:  # Seafood allergy
            allergy_tags_to_exclude.append('seafood')
        elif selection == 9:  # Nuts allergy
            allergy_tags_to_exclude.append('nuts')
        # Option 10 is "No specific requirement", so we don't add anything
    
    # Extract calorie preference (question2)
    calorie_option = user_preferences.get('question2', 7)  # Default: No specific requirement
    
    # Extract time preference (question3)
    time_option = user_preferences.get('question3', 6)  # Default: No specific requirement
    
    # Extract cuisine preferences (question4)
    cuisine_selections = user_preferences.get('question4', [15])  # Default: No specific requirement
    
    # Convert cuisine selections to tags
    cuisine_tags = []
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
    
    for selection in cuisine_selections:
        if selection != 15 and selection in cuisine_mapping:  # Skip "No specific requirement"
            cuisine_tags.append(cuisine_mapping[selection])
    
    # Extract cooking experience (question5)
    is_beginner = user_preferences.get('question5', 2) == 1  # Check if beginner (1 = beginner)
    
    # Extract meal types (question6)
    meal_type_selections = user_preferences.get('question6', [])
    meal_types = []
    meal_mapping = {
        1: 'breakfast',
        2: 'brunch',
        3: 'lunch',
        4: 'dinner'
    }
    
    for selection in meal_type_selections:
        if selection in meal_mapping:
            meal_types.append(meal_mapping[selection])
    
    # Extract dish types (question7)
    dish_type_selections = user_preferences.get('question7', [1])  # Default: Main dish
    dish_types = []
    dish_mapping = {
        1: "main-dish",
        2: "side-dish",
        3: "dessert",
        4: "appetizer",
        5: "soup",
        6: "beverage"
    }
    
    for selection in dish_type_selections:
        if selection in dish_mapping:
            dish_types.append(dish_mapping[selection])
    
    # 2. Create base query with diet & allergy requirements (highest priority)
    query = {}
    
    # Add dietary tags requirement if specified
    if diet_tags_to_include:
        query['tags'] = {'$all': diet_tags_to_include}
    
    # Add allergy exclusions if specified
    if allergy_tags_to_exclude:
        # Check if we need to handle both tags fields
        allergy_condition = {'$nin': allergy_tags_to_exclude}
        
        if 'tags' in query:
            # We already have tag requirements, need to combine
            query = {
                '$and': [
                    {'tags': query['tags']},  # Keep existing diet requirements
                    {'tags': allergy_condition}  # Add allergy exclusions
                ]
            }
        else:
            # Just add the allergy exclusions
            query['tags'] = allergy_condition
    
    # Add time constraint if specified
    if time_option != 6:  # Not "No specific requirement"
        time_limits = {
            1: 30,            # Less than 30 minutes
            2: 60,            # 30 minutes to 1 hour
            3: 90,            # 1 hour to 1.5 hours
            4: 120,           # 1.5 hours to 2 hours
            5: float('inf')   # More than 2 hours
        }
        
        # Get the selected time limit
        max_minutes = time_limits[time_option]
        
        # For option 5 (more than 2 hours), we need a lower bound
        if time_option == 5:
            query['minutes'] = {'$gt': 120}  # Greater than 2 hours
        else:
            # For options 1-4, we need an upper bound
            query['minutes'] = {'$lte': max_minutes}
    
    # 3. Set up recommendations container
    recommendations = {meal: [] for meal in meal_types}
    used_recipe_ids = set()  # Track already recommended recipes
    
    # 4. Calculate calorie ranges for each meal using hardcoded weights
    meal_calorie_ranges = {}
    
    # Only process calories if a specific requirement was selected
    if calorie_option != 7:  # Not "No specific requirement"
        # Define calorie ranges based on selection
        calorie_ranges = {
            1: (1200, 1400),  # Very low
            2: (1400, 1600),  # Low
            3: (1600, 1800),  # Moderate
            4: (1800, 2200),  # Balanced
            5: (2200, 2500),  # High
            6: (2500, 3000)   # Very high
        }
        
        # Get the selected calorie range
        min_calories, max_calories = calorie_ranges[calorie_option]
        
        # Define meal weight ratios
        meal_weights = {
            'breakfast': (0.9, 1.1),
            'brunch': (1.8, 2.1),
            'lunch': (2.1, 2.5),
            'dinner': (1.9, 2.3)
        }
        
        # Calculate total weight range
        total_min_weight = sum(meal_weights.get(meal, (1.0, 1.0))[0] for meal in meal_types)
        total_max_weight = sum(meal_weights.get(meal, (1.0, 1.0))[1] for meal in meal_types)
        
        # Calculate calorie range for each meal
        for meal in meal_types:
            min_weight, max_weight = meal_weights.get(meal, (1.0, 1.0))
            min_meal_calories = int(min_calories * (min_weight / total_max_weight))
            max_meal_calories = int(max_calories * (max_weight / total_min_weight))
            meal_calorie_ranges[meal] = (min_meal_calories, max_meal_calories)
    
    # 5. For each meal type, find suitable recipes
    for meal in meal_types:
        meal_query = query.copy()
        
        # Add meal-specific criteria
        if 'tags' not in meal_query:
            meal_query['tags'] = {'$in': [meal]}
        elif '$all' in meal_query['tags']:
            meal_query['tags']['$all'].append(meal)
        elif '$in' in meal_query['tags']:
            meal_query['tags']['$in'].append(meal)
        elif '$and' in meal_query:
            # Complex query with $and, need to modify the right condition
            for condition in meal_query['$and']:
                if 'tags' in condition and '$all' in condition['tags']:
                    condition['tags']['$all'].append(meal)
                    break
            else:
                # No suitable condition found, add a new one
                meal_query['$and'].append({'tags': {'$in': [meal]}})
        else:
            # Just add the meal tag as a new condition
            meal_query['tags'] = {'$in': [meal]}
        
        # Add beginner-friendly tags if needed
        if is_beginner:
            beginner_tags = ['easy', 'beginner-cook', 'kid-friendly']
            
            if 'tags' not in meal_query:
                meal_query['tags'] = {'$in': beginner_tags}
            elif '$in' in meal_query['tags']:
                meal_query['tags']['$in'].extend(beginner_tags)
            elif '$all' in meal_query['tags']:
                # Can't add $in to $all directly, need to use $and
                if '$and' not in meal_query:
                    meal_query = {
                        '$and': [
                            {'tags': meal_query['tags']},
                            {'tags': {'$in': beginner_tags}}
                        ]
                    }
                else:
                    meal_query['$and'].append({'tags': {'$in': beginner_tags}})
            elif '$and' in meal_query:
                meal_query['$and'].append({'tags': {'$in': beginner_tags}})
            else:
                # Convert to $and query
                meal_query = {
                    '$and': [
                        {'tags': meal_query['tags']},
                        {'tags': {'$in': beginner_tags}}
                    ]
                }
        
        # Add cuisine tags if specified
        if cuisine_tags:
            if 'tags' not in meal_query:
                meal_query['tags'] = {'$in': cuisine_tags}
            elif '$in' in meal_query['tags']:
                meal_query['tags']['$in'].extend(cuisine_tags)
            elif '$all' in meal_query['tags']:
                # Can't add $in to $all directly, need to use $and
                if '$and' not in meal_query:
                    meal_query = {
                        '$and': [
                            {'tags': meal_query['tags']},
                            {'tags': {'$in': cuisine_tags}}
                        ]
                    }
                else:
                    meal_query['$and'].append({'tags': {'$in': cuisine_tags}})
            elif '$and' in meal_query:
                meal_query['$and'].append({'tags': {'$in': cuisine_tags}})
            else:
                # Convert to $and query
                meal_query = {
                    '$and': [
                        {'tags': meal_query['tags']},
                        {'tags': {'$in': cuisine_tags}}
                    ]
                }
        
        # Add calorie constraints for this meal if specified
        if meal in meal_calorie_ranges:
            min_meal_cal, max_meal_cal = meal_calorie_ranges[meal]
            meal_query['nutrition.calories'] = {'$gte': min_meal_cal, '$lte': max_meal_cal}
        
        # For lunch/dinner, handle dish types separately with weighted calorie distribution
        if meal in ['lunch', 'dinner']:
            # Define dish type weights for calorie distribution
            dish_weights = {
                'main-dish': 0.6,
                'side-dish': 0.2,
                'dessert': 0.15,
                'appetizer': 0.15,
                'soup': 0.25,
                'beverage': 0.05
            }
            
            # Normalize weights based on selected dish types
            total_dish_weight = sum(dish_weights.get(dish, 0.5) for dish in dish_types)
            
            for dish in dish_types:
                dish_query = meal_query.copy()
                
                # Add dish tag to query
                if 'tags' not in dish_query:
                    dish_query['tags'] = {'$in': [dish]}
                elif '$in' in dish_query['tags']:
                    dish_query['tags']['$in'].append(dish)
                elif '$all' in dish_query['tags']:
                    # Can't add $in to $all directly, need to use $and
                    if '$and' not in dish_query:
                        dish_query = {
                            '$and': [
                                {'tags': dish_query['tags']},
                                {'tags': {'$in': [dish]}}
                            ]
                        }
                    else:
                        dish_query['$and'].append({'tags': {'$in': [dish]}})
                elif '$and' in dish_query:
                    dish_query['$and'].append({'tags': {'$in': [dish]}})
                else:
                    # Convert to $and query
                    dish_query = {
                        '$and': [
                            {'tags': dish_query['tags']},
                            {'tags': {'$in': [dish]}}
                        ]
                    }
                
                # Adjust calorie range for this specific dish type if needed
                if meal in meal_calorie_ranges and total_dish_weight > 0:
                    dish_weight = dish_weights.get(dish, 0.5) / total_dish_weight
                    min_meal_cal, max_meal_cal = meal_calorie_ranges[meal]
                    min_dish_cal = int(min_meal_cal * dish_weight * 0.8)  # Allow 20% flexibility
                    max_dish_cal = int(max_meal_cal * dish_weight * 1.2)  # Allow 20% flexibility
                    dish_query['nutrition.calories'] = {'$gte': min_dish_cal, '$lte': max_dish_cal}
                
                # Exclude already recommended recipes
                dish_query['_id'] = {'$nin': list(used_recipe_ids)}
                
                # Find 1 recipe per dish type
                matching_recipe = database.find_one(dish_query)
                
                if matching_recipe:
                    recommendations[meal].append(matching_recipe)
                    used_recipe_ids.add(matching_recipe['_id'])
                else:
                    # If no exact match, try relaxing constraints
                    relaxed_recipe = find_with_relaxed_constraints(dish_query, database, diet_tags_to_include, allergy_tags_to_exclude, dish)
                    if relaxed_recipe:
                        recommendations[meal].append(relaxed_recipe)
                        used_recipe_ids.add(relaxed_recipe['_id'])
        else:
            # For breakfast/brunch, just find matches
            breakfast_query = meal_query.copy()
            breakfast_query['_id'] = {'$nin': list(used_recipe_ids)}
            
            matching_recipes = database.find(breakfast_query, limit=2)
            
            for recipe in matching_recipes:
                recommendations[meal].append(recipe)
                used_recipe_ids.add(recipe['_id'])
    
    # Random shuffling for variety
    for meal in recommendations:
        random.shuffle(recommendations[meal])
    
    return recommendations

def find_with_relaxed_constraints(original_query, database, diet_tags, allergy_tags, dish_type=None):
    """Find a recipe with relaxed constraints while maintaining dietary requirements"""
    # Start with dietary restrictions only (highest priority)
    relaxed_query = {}
    
    # Always keep dietary requirements
    if diet_tags:
        relaxed_query['tags'] = {'$all': diet_tags}
    
    # Always maintain allergy exclusions
    if allergy_tags:
        if 'tags' in relaxed_query:
            relaxed_query = {
                '$and': [
                    {'tags': relaxed_query['tags']},
                    {'tags': {'$nin': allergy_tags}}
                ]
            }
        else:
            relaxed_query['tags'] = {'$nin': allergy_tags}
    
    # Add dish type if specified
    if dish_type:
        if 'tags' not in relaxed_query:
            relaxed_query['tags'] = {'$in': [dish_type]}
        elif '$all' in relaxed_query['tags']:
            # Convert to $and query
            relaxed_query = {
                '$and': [
                    {'tags': relaxed_query['tags']},
                    {'tags': {'$in': [dish_type]}}
                ]
            }
        elif '$nin' in relaxed_query['tags']:
            # Already have $nin condition
            relaxed_query = {
                '$and': [
                    {'tags': relaxed_query['tags']},
                    {'tags': {'$in': [dish_type]}}
                ]
            }
        elif '$and' in relaxed_query:
            relaxed_query['$and'].append({'tags': {'$in': [dish_type]}})
    
    # Exclude already selected recipes
    if '_id' in original_query:
        relaxed_query['_id'] = original_query['_id']
    
    # Try to find a matching recipe
    recipe = database.find_one(relaxed_query)
    
    return recipe