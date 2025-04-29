import pytest
import mongomock
from mongoengine import connect, disconnect, get_connection
from web_app.back_end.model import (
    UserInformation, CookMode, MealType, AllergyPreferences,
    Cuisine, DailyPlan, Requirements, Recipe, RecipeHistory
)

@pytest.fixture(autouse=True)
def mock_db():
    connect(
        db="testdb",
        alias="default",
        host="mongodb://localhost",  # dummy URI
        mongo_client_class=mongomock.MongoClient
    )
    yield
    disconnect(alias="default")

def test_create_user():
    user = UserInformation(username="testuser", password="pass", email="test@example.com")
    user.save()
    assert UserInformation.objects(username="testuser").first() is not None

def test_create_cook_mode():
    cm = CookMode(easy=True)
    cm.save()
    assert CookMode.objects(easy=True).first() is not None

def test_create_meal_type():
    meal = MealType(main_dish=True, desserts=True)
    meal.save()
    assert MealType.objects(main_dish=True).first() is not None

def test_create_allergy_preferences():
    allergy = AllergyPreferences(vegetarian=True, nuts=False)
    allergy.save()
    assert AllergyPreferences.objects(vegetarian=True).first() is not None

def test_create_cuisine():
    cuisine = Cuisine(italian=True, chinese=True)
    cuisine.save()
    assert Cuisine.objects(italian=True).first() is not None

def test_create_daily_plan():
    plan = DailyPlan(breakfast=True)
    plan.save()
    assert DailyPlan.objects(breakfast=True).first() is not None

def test_create_requirements():
    user = UserInformation(username="u1", password="p1", email="u1@test.com").save()
    plan = DailyPlan(breakfast=True).save()
    meal = MealType(main_dish=True).save()
    allergy = AllergyPreferences(vegan=True).save()
    cuisine = Cuisine(indian=True).save()
    cm = CookMode(easy=True).save()
    r = Requirements(
        time_interval=2, calory_interval=3,
        cook_mode=cm, daily_plan=plan, meal_type=meal,
        allergy_preferences=allergy, cuisine=cuisine,
        user=user
    )
    r.save()
    assert Requirements.objects(user=user).first() is not None

def test_create_recipe():
    user = UserInformation(username="u2", password="p2", email="u2@test.com").save()
    recipe = Recipe(
        type="lunch", name="Ramen", time=30,
        tags=["japanese", "main-dish"], nutrition=["calories: 500"],
        n_steps=2, steps=["Boil water", "Add noodles"],
        ingredients=["water", "noodles"], user=user
    )
    recipe.save()
    assert Recipe.objects(name="Ramen").first() is not None

def test_create_recipe_history():
    user = UserInformation(username="u3", password="p3", email="u3@test.com").save()
    recipe = Recipe(type="dinner", name="Curry", time=45, user=user).save()
    history = RecipeHistory(user=user, recipe=recipe)
    history.save()
    assert RecipeHistory.objects(user=user).first() is not None
