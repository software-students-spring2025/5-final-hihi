# 2. Build base query
    query = {}

    # Strict handling of diet tags - they must be present
    if diet_tags_to_include:
        query = add_tags_to_query(query, diet_tags_to_include, mode='$all')

    # Strict handling of allergy exclusions
    if allergy_tags_to_exclude:
        allergy_condition = {'$nin': allergy_tags_to_exclude}
        if 'tags' in query:
            query = {
                '$and': [
                    {'tags': query['tags']},
                    {'tags': allergy_condition}
                ]
            }
        else:
            query['tags'] = allergy_condition

    # Time constraint handling
    if time_option != 6:
        time_limits = {
            1: 30, 2: 60, 3: 90, 4: 120, 5: float('inf')
        }
        max_minutes = time_limits[time_option]
        if time_option == 5:
            query['minutes'] = {'$gt': 120}
        else:
            # For option 2 (30-60 minutes), set both min and max
            if time_option == 2:
                query['minutes'] = {'$gte': 30, '$lte': 60}
            else:
                query['minutes'] = {'$lte': max_minutes}
                
    # Debug the base query
    print(f"Base query: {query}")

    # 3. Setup recommendations container
    recommendations = {meal: [] for meal in meal_types}
    used_recipe_ids = set()

    # 4. Handle calories
    meal_calorie_ranges = {}
    if calorie_option != 7:
        calorie_ranges = {
            1: (1200, 1400), 2: (1400, 1600), 3: (1600, 1800),
            4: (1800, 2200), 5: (2200, 2500), 6: (2500, 3000)
        }
        daily_min_calories, daily_max_calories = calorie_ranges[calorie_option]

        
        # Calculate total weights across all selected meal types
        total_min_weight = sum(meal_weights.get(m, (1.0, 1.0))[0] for m in meal_types)
        total_max_weight = sum(meal_weights.get(m, (1.0, 1.0))[1] for m in meal_types)

        # Distribute calories across meal types
        for meal in meal_types:
            min_weight, max_weight = meal_weights.get(meal, (1.0, 1.0))
            min_meal_calories = int(daily_min_calories * (min_weight / total_max_weight))
            max_meal_calories = int(daily_max_calories * (max_weight / total_min_weight))
            meal_calorie_ranges[meal] = (min_meal_calories, max_meal_calories)

    # 5. Calculate dish type calorie ranges for each meal
    dish_calorie_ranges = {}
    for meal in meal_types:
        if meal in meal_calorie_ranges:
            min_meal_cal, max_meal_cal = meal_calorie_ranges[meal]
            
            # Calculate total weight for selected dish types
            meal_dish_types = dish_types
            total_dish_weight = sum(dish_weights.get(dish, 1.0) for dish in meal_dish_types)
            
            # Distribute calories across dish types
            dish_calorie_ranges[meal] = {}
            for dish in meal_dish_types:
                dish_weight = dish_weights.get(dish, 1.0)
                min_dish_calories = int(min_meal_cal * (dish_weight / total_dish_weight))
                max_dish_calories = int(max_meal_cal * (dish_weight / total_dish_weight))
                dish_calorie_ranges[meal][dish] = (min_dish_calories, max_dish_calories)

    # 6. Query recipes for each meal
    for meal in meal_types:
        if meal in ['breakfast', 'brunch']:
            # Special case: only 1 random recipe
            meal_query = copy.deepcopy(query)
            meal_query = add_tags_to_query(meal_query, [meal], mode='$in')

            if is_beginner:
                meal_query = add_tags_to_query(meal_query, ['easy', 'beginner-cook'], mode='$in')
            if cuisine_tags:
                meal_query = add_tags_to_query(meal_query, cuisine_tags, mode='$in')

            matched_recipes = database.find(meal_query)

            if calorie_option != 7 and meal in meal_calorie_ranges:
                min_cal, max_cal = meal_calorie_ranges[meal]
                matched_recipes = [r for r in matched_recipes if min_cal <= r.get('calories', 0) <= max_cal]

            matched_recipes = [r for r in matched_recipes if r['_id'] not in used_recipe_ids]
            
            if matched_recipes:
                selected_recipes = random.sample(matched_recipes, min(1, len(matched_recipes)))
                
                for recipe in selected_recipes:
                    recommendations[meal].append(recipe)
                    used_recipe_ids.add(recipe['_id'])
            elif diet_tags_to_include or allergy_tags_to_exclude:
                # Try with relaxed constraints if no matches found
                relaxed_recipe = find_with_relaxed_constraints(
                    query, database, diet_tags_to_include, allergy_tags_to_exclude
                )
                if relaxed_recipe and relaxed_recipe['_id'] not in used_recipe_ids:
                    recommendations[meal].append(relaxed_recipe)
                    used_recipe_ids.add(relaxed_recipe['_id'])

        else:  # Lunch and Dinner
            # For each dish type, select a recipe
            for dish_type in dish_types:
                dish_query = copy.deepcopy(query)
                dish_query = add_tags_to_query(dish_query, [meal], mode='$in')
                dish_query = add_tags_to_query(dish_query, [dish_type], mode='$in')

                if is_beginner:
                    dish_query = add_tags_to_query(dish_query, ['easy', 'beginner-cook'], mode='$in')
                
                # Ensure cuisine preferences are strictly enforced
                if cuisine_tags:
                    dish_query = add_tags_to_query(dish_query, cuisine_tags, mode='$in')
                
                # Print the query for debugging
                print(f"Query for {meal} {dish_type}: {dish_query}")

                matched_recipes = database.find(dish_query)
                
                # Debug the matched recipes
                print(f"Found {len(list(matched_recipes))} recipes for {meal} {dish_type}")
                
                # Re-run the query since the cursor might be exhausted
                matched_recipes = database.find(dish_query)

                # Apply dish-specific calorie range if available
                filtered_recipes = []
                for recipe in matched_recipes:
                    # Debug each recipe
                    print(f"Checking recipe: {recipe.get('name')}, Tags: {recipe.get('tags')}")
                    
                    # Verify vegetarian constraint explicitly
                    if 'vegetarian' in diet_tags_to_include and 'vegetarian' not in recipe.get('tags', []):
                        print(f"Rejecting non-vegetarian recipe: {recipe.get('name')}")
                        continue
                        
                    # Verify cuisine constraint explicitly
                    if cuisine_tags and not any(tag in recipe.get('tags', []) for tag in cuisine_tags):
                        print(f"Rejecting non-matching cuisine: {recipe.get('name')}")
                        continue
                    
                    # Check calories if needed
                    if (calorie_option != 7 and meal in dish_calorie_ranges 
                            and dish_type in dish_calorie_ranges[meal]):
                        min_cal, max_cal = dish_calorie_ranges[meal][dish_type]
                        if not (min_cal <= recipe.get('calories', 0) <= max_cal):
                            print(f"Rejecting due to calories: {recipe.get('name')}")
                            continue
                            
                    # Check if recipe already used
                    if recipe['_id'] in used_recipe_ids:
                        print(f"Rejecting already used recipe: {recipe.get('name')}")
                        continue
                        
                    filtered_recipes.append(recipe)
                
                print(f"After filtering, {len(filtered_recipes)} recipes remain")
                
                if filtered_recipes:
                    selected_recipes = random.sample(filtered_recipes, min(1, len(filtered_recipes)))
                    
                    for recipe in selected_recipes:
                        recommendations[meal].append(recipe)
                        used_recipe_ids.add(recipe['_id'])
                        print(f"Selected for {meal} {dish_type}: {recipe.get('name')}")
                elif diet_tags_to_include or allergy_tags_to_exclude:
                    print(f"No recipes found, trying relaxed constraints for {meal} {dish_type}")
                    # Try with relaxed constraints if no matches found
                    relaxed_recipe = find_with_relaxed_constraints(
                        query, database, diet_tags_to_include, allergy_tags_to_exclude, dish_type, cuisine_tags
                    )
                    if relaxed_recipe and relaxed_recipe['_id'] not in used_recipe_ids:
                        # Additional verification for strict constraints
                        is_valid = True
                        
                        # Verify vegetarian constraint explicitly
                        if 'vegetarian' in diet_tags_to_include and 'vegetarian' not in relaxed_recipe.get('tags', []):
                            is_valid = False
                            
                        # Verify cuisine constraint explicitly
                        if cuisine_tags and not any(tag in relaxed_recipe.get('tags', []) for tag in cuisine_tags):
                            is_valid = False
                            
                        if is_valid:
                            recommendations[meal].append(relaxed_recipe)
                            used_recipe_ids.add(relaxed_recipe['_id'])
                            print(f"Selected relaxed recipe for {meal} {dish_type}: {relaxed_recipe.get('name')}")
                        else:
                            print(f"Relaxed recipe doesn't meet strict constraints: {relaxed_recipe.get('name')}")

    return recommendations


def find_with_relaxed_constraints(original_query, database, diet_tags, allergy_tags, dish_type=None, cuisine_tags=None):
    """Find a recipe with relaxed constraints while maintaining dietary requirements"""
    # Start with dietary restrictions only (highest priority)
    relaxed_query = {}
    
    print(f"Finding with relaxed constraints. Diet: {diet_tags}, Allergies: {allergy_tags}, Dish: {dish_type}")
    
    # Always keep dietary requirements
    if diet_tags:
        relaxed_query['tags'] = {'$all': list(diet_tags)}
    
    # Always maintain allergy exclusions
    if allergy_tags:
        if 'tags' in relaxed_query:
            relaxed_query = {
                '$and': [
                    {'tags': relaxed_query['tags']},
                    {'tags': {'$nin': list(allergy_tags)}}
                ]
            }
        else:
            relaxed_query['tags'] = {'$nin': list(allergy_tags)}
    
    # Add dish type if specified (but as a lower priority)
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
    
    # For cuisine constraints, we should preserve them for vegetarian search
    if cuisine_tags and 'vegetarian' in diet_tags:
        if 'tags' not in relaxed_query:
            relaxed_query['tags'] = {'$in': cuisine_tags}
        elif '$all' in relaxed_query['tags']:
            temp_query = {'$all': relaxed_query['tags']['$all']}
            relaxed_query = {
                '$and': [
                    {'tags': temp_query},
                    {'tags': {'$in': cuisine_tags}}
                ]
            }
        elif '$nin' in relaxed_query['tags']:
            relaxed_query = {
                '$and': [
                    {'tags': relaxed_query['tags']},
                    {'tags': {'$in': cuisine_tags}}
                ]
            }
        elif '$and' in relaxed_query:
            relaxed_query['$and'].append({'tags': {'$in': cuisine_tags}})
    
    print(f"Relaxed query: {relaxed_query}")
    
    # Try to find a matching recipe
    recipe = database.find_one(relaxed_query)
    
    # If still nothing found, try even more relaxed constraints
    if not recipe and dish_type:
        print("No recipe found with dish type, trying without")
        # Try without dish type constraint but keep dietary requirements
        less_relaxed_query = {}
        if diet_tags:
            less_relaxed_query['tags'] = {'$all': list(diet_tags)}
        
        if allergy_tags:
            if 'tags' in less_relaxed_query:
                less_relaxed_query = {
                    '$and': [
                        {'tags': less_relaxed_query['tags']},
                        {'tags': {'$nin': list(allergy_tags)}}
                    ]
                }
            else:
                less_relaxed_query['tags'] = {'$nin': list(allergy_tags)}
        
        # Keep cuisine for vegetarians
        if cuisine_tags and 'vegetarian' in diet_tags:
            if 'tags' not in less_relaxed_query:
                less_relaxed_query['tags'] = {'$in': cuisine_tags}
            elif '$all' in less_relaxed_query['tags']:
                temp_query = {'$all': less_relaxed_query['tags']['$all']}
                less_relaxed_query = {
                    '$and': [
                        {'tags': temp_query},
                        {'tags': {'$in': cuisine_tags}}
                    ]
                }
            elif '$nin' in less_relaxed_query['tags']:
                less_relaxed_query = {
                    '$and': [
                        {'tags': less_relaxed_query['tags']},
                        {'tags': {'$in': cuisine_tags}}
                    ]
                }
            elif '$and' in less_relaxed_query:
                less_relaxed_query['$and'].append({'tags': {'$in': cuisine_tags}})
        
        print(f"More relaxed query: {less_relaxed_query}")
        recipe = database.find_one(less_relaxed_query)
    
    if recipe:
        print(f"Found relaxed recipe: {recipe.get('name')}, Tags: {recipe.get('tags')}")
    else:
        print("No recipe found with relaxed constraints")
        
    return recipe