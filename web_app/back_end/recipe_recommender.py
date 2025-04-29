import random
import copy

def recommend_recipes(user_preferences, database):
    # 1. Extract user preferences
    diet_selections = user_preferences.get('question1', [10])  # Default "no restriction"
    try:
        calorie_option = int(user_preferences.get('question2', 7))
    except (TypeError, ValueError):
        calorie_option = 7      # Default "no restriction"
    try:
        time_option = int(user_preferences.get('question3', 6))
    except (TypeError, ValueError):
        time_option = 6         # Default "any time"
    cuisine_selections = user_preferences.get('question4', [15])  # Default "any cuisine"
    is_beginner = user_preferences.get('question5', 2) == 1    # Default not beginner
    meal_type_selections = user_preferences.get('question6', [])
    dish_type_selections = user_preferences.get('question7', [1])  # Default main dish

    diet_tags_to_include = []
    allergy_tags_to_exclude = []
    cuisine_tags = []
    meal_types = []
    dish_types = []

    # Mappings
    cuisine_mapping = {
        1: "north-american", 2: "european", 3: "asian", 4: "italian",
        5: "mexican", 6: "canadian", 7: "australian", 8: "midwestern",
        9: "african", 10: "indian", 11: "greek", 12: "french",
        13: "middle-eastern", 14: "chinese"
    }
    meal_mapping = {1: 'breakfast', 2: 'brunch', 3: 'lunch', 4: 'dinner'}
    dish_mapping = {
        1: "main-dish", 2: "side-dishes", 3: "desserts",
        4: "appetizers", 5: "soups-stews", 6: "beverages"
    }
    
    # Dish&Meal type weights for calorie distribution
    dish_weights = {
        "main-dish": 2.1, "side-dishes": 1.0, "desserts": 0.9,
        "appetizers": 0.7, "soups-stews": 0.8, "beverages": 0.3
    }
    meal_weights = {
        'breakfast': random.uniform(0.9, 1.1), 'brunch': random.uniform(1.8, 2.1),
        'lunch': random.uniform(2.1, 2.5), 'dinner': random.uniform(1.9, 2.3)
    }
    calorie_ranges = {
        1: (1200, 1400), 2: (1400, 1600), 3: (1600, 1800),
        4: (1800, 2200), 5: (2200, 2500), 6: (2500, 3000)
    }
    time_ranges = {
        1: (0, 30), 2: (30, 60), 3: (60, 90),
        4: (90, 120), 5: (120, float('inf'))
    }

    # Process preferences
    print("Diet Selection: ", diet_selections)
    for selection in diet_selections:
        if selection in ['vegetarian', 'vegan', 'gluten-free', 'kosher', 'lactose-free']:
            diet_tags_to_include.append(selection)
        elif selection == 'eggs_dairy':
            allergy_tags_to_exclude.append('eggs_dairy')
        elif selection == 'seafood':
            allergy_tags_to_exclude.append('seafood')
        elif selection == 'nuts':
            allergy_tags_to_exclude.append('nuts')
    print("Diet: ", allergy_tags_to_exclude)

    print("Cuisine Selections: ", cuisine_selections)
    for selection in cuisine_selections:
        if selection != "any":
            cuisine_tags.append(selection)
    print("Cuisine: ", cuisine_tags)

    """ print(meal_type_selections)
    #meal_mapping_reverse = {v: k for k, v in meal_mapping.items()}
    meal_types = [meal_mapping.get(sel) for sel in meal_type_selections]
    if None in meal_types:
        meal_types = None """

    meal_types = meal_type_selections
    # print(meal_types)
    
    # If no meal types selected, default to all
    if not meal_types:
        meal_types = ['breakfast', 'lunch', 'dinner']

    print("Dish Selections: ", dish_type_selections)
    """ for selection in dish_type_selections:
        if selection in dish_mapping:
            dish_types.append(dish_mapping[selection]) """
    dish_types = dish_type_selections
    print("Dish: ", dish_types)
    
    # If no dish types selected, default to main dish
    if not dish_types:
        dish_types = ["main-dish"]

    # Initialize containers for calorie ranges
    meal_calorie_ranges = {}
    dish_calorie_ranges = {meal: {} for meal in meal_types}
    
    # Calculate meal and dish calorie allocations
    calorie_option = int(calorie_option)
    if calorie_option != 7:
        daily_min_calories, daily_max_calories = calorie_ranges[calorie_option]
    else:
        daily_min_calories = 1500
        daily_max_calories = 4000
    
    # Calculate total weights for proportional distribution
    total_meal_weight = sum(meal_weights.get(meal, 1.0) for meal in meal_types)
    
    # For each meal type
    for meal in meal_types:
        meal_weight = meal_weights.get(meal, 1.0)
        
        # Allocate calories proportionally based on meal weight
        min_meal_calories = int(daily_min_calories * (meal_weight / total_meal_weight))
        max_meal_calories = int(daily_max_calories * (meal_weight / total_meal_weight))
        
        meal_calorie_ranges[meal] = (min_meal_calories, max_meal_calories)
        
        # Calculate total dish weight for this meal
        total_dish_weight = sum(dish_weights.get(dish, 1.0) for dish in dish_types)
        
        # For each dish type within a meal
        for dish in dish_types:
            dish_weight = dish_weights.get(dish, 1.0)
            
            # Proportional allocation based on dish weight
            min_dish_calories = int(min_meal_calories * (dish_weight / total_dish_weight))
            max_dish_calories = int(max_meal_calories * (dish_weight / total_dish_weight))
            
            dish_calorie_ranges[meal][dish] = (min_dish_calories, max_dish_calories)
    
    # Initialize recommendations container
    recommendations = {meal: [] for meal in meal_types}
    used_recipe_ids = set()
    # print(recommendations)
    # Build the query
    for meal in meal_types:                           # ───── MEAL LOOP ─────
        # ───────────────────────────── BREAKFAST / BRUNCH ─────────────────────────────
        if meal in ('breakfast', 'brunch'):
            # For breakfast/brunch, we just need one recipe
            # ---------- build the base query ----------
            query = {}
            query_parts = []

            # ❶ dietary / allergy (always highest priority)
            if diet_tags_to_include:
                query_parts.append({"tags": {"$all": diet_tags_to_include}})
            
            if allergy_tags_to_exclude:
                query_parts.append({"tags": {"$nin": allergy_tags_to_exclude}})

            # ❷ meal tag
            query_parts.append({"tags": {"$in": [meal]}})

            # ❸ time
            time_option = int(time_option)
            if time_option != 6:
                min_t, max_t = time_ranges[time_option]
                if max_t == float('inf'):
                    query_parts.append({"minutes": {"$gte": min_t}})
                else:
                    query_parts.append({"minutes": {"$gte": min_t, "$lte": max_t}})

            # ❹ beginner
            if is_beginner:
                query_parts.append({"tags": {"$in": ['easy', 'beginner-cook']}})

            # ❺ cuisine
            if cuisine_tags:
                query_parts.append({"tags": {"$in": cuisine_tags}})

            # ❻ calories
            has_calorie = False
            if calorie_option != 7 and meal in meal_calorie_ranges:
                cmin, cmax = meal_calorie_ranges[meal]
                query_parts.append({"nutrition.calories": {"$gte": cmin, "$lte": cmax}})
                has_calorie = True

            # Combine all query parts with $and
            if len(query_parts) > 1:
                query = {"$and": query_parts}
            elif len(query_parts) == 1:
                query = query_parts[0]

            # ---------- search ----------
            has_time = any("minutes" in part for part in query_parts) if query_parts else False
            has_cuisine = any("$in" in part.get("tags", {}) and any(tag in cuisine_tags for tag in part["tags"]["$in"]) 
                           for part in query_parts) if query_parts else False
            has_diet = any("$all" in part.get("tags", {}) for part in query_parts) if query_parts else False
            
            # Store search parameters for relaxation strategy
            search_params = {
                "query": query,
                "cuisine_tags": cuisine_tags,
                "has_calorie": has_calorie,
                "has_time": has_time,
                "has_diet": has_diet,
                "diet_tags": diet_tags_to_include,
                "allergy_tags": allergy_tags_to_exclude,
                "meal_tags": [meal],
                "dish_tags": []
            }
            
            # We need exactly one recipe for breakfast/brunch
            matched = list(database.find(query).limit(5))
            matched = [r for r in matched if r['_id'] not in used_recipe_ids]

            if not matched:
                # progressive relaxation with improved strategy
                selected = find_with_improved_relaxation(database, search_params)
                if selected and selected['_id'] not in used_recipe_ids:
                    recommendations[meal] = [selected]
                    used_recipe_ids.add(selected['_id'])
            else:
                selected = random.choice(matched)
                recommendations[meal] = [selected]
                used_recipe_ids.add(selected['_id'])

        # ───────────────────────────── LUNCH / DINNER ─────────────────────────────
        else:
            # Initialize empty list for this meal - clear any previous recipes
            recommendations[meal] = []
            
            # Track which dish types we've found
            found_dish_types = {dish_type: None for dish_type in dish_types}
            
            # For lunch/dinner, we need exactly one recipe per dish type
            for dish_type in dish_types:
                print(f"Finding a {dish_type} for {meal}")
                
                # Build the query for this dish type
                query = {}
                query_parts = []

                # ❶ diet / allergy restrictions
                if diet_tags_to_include:
                    query_parts.append({"tags": {"$all": diet_tags_to_include}})
                
                if allergy_tags_to_exclude:
                    query_parts.append({"tags": {"$nin": allergy_tags_to_exclude}})

                # ❷ meal and dish tags - explicitly require both tags
                #test point 2 here, get rid of meal type
                query_parts.append({"tags": dish_type})

                # ❸ time
                time_option = int(time_option)
                if time_option != 6:
                    min_t, max_t = time_ranges[time_option]
                    if max_t == float('inf'):
                        query_parts.append({"minutes": {"$gte": min_t}})
                    else:
                        query_parts.append({"minutes": {"$gte": min_t, "$lte": max_t}})

                # ❹ beginner
                if is_beginner:
                    query_parts.append({"tags": {"$in": ['easy', 'beginner-cook']}})

                # ❺ cuisine
                if cuisine_tags:
                    query_parts.append({"tags": {"$in": cuisine_tags}})

                # ❻ calories
                has_calorie = False
                calorie_option = int(calorie_option)
                if calorie_option != 7 and dish_type in dish_calorie_ranges.get(meal, {}):
                    cmin, cmax = dish_calorie_ranges[meal][dish_type]
                    query_parts.append({"nutrition.calories": {"$gte": cmin, "$lte": cmax}})
                    has_calorie = True

                # Combine query parts
                if len(query_parts) > 1:
                    query = {"$and": query_parts}
                elif len(query_parts) == 1:
                    query = query_parts[0]

                # Track which constraints are active
                has_time = any("minutes" in part for part in query_parts) if query_parts else False
                has_cuisine = any(part.get("tags", {}) in cuisine_tags for part in query_parts) if query_parts else False
                has_diet = any("$all" in part.get("tags", {}) for part in query_parts) if query_parts else False
                
                # Search parameters for relaxation
                search_params = {
                    "query": query,
                    "cuisine_tags": cuisine_tags,
                    "has_calorie": has_calorie,
                    "has_time": has_time,
                    "has_diet": has_diet,
                    "diet_tags": diet_tags_to_include,
                    "allergy_tags": allergy_tags_to_exclude,
                    "meal_tags": [meal],
                    "dish_tags": [dish_type]
                }
                
                # Try to find a recipe for this dish type
                matched = list(database.find(query).limit(5))
                matched = [r for r in matched if r['_id'] not in used_recipe_ids]
                
                if matched:
                    # Select one recipe and add it
                    selected = random.choice(matched)
                    recommendations[meal].append(selected)
                    used_recipe_ids.add(selected['_id'])
                    found_dish_types[dish_type] = selected
                    print(f"Found a {dish_type} for {meal} with primary search")
                else:
                    # Try relaxed search
                    print(f"No {dish_type} found for {meal}, trying relaxation")
                    selected = find_with_improved_relaxation(database, search_params)
                    
                    if selected and selected['_id'] not in used_recipe_ids:
                        recommendations[meal].append(selected)
                        used_recipe_ids.add(selected['_id'])
                        found_dish_types[dish_type] = selected
                        print(f"Found a {dish_type} for {meal} with relaxation")
                    else:
                        # Try with just meal and dish tags
                        print(f"Trying simple query for {dish_type} in {meal}")
                        basic_query = {"$and": [{}, {"tags": dish_type}]} #test point here
                        basic_matched = list(database.find(basic_query).limit(5))
                        basic_matched = [r for r in basic_matched if r['_id'] not in used_recipe_ids]
                        
                        if basic_matched:
                            selected = random.choice(basic_matched)
                            recommendations[meal].append(selected)
                            used_recipe_ids.add(selected['_id'])
                            found_dish_types[dish_type] = selected
                            print(f"Found a {dish_type} for {meal} with basic query")
                        else:
                            # Try with just the dish type
                            print(f"Trying dish-only query for {dish_type}")
                            dish_query = {"tags": dish_type}
                            dish_matched = list(database.find(dish_query).limit(5))
                            dish_matched = [r for r in dish_matched if r['_id'] not in used_recipe_ids]
                            
                            if dish_matched:
                                selected = random.choice(dish_matched)
                                recommendations[meal].append(selected)
                                used_recipe_ids.add(selected['_id'])
                                found_dish_types[dish_type] = selected
                                print(f"Found a {dish_type} with dish-only query")
                            else:
                                # Try ultimate fallback - any recipe
                                print(f"No {dish_type} found even with minimal constraints. Using fallback.")
                                fallback_query = {"tags": {"$nin": allergy_tags_to_exclude}} if allergy_tags_to_exclude else {}
                                fallback_recipes = list(database.find(fallback_query).limit(5))
                                fallback_recipes = [r for r in fallback_recipes if r['_id'] not in used_recipe_ids]
                                
                                if fallback_recipes:
                                    selected = random.choice(fallback_recipes)
                                    # Add the missing tags to this recipe
                                    if dish_type not in selected.get('tags', []):
                                        selected.setdefault('tags', []).append(dish_type)
                                    if meal not in selected.get('tags', []):
                                        selected.setdefault('tags', []).append(meal)
                                    
                                    recommendations[meal].append(selected)
                                    used_recipe_ids.add(selected['_id'])
                                    found_dish_types[dish_type] = selected
                                    print(f"Using a generic recipe as {dish_type} for {meal}")
    
    # Final check - ensure we have exactly one recipe for breakfast/brunch
    # and exactly one recipe per dish type for lunch/dinner
    for meal in meal_types:
        if meal in ('breakfast', 'brunch'):
            # For breakfast/brunch, just make sure we have exactly one recipe
            if not recommendations[meal]:
                print(f"No {meal} recipes found. Using generic fallback.")
                basic_query = {"tags": meal}
                fallback_recipe = database.find_one(basic_query)
                if fallback_recipe:
                    recommendations[meal] = [fallback_recipe]
                    used_recipe_ids.add(fallback_recipe['_id'])
                else:
                    # Really desperate fallback - any recipe
                    last_resort = database.find_one({})
                    if last_resort:
                        # Make sure it has the meal tag
                        if meal not in last_resort.get('tags', []):
                            last_resort.setdefault('tags', []).append(meal)
                        recommendations[meal] = [last_resort]
                        used_recipe_ids.add(last_resort['_id'])
        else:
            # For lunch/dinner, we've already handled the finding of recipes
            # in the previous loop, so no need to add more here
            pass
    
    # Debug check to ensure we have the correct number of recommendations
    for meal, recipes in recommendations.items():
        if meal in ('breakfast', 'brunch'):
            if len(recipes) != 1:
                print(f"WARNING: Found {len(recipes)} {meal} recipes instead of 1")
        else:
            # For lunch/dinner, we should have exactly one recipe per dish type
            if len(recipes) != len(dish_types):
                print(f"WARNING: Found {len(recipes)} {meal} recipes instead of {len(dish_types)}")
    
    return recommendations


def find_with_improved_relaxation(database, params):
    """
    Improved relaxation strategy with the following order:
    1. Cuisine (least important)
    2. Calories (important for some)
    3. Time (moderately important) 
    4. Diet restrictions (most important but may need relaxation as last resort)
    
    params should contain: query, cuisine_tags, has_calorie, has_time, 
    has_diet, diet_tags, allergy_tags, meal_tags, dish_tags
    """
    print(f"Starting relaxation for {params['meal_tags']} and {params['dish_tags']}")
    
    # Create a baseline query with only meal and dish tags
    # This ensures we're starting with the right meal/dish type
    baseline_query = {"tags": {"$in": params['meal_tags'] + params['dish_tags']}}
    
    # Level 1: Drop cuisine tags
    if params['cuisine_tags']:
        # Create query without cuisine
        query_parts = []
        
        # Add diet restrictions if present
        if params['diet_tags']:
            query_parts.append({"tags": {"$all": params['diet_tags']}})
        
        # Add allergy restrictions if present  
        if params['allergy_tags']:
            query_parts.append({"tags": {"$nin": params['allergy_tags']}})
        
        # Add meal/dish tags
        query_parts.append(baseline_query)
        
        # Add time constraints if present
        if params['has_time']:
            for part in params['query'].get('$and', [params['query']]):
                if 'minutes' in part:
                    query_parts.append(part)
                    break
        
        # Add calorie constraints if present
        if params['has_calorie']:
            for part in params['query'].get('$and', [params['query']]):
                if 'nutrition.calories' in part:
                    query_parts.append(part)
                    break
        
        # Build the query
        query_no_cuisine = {"$and": query_parts} if len(query_parts) > 1 else query_parts[0]
        
        # Try the search
        result = database.find_one(query_no_cuisine)
        if result:
            print("Found recipe by relaxing cuisine")
            return result
    
    # Level 2: Drop calories as well
    if params['has_calorie']:
        query_parts = []
        
        # Add diet restrictions
        if params['diet_tags']:
            query_parts.append({"tags": {"$all": params['diet_tags']}})
            
        # Add allergy restrictions
        if params['allergy_tags']:
            query_parts.append({"tags": {"$nin": params['allergy_tags']}})
        
        # Add meal/dish tags
        query_parts.append(baseline_query)
        
        # Add time constraints
        if params['has_time']:
            for part in params['query'].get('$and', [params['query']]):
                if 'minutes' in part:
                    query_parts.append(part)
                    break
        
        query_no_calories = {"$and": query_parts} if len(query_parts) > 1 else query_parts[0]
        result = database.find_one(query_no_calories)
        if result:
            print("Found recipe by relaxing cuisine and calories")
            return result
    
    # Level 3: Drop time constraints as well
    if params['has_time']:
        query_parts = []
        
        # Add diet restrictions
        if params['diet_tags']:
            query_parts.append({"tags": {"$all": params['diet_tags']}})
            
        # Add allergy restrictions
        if params['allergy_tags']:
            query_parts.append({"tags": {"$nin": params['allergy_tags']}})
        
        # Add meal/dish tags
        query_parts.append(baseline_query)
        
        query_basic = {"$and": query_parts} if len(query_parts) > 1 else query_parts[0]
        result = database.find_one(query_basic)
        if result:
            print("Found recipe by relaxing cuisine, calories, and time")
            return result
    
    # Level 4: Relax dietary restrictions (but keep allergies)
    if params['has_diet']:
        query_parts = []
        
        # Keep allergy restrictions
        if params['allergy_tags']:
            query_parts.append({"tags": {"$nin": params['allergy_tags']}})
        
        # Add meal/dish tags
        query_parts.append(baseline_query)
        
        query_no_diet = {"$and": query_parts} if len(query_parts) > 1 else query_parts[0]
        result = database.find_one(query_no_diet)
        if result:
            print("Found recipe by relaxing all constraints except allergies")
            return result
    
    # Level 5: Last resort - just find something matching the meal and dish type
    result = database.find_one(baseline_query)
    if result:
        print("Found recipe with only meal/dish match")
        return result
        
    # If still nothing, try just the meal type
    if params['meal_tags']:
        meal_only_query = {"tags": {"$in": params['meal_tags']}}
        return database.find_one(meal_only_query)
    
    # Nothing found at all
    return None