import sys
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-02-6bb634618822"

RECIPES = [
    {
        "id": "mediterranean-chickpea-salad",
        "title": "Mediterranean Chickpea Salad",
        "category": "Lunch",
        "prep_time_mins": 15,
        "calories": 350,
        "ingredients": ["chickpeas", "cucumber", "cherry tomatoes", "feta cheese", "olive oil", "lemon juice"],
        "instructions": "Combine diced cucumber, cherry tomatoes, and rinsed chickpeas in a bowl. Toss with olive oil and lemon juice, then top with crumbled feta.",
        "dietary_tags": ["vegetarian", "gluten-free"],
    },
    {
        "id": "creamy-coconut-lentil-curry",
        "title": "Creamy Coconut Lentil Curry",
        "category": "Dinner",
        "prep_time_mins": 30,
        "calories": 480,
        "ingredients": ["red lentils", "coconut milk", "spinach", "garlic", "ginger", "curry powder", "diced tomatoes"],
        "instructions": "Sauté garlic and ginger. Add curry powder, lentils, diced tomatoes, and coconut milk. Simmer for 20 minutes, then stir in spinach.",
        "dietary_tags": ["vegan", "gluten-free", "dairy-free"],
    },
    {
        "id": "berry-avocado-smoothie-bowl",
        "title": "Berry Avocado Smoothie Bowl",
        "category": "Breakfast",
        "prep_time_mins": 10,
        "calories": 290,
        "ingredients": ["frozen berries", "avocado", "almond milk", "chia seeds", "granola"],
        "instructions": "Blend frozen berries, half an avocado, and almond milk until smooth and thick. Top with chia seeds and granola.",
        "dietary_tags": ["vegan", "dairy-free"],
    },
]

PANTRY = [
    {
        "id": "chickpeas",
        "name": "Chickpeas (Canned)",
        "quantity": 2.0,
        "unit": "cans",
        "category": "canned",
    },
    {
        "id": "coconut-milk",
        "name": "Coconut Milk",
        "quantity": 3.0,
        "unit": "cans",
        "category": "canned",
    },
    {
        "id": "red-lentils",
        "name": "Red Lentils",
        "quantity": 500.0,
        "unit": "grams",
        "category": "dry goods",
    },
    {
        "id": "olive-oil",
        "name": "Extra Virgin Olive Oil",
        "quantity": 1.0,
        "unit": "bottle",
        "category": "pantry",
    },
]


def seed_database():
    print(f"Connecting to Firestore for project '{PROJECT_ID}'...")
    db = firestore.Client(project=PROJECT_ID)

    print("Seeding 'recipes' collection...")
    for recipe in RECIPES:
        doc_ref = db.collection("recipes").document(recipe["id"])
        doc_ref.set(recipe)
        print(f"  ✓ Added recipe: {recipe['title']}")

    print("Seeding 'pantry' collection...")
    for item in PANTRY:
        doc_ref = db.collection("pantry").document(item["id"])
        doc_ref.set(item)
        print(f"  ✓ Added pantry item: {item['name']}")

    print("Firestore database seeded successfully!")


if __name__ == "__main__":
    seed_database()
