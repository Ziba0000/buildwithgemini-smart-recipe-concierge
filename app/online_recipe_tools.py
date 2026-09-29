"""External API tools for Smart Recipe & Pantry Concierge."""

import json
import os
import urllib.parse
import urllib.request
from typing import Any


def search_online_recipes(query: str) -> list[dict[str, Any]]:
    """Search live online recipe database (TheMealDB) by query string (e.g., 'chicken', 'pasta', 'curry').

    Args:
        query: Recipe search term or dish name.

    Returns:
        A list of online recipe details including title, category, cuisine area, instructions, ingredients, and thumbnail URL.
    """
    api_key = os.getenv("THEMEALDB_API_KEY", "1")
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.themealdb.com/api/json/v1/{api_key}/search.php?s={encoded_query}"

    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            meals = data.get("meals") or []
    except Exception as e:
        return [{"error": f"Failed to fetch online recipes: {str(e)}"}]

    results = []
    for meal in meals[:5]:  # Limit to top 5 results
        ingredients = []
        for i in range(1, 21):
            ing = meal.get(f"strIngredient{i}")
            measure = meal.get(f"strMeasure{i}")
            if ing and ing.strip():
                item_str = f"{measure.strip()} {ing.strip()}".strip() if measure else ing.strip()
                ingredients.append(item_str)

        results.append(
            {
                "id": meal.get("idMeal"),
                "title": meal.get("strMeal"),
                "category": meal.get("strCategory"),
                "area": meal.get("strArea"),
                "instructions": meal.get("strInstructions"),
                "image_url": meal.get("strMealThumb"),
                "ingredients": ingredients,
            }
        )

    return results
