"""Video generation tools for Smart Recipe & Pantry Concierge using Google Omni models."""

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


async def generate_recipe_video(
    recipe_title: str, description: str, tool_context: ToolContext
) -> dict[str, Any]:
    """Generate a short presentation video for a recipe dish using Google's Omni model (gemini-omni-flash-preview) in the global region, save it as an artifact, and upload it to public Cloud Storage.

    Args:
        recipe_title: Title or name of the recipe dish.
        description: Description or visual scene of the dish to guide video generation.
        tool_context: ADK ToolContext injected automatically by the framework.

    Returns:
        A dictionary containing the recipe title, public Cloud Storage URL, artifact filename, and status.
    """
    client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
    prompt = f"A short, high-quality, professional food video of {recipe_title}: {description}. Appetizing presentation and smooth movement."

    response = client.models.generate_content(
        model="gemini-omni-flash-preview",
        contents=prompt,
        config=GenerateContentConfig(response_modalities=["TEXT", "VIDEO"]),
    )

    video_bytes = None
    mime_type = "video/mp4"
    if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                video_bytes = part.inline_data.data
                if part.inline_data.mime_type:
                    mime_type = part.inline_data.mime_type
                break

    if not video_bytes:
        return {"error": "Failed to generate video bytes from model."}

    # 1. Save artifact with tool_context
    clean_title = recipe_title.lower().replace(" ", "_").replace("/", "_")
    ext = ".mp4" if "mp4" in mime_type else ".webm"
    filename = f"{clean_title}_video{ext}"
    artifact_part = Part.from_bytes(data=video_bytes, mime_type=mime_type)
    await tool_context.save_artifact(filename=filename, artifact=artifact_part)

    # 2. Upload video bytes to public Cloud Storage bucket
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob_name = f"videos/{uuid.uuid4().hex[:8]}_{filename}"
    blob = bucket.blob(blob_name)
    blob.upload_from_string(video_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{blob_name}"

    return {
        "recipe_title": recipe_title,
        "public_url": public_url,
        "artifact_filename": filename,
        "status": "Video successfully generated, saved as artifact, and uploaded to Cloud Storage.",
    }
