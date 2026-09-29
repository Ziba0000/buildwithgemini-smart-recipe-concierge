"""Firestore database tools for Smart Recipe & Pantry Concierge."""

import os
from typing import Any, Optional
from google.cloud import firestore

# Hardcode project ID as requested to prevent project number resolution issues on Agent Platform
PROJECT_ID = "qwiklabs-gcp-02-6bb634618822"

# Support local sa-key.json if present
if os.path.exists("sa-key.json") and "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "sa-key.json"


def _get_db_client() -> firestore.Client:
    """Returns a Firestore client instance configured with the hardcoded project ID."""
    return firestore.Client(project=PROJECT_ID)


def search_recipes(category: Optional[str] = None, ingredient: Optional[str] = None) -> list[dict[str, Any]]:
    """Search for recipes in the database by category or ingredient.

    Args:
        category: Optional category filter (e.g., 'Breakfast', 'Lunch', 'Dinner').
        ingredient: Optional ingredient filter (e.g., 'chickpeas', 'spinach').

    Returns:
        A list of matching recipe documents.
    """
    db = _get_db_client()
    recipes_ref = db.collection("recipes")
    docs = recipes_ref.stream()

    results = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id

        # Category filter
        if category and category.lower() not in data.get("category", "").lower():
            continue

        # Ingredient filter
        if ingredient:
            ing_list = [i.lower() for i in data.get("ingredients", [])]
            if not any(ingredient.lower() in ing for ing in ing_list):
                continue

        results.append(data)

    return results


def get_recipe_details(recipe_id: str) -> dict[str, Any]:
    """Get full details, ingredients, and instructions for a specific recipe.

    Args:
        recipe_id: The unique ID of the recipe document.

    Returns:
        A dictionary with the recipe details, or an error message if not found.
    """
    db = _get_db_client()
    doc_ref = db.collection("recipes").document(recipe_id)
    doc = doc_ref.get()

    if not doc.exists:
        return {"error": f"Recipe with ID '{recipe_id}' not found."}

    data = doc.to_dict()
    data["id"] = doc.id
    return data


def add_recipe(
    title: str,
    category: str,
    prep_time_mins: int,
    calories: int,
    ingredients: list[str],
    instructions: str,
    dietary_tags: list[str],
) -> str:
    """Add a new recipe to the recipe database.

    Args:
        title: The title of the recipe.
        category: The category (e.g., 'Breakfast', 'Lunch', 'Dinner', 'Snack').
        prep_time_mins: Preparation time in minutes.
        calories: Total calorie count per serving.
        ingredients: List of ingredient strings.
        instructions: Preparation instructions.
        dietary_tags: List of tags like 'vegan', 'gluten-free', 'vegetarian'.

    Returns:
        A confirmation message with the generated recipe ID.
    """
    db = _get_db_client()
    doc_id = title.lower().replace(" ", "-").replace("&", "and")
    doc_ref = db.collection("recipes").document(doc_id)

    recipe_data = {
        "id": doc_id,
        "title": title,
        "category": category,
        "prep_time_mins": prep_time_mins,
        "calories": calories,
        "ingredients": ingredients,
        "instructions": instructions,
        "dietary_tags": dietary_tags,
    }

    doc_ref.set(recipe_data)
    return f"Successfully added recipe '{title}' with ID '{doc_id}'."


def get_pantry_items() -> list[dict[str, Any]]:
    """Retrieve all items currently stored in the user's pantry inventory.

    Returns:
        A list of pantry item documents with quantities and units.
    """
    db = _get_db_client()
    docs = db.collection("pantry").stream()

    items = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        items.append(data)

    return items


def update_pantry_item(name: str, quantity: float, unit: str, category: str = "pantry") -> str:
    """Add or update an ingredient item in the pantry inventory.

    Args:
        name: Name of the ingredient/item.
        quantity: Current quantity available.
        unit: Unit of measurement (e.g., 'cans', 'grams', 'items', 'cups').
        category: Category of item (e.g., 'canned', 'dry goods', 'produce', 'spices').

    Returns:
        A confirmation message detailing the update.
    """
    db = _get_db_client()
    doc_id = name.lower().replace(" ", "-")
    doc_ref = db.collection("pantry").document(doc_id)

    item_data = {
        "id": doc_id,
        "name": name,
        "quantity": float(quantity),
        "unit": unit,
        "category": category,
    }

    doc_ref.set(item_data)
    return f"Updated pantry item '{name}': {quantity} {unit}."


def generate_shopping_list(recipe_id: str) -> dict[str, Any]:
    """Generate a shopping list of missing ingredients needed for a specific recipe by checking pantry inventory.

    Args:
        recipe_id: The unique ID of the target recipe.

    Returns:
        A summary dictionary containing available pantry ingredients and missing ingredients to buy.
    """
    recipe = get_recipe_details(recipe_id)
    if "error" in recipe:
        return recipe

    pantry_items = get_pantry_items()
    pantry_names = [item["name"].lower() for item in pantry_items]
    pantry_ids = [item["id"].lower() for item in pantry_items]

    required_ingredients = recipe.get("ingredients", [])
    in_pantry = []
    missing = []

    for ing in required_ingredients:
        ing_lower = ing.lower()
        if any(p_name in ing_lower or ing_lower in p_name for p_name in pantry_names) or any(
            p_id in ing_lower for p_id in pantry_ids
        ):
            in_pantry.append(ing)
        else:
            missing.append(ing)

    return {
        "recipe_title": recipe.get("title", recipe_id),
        "in_pantry": in_pantry,
        "missing_ingredients_to_buy": missing,
    }
