from mongoengine import Document, StringField, IntField, EmailField, MapField, BooleanField, ReferenceField, DateField, FloatField
from datetime import datetime
from mongoengine import connect

connect('recipe', host='mongodb://localhost:27017/recipe') #name to be changed

# User information table
class UserInformation(Document):
    meta = {'collection': 'user_information'}
    username = StringField(required=True, unique=True)
    password = StringField(required=True)
    email = EmailField(required=True, unique=True)

# Cook mode table
class CookMode(Document):
    meta = {'collection': 'cook_mode'}
    easy = BooleanField(default=False)
    beginner_cook = BooleanField(default=False)

# Meal type table
class MealType(Document):
    meta = {'collection': 'meal_type'}
    main_dish = BooleanField(default=False)
    desserts = BooleanField(default=False)
    side_dishes = BooleanField(default=False)
    lunch = BooleanField(default=False)
    appetizers = BooleanField(default=False)
    soups_stews = BooleanField(default=False)
    breakfast = BooleanField(default=False)
    beverage = BooleanField(default=False)

# Allergy and preferences table
class AllergyPreferences(Document):
    meta = {'collection': 'allergy_preferences'}
    
    # Preference
    vegetarian = BooleanField(default=False)
    vegan = BooleanField(default=False)
    dietary = BooleanField(default=False)
    gluten_free = BooleanField(default=False)
    kosher = BooleanField(default=False)
    lactose = BooleanField(default=False)
    
    #Allergy
    eggs_dairy = BooleanField(default=True)
    seafood = BooleanField(default=True)
    nuts = BooleanField(default=True)

# Cuisine table
class Cuisine(Document):
    meta = {'collection': 'cuisine'}
    north_american = BooleanField(default=False)
    european = BooleanField(default=False)
    asian = BooleanField(default=False)
    italian = BooleanField(default=False)
    mexican = BooleanField(default=False)
    canadian = BooleanField(default=False)
    australian = BooleanField(default=False)
    midwestern = BooleanField(default=False)
    african = BooleanField(default=False)
    indian = BooleanField(default=False)
    greek = BooleanField(default=False)
    french = BooleanField(default=False)
    middle_eastern = BooleanField(default=False)
    chinese = BooleanField(default=False)

# Requirements table
class Requirements(Document):
    meta = {'collection': 'requirements'}
    
    max_time = IntField(min_value=0)  # in minutes
    max_calories = IntField(min_value=0)
    
    '''min_protein = IntField(min_value=0)
    max_carbs = IntField(min_value=0)
    max_fat = IntField(min_value=0)'''
    
    # References to filtering categories
    cook_mode = ReferenceField(CookMode)
    meal_type = ReferenceField(MealType)
    allergy_preferences = ReferenceField(AllergyPreferences)
    cuisine = ReferenceField(Cuisine)
    
    # User reference
    user = ReferenceField(UserInformation, required=True)

# Recipe table
class Recipe(Document):
    meta = {'collection': 'recipes'}
    
    name = StringField(required=True)
    time = IntField(min_value=0)  # in minutes
    description = StringField()
    tags = ListField(StringField())
    nutrition = ListField(StringField()) # can be change to detail
    n_steps = IntField(min_value=0)
    steps = ListField(StringField())
    ingredients = ListField(StringField())
    
    
    #requirement part
    '''
    requirement = ReferenceField(Requirement)
    cook_mode = ReferenceField(CookMode)
    meal_type = ReferenceField(MealType)
    allergy_preferences = ReferenceField(AllergyPreferences)
    cuisine = ReferenceField(Cuisine)
    '''
    
    # Metadata
    user = ReferenceField(UserInformation, required=True)
    
    
    timestamp = DateField(default=datetime.now)
