from mongoengine import Document, StringField, IntField, EmailField, MapField, BooleanField, ReferenceField, DateField, FloatField
from datetime import datetime
from mongoengine import connect

connect('recipe', host='mongodb://localhost:27017/recipe') #name to be changed

#user-information table
class UserInformation(Document):
    meta = {'collection': 'user_information'}
    username = StringField(required=True, unique=True)
    password = StringField(required=True)
    email = EmailField(required=True, unique=True)


# meal-type table
class MealType(Document):
    meta = {'collection': 'meal_type'}
    
    desserts = BooleanField(default=False)
    drinks = BooleanField(default=False)
    side = BooleanField(default=False)
    soup = BooleanField(default=False)
    cuisine = BooleanField(default=False)
    bread = BooleanField(default=False)
    main = BooleanField(default=False)

# recipe table
class Recipe(Document):
    meta = {'collection': 'recipes'}

    total_time = IntField(required=True, min_value=0)  # in minutes
    ingredients = MapField(field=StringField())        # key-value ingredient names
    nutrition = IntField(min_value=0, max_value=20000)  # calories or another measure

    meal_type = ReferenceField(MealType, required=True)
    user = ReferenceField(UserInformation, required=True)
