"""
Mock MongoDB Class for Local Testing

This provides a fake implementation of the MongoDB connection
for testing without requiring an actual MongoDB connection.
"""

import json
import random
from datetime import datetime

class MockMongoDB:
    """Mock implementation of MongoDB connection for testing"""
    
    def __init__(self):
        self.connected = False
        self.sample_recipes = []
        self._create_sample_recipes()
    
    def connect(self):
        """Simulate connecting to MongoDB"""
        print("Connecting to mock MongoDB database...")
        self.connected = True
        print(f"Successfully connected to mock MongoDB")
        print(f"Found {len(self.sample_recipes)} recipes in the collection")
        return True
    
    def disconnect(self):
        """Simulate disconnecting from MongoDB"""
        self.connected = False
        print("Disconnected from mock MongoDB")
    
    def find_recipe_by_id(self, recipe_id):
        """Find recipe by ID in the mock database"""
        for recipe in self.sample_recipes:
            if str(recipe['_id']) == str(recipe_id):
                return recipe
        return None
    
    def find_recipes(self, query=None, limit=10):
        """Find recipes matching the query in the mock database"""
        if not self.connected:
            print("Not connected to mock database")
            return []
        
        if query is None:
            query = {}
        
        print(f"Executing query: {json.dumps(query, default=str)}")
        
        # Apply filters based on the query
        filtered_recipes = self._filter_recipes(query)
        
        # Limit results
        limited_results = filtered_recipes[:limit]
        
        print(f"Found {len(limited_results)} matching recipes")
        return limited_results
    
    def find_recipes_by_tags(self, tags, match_all=True, limit=10):
        """Find recipes with the specified tags in the mock database"""
        if match_all:
            query = {"tags": {"$all": tags}}
        else:
            query = {"tags": {"$in": tags}}
        
        return self.find_recipes(query, limit)
    
    def find_recipes_by_diet(self, diet, limit=10):
        """Find recipes matching dietary restriction in the mock database"""
        return self.find_recipes_by_tags([diet], True, limit)
    
    def find_recipes_by_cuisine(self, cuisine, limit=10):
        """Find recipes matching cuisine in the mock database"""
        return self.find_recipes_by_tags([cuisine], True, limit)
    
    def find_recipes_by_ingredients(self, ingredients, match_all=True, limit=10):
        """Find recipes with specified ingredients in the mock database"""
        if match_all:
            query = {"ingredients": {"$all": ingredients}}
        else:
            query = {"ingredients": {"$in": ingredients}}
        
        return self.find_recipes(query, limit)
    
    def find_recipes_by_time(self, max_minutes, limit=10):
        """Find recipes that take at most max_minutes to prepare in the mock database"""
        query = {"minutes": {"$lte": max_minutes}}
        return self.find_recipes(query, limit)
    
    def find_recipes_by_nutrition(self, nutrient, min_val=None, max_val=None, limit=10):
        """Find recipes by nutritional content in the mock database"""
        query = {}
        
        # Build query based on min/max values
        if min_val is not None and max_val is not None:
            query[f"nutrition.{nutrient}"] = {"$gte": min_val, "$lte": max_val}
        elif min_val is not None:
            query[f"nutrition.{nutrient}"] = {"$gte": min_val}
        elif max_val is not None:
            query[f"nutrition.{nutrient}"] = {"$lte": max_val}
        else:
            return []
        
        return self.find_recipes(query, limit)
    
    def find_recipes_with_relaxed_constraints(self, original_query, diet_allergies, 
                                            dish_tag=None, meal_type=None, 
                                            strict_cuisine=False, limit=1,
                                            exclude_ids=None):
        """Find recipes with relaxed constraints for testing"""
        # For mock purposes, simply return some recipes that match basic criteria
        relaxed_query = {}
        
        # Maintain any dietary restrictions
        if 'tags' in original_query and '$all' in original_query['tags']:
            diet_tags = [tag for tag in original_query['tags']['$all'] 
                       if tag in ['vegetarian', 'vegan', 'gluten-free']]
            if diet_tags:
                relaxed_query['tags'] = {'$all': diet_tags}
        
        # Try to include dish type or meal type if specified
        tag_list = []
        if dish_tag:
            tag_list.append(dish_tag)
        if meal_type:
            tag_list.append(meal_type)
        
        if tag_list:
            if 'tags' in relaxed_query:
                if '$in' not in relaxed_query['tags']:
                    relaxed_query['tags']['$in'] = []
                relaxed_query['tags']['$in'].extend(tag_list)
            else:
                relaxed_query['tags'] = {'$in': tag_list}
        
        # Exclude already recommended recipes
        if exclude_ids:
            relaxed_query['_id'] = {'$nin': list(exclude_ids)}
        
        return self.find_recipes(relaxed_query, limit)
    
    # Private helper methods
    def _create_sample_recipes(self):
        """Create sample recipes for testing"""
        # Generate a few sample recipes
        recipe_templates = [
            {
                "name": "Vegan Asian Breakfast Bowl",
                "minutes": 25,
                "tags": ["breakfast", "brunch", "asian", "vegan", "beginner-cook", "easy"],
                "nutrition": {"calories": 350, "protein": 12, "carbs": 45, "fat": 14},
                "steps": [
                    "Cook rice according to package instructions.",
                    "Stir-fry vegetables in sesame oil.",
                    "Add tofu and season with soy sauce.",
                    "Serve topped with green onions and sesame seeds."
                ],
                "description": "A nutritious vegan breakfast bowl with Asian flavors, perfect for beginners.",
                "ingredients": ["rice", "tofu", "bell peppers", "broccoli", "sesame oil", "soy sauce"]
            },
            {
                "name": "Vegan Miso Soup",
                "minutes": 35,
                "tags": ["soup", "lunch", "asian", "vegan", "beginner-cook", "easy"],
                "nutrition": {"calories": 220, "protein": 8, "carbs": 25, "fat": 10},
                "steps": [
                    "Bring water to boil and add miso paste.",
                    "Add diced tofu and seaweed.",
                    "Simmer for 10 minutes.",
                    "Garnish with green onions."
                ],
                "description": "A comforting vegan miso soup that's perfect for lunch.",
                "ingredients": ["miso paste", "tofu", "seaweed", "green onions", "water"]
            },
            {
                "name": "Vegan Mango Sticky Rice",
                "minutes": 45,
                "tags": ["dessert", "lunch", "asian", "vegan", "easy"],
                "nutrition": {"calories": 380, "protein": 5, "carbs": 70, "fat": 8},
                "steps": [
                    "Cook sticky rice according to package instructions.",
                    "Mix coconut milk with sugar and salt, heat until dissolved.",
                    "Pour over cooked sticky rice and let sit for 30 minutes.",
                    "Serve with sliced fresh mango."
                ],
                "description": "A traditional Thai dessert made vegan-friendly with coconut milk.",
                "ingredients": ["sticky rice", "coconut milk", "sugar", "salt", "mangoes"]
            },
            {
                "name": "Vegan Asian Stir-Fry",
                "minutes": 30,
                "tags": ["main-dish", "lunch", "dinner", "asian", "vegan", "beginner-cook"],
                "nutrition": {"calories": 420, "protein": 15, "carbs": 55, "fat": 16},
                "steps": [
                    "Cook rice or noodles according to package instructions.",
                    "Stir-fry vegetables in oil until tender-crisp.",
                    "Add tofu and sauce mixture (soy sauce, rice vinegar, ginger, garlic).",
                    "Cook until sauce thickens and serve over rice/noodles."
                ],
                "description": "A quick and nutritious vegan stir-fry with Asian flavors.",
                "ingredients": ["rice", "tofu", "mixed vegetables", "soy sauce", "rice vinegar", "ginger", "garlic"]
            }
        ]
        
        # Create sample recipes with IDs
        for i, template in enumerate(recipe_templates):
            recipe = template.copy()
            recipe["_id"] = f"sample_recipe_{i+1}"
            
            # Convert nutrition to array format for some recipes to test both formats
            if i % 2 == 0:
                nutrition_values = [
                    recipe["nutrition"]["calories"],
                    recipe["nutrition"]["fat"],
                    recipe["nutrition"]["protein"],
                    recipe["nutrition"]["carbs"]
                ]
                recipe["nutrition"] = nutrition_values
            
            self.sample_recipes.append(recipe)
    
    def _filter_recipes(self, query):
        """Filter recipes based on the query criteria"""
        # This is a simplified implementation that handles basic query operations
        filtered = []
        
        for recipe in self.sample_recipes:
            if self._matches_query(recipe, query):
                filtered.append(recipe)
        
        return filtered
    
    def _matches_query(self, recipe, query):
        """Check if a recipe matches the query criteria"""
        for field, condition in query.items():
            # Handle special case for _id
            if field == '_id':
                if isinstance(condition, dict) and '$nin' in condition:
                    if str(recipe['_id']) in [str(id_val) for id_val in condition['$nin']]:
                        return False
                elif str(recipe['_id']) != str(condition):
                    return False
                continue
            
            # Handle nested fields (e.g., 'nutrition.calories')
            if '.' in field:
                main_field, sub_field = field.split('.')
                if main_field not in recipe:
                    return False
                
                # Handle array-based nutrition
                if main_field == 'nutrition' and isinstance(recipe[main_field], list):
                    # Map common nutrition fields to array indices
                    nutrition_indices = {'0': 0, 'calories': 0, 'fat': 1, 'protein': 2, 'carbs': 3}
                    idx = nutrition_indices.get(sub_field, -1)
                    if idx == -1 or idx >= len(recipe[main_field]):
                        return False
                    
                    value = recipe[main_field][idx]
                else:
                    # Handle dict-based nutrition
                    if sub_field not in recipe[main_field]:
                        return False
                    value = recipe[main_field][sub_field]
                
                if not self._check_condition(value, condition):
                    return False
                continue
            
            # Handle regular fields
            if field not in recipe:
                return False
            
            if field == 'tags':
                # Handle tag matching
                if isinstance(condition, dict):
                    if '$all' in condition:
                        if not all(tag in recipe['tags'] for tag in condition['$all']):
                            return False
                    elif '$in' in condition:
                        if not any(tag in recipe['tags'] for tag in condition['$in']):
                            return False
                elif recipe['tags'] != condition:
                    return False
            elif field == 'minutes':
                # Handle minutes comparison
                if isinstance(condition, dict):
                    if '$lte' in condition and recipe['minutes'] > condition['$lte']:
                        return False
                    if '$gte' in condition and recipe['minutes'] < condition['$gte']:
                        return False
                elif recipe['minutes'] != condition:
                    return False
            else:
                # Handle other field comparisons
                if not self._check_condition(recipe[field], condition):
                    return False
        
        return True
    
    def _check_condition(self, value, condition):
        """Check if a value matches a condition"""
        if isinstance(condition, dict):
            if '$lte' in condition and value > condition['$lte']:
                return False
            if '$gte' in condition and value < condition['$gte']:
                return False
            if '$in' in condition and value not in condition['$in']:
                return False
            if '$all' in condition and not all(item in value for item in condition['$all']):
                return False
        elif value != condition:
            return False
        
        return True