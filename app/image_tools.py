"""Image generation tools for Smart Recipe & Pantry Concierge."""

import os
import uuid
from typing import Any
from google import genai
from google.adk.tools import ToolContext
from google.cloud import storage
from google.genai.types import GenerateContentConfig, Part

# Hardcode project ID and Cloud Storage bucket name
PROJECT_ID = "qwiklabs-gcp-02-6bb634618822"
BUCKET_NAME = "smart-recipe-concierge-media-qwiklabs-gcp-02-6bb634618822"

# Support local sa-key.json if present
if os.path.exists("sa-key.json") and "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "sa-key.json"


async def generate_recipe_image(
    recipe_title: str, description: str, tool_context: ToolContext
) -> dict[str, Any]:
    """Generate a presentation image for a recipe using gemini-3.1-flash-lite-image, save it as an artifact, and upload it to public Cloud Storage.

    Args:
        recipe_title: Title or name of the recipe dish.
        description: Description or key ingredients of the dish to guide image generation.
        tool_context: ADK ToolContext injected automatically by the framework.

    Returns:
        A dictionary containing the image title, public Cloud Storage URL, and status.
    """
    client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
    prompt = f"A high-quality, professional food photograph of {recipe_title}: {description}. Beautiful presentation, appetizing lighting."

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-image",
        contents=prompt,
        config=GenerateContentConfig(response_modalities=["TEXT", "IMAGE"]),
    )

    image_bytes = None
    mime_type = "image/png"
    if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                image_bytes = part.inline_data.data
                if part.inline_data.mime_type:
                    mime_type = part.inline_data.mime_type
                break

    if not image_bytes:
        return {"error": "Failed to generate image bytes from model."}

    # 1. Save artifact with tool_context
    clean_title = recipe_title.lower().replace(" ", "_").replace("/", "_")
    filename = f"{clean_title}_image.png"
    artifact_part = Part.from_bytes(data=image_bytes, mime_type=mime_type)
    await tool_context.save_artifact(filename=filename, artifact=artifact_part)

    # 2. Upload image bytes to public Cloud Storage bucket
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob_name = f"recipes/{uuid.uuid4().hex[:8]}_{filename}"
    blob = bucket.blob(blob_name)
    blob.upload_from_string(image_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{blob_name}"

    return {
        "recipe_title": recipe_title,
        "public_url": public_url,
        "artifact_filename": filename,
        "status": "Image successfully generated, saved as artifact, and uploaded to Cloud Storage.",
    }
