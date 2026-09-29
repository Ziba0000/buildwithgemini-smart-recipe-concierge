# Smart Recipe & Pantry Concierge

An agentic AI assistant built with Google's **Agent Development Kit (ADK)**, **Gemini models**, and **Google Cloud Agent Platform**. It provides intelligent meal planning, pantry tracking, nutritional code execution, AI food photo & video generation, cross-session long-term memory, and rich visual A2UI cards.

![Smart Recipe & Pantry Concierge Demo](./demo.gif)

---

## 🌟 Key Features & Wired Services

The agent integrates the following Google Cloud services, models, and tools:

- **🥗 Pantry Inventory Management (Google Cloud Firestore)**
  - Tracks user pantry items, quantities, and expiration dates in Firestore (`get_pantry_items`, `update_pantry_item`).

- **🍝 Recipe Discovery (Firestore & DDGS Online Search)**
  - Searches local curated recipe collections in Firestore (`search_recipes`, `get_recipe_details`, `add_recipe`).
  - Searches live web recipes via DuckDuckGo search (`search_online_recipes`).

- **🛒 Automated Shopping List Generation**
  - Cross-references recipe requirements against available pantry inventory to generate missing ingredients lists (`generate_shopping_list`).

- **🧮 Precise Nutritional Math (Agent Engine Code Sandbox)**
  - Executes Python code in an isolated `AgentEngineSandboxCodeExecutor` container for accurate unit conversions, macro calculations, and scaling recipe yields.

- **📷 AI Food Photo Generation (Gemini Image Model + Cloud Storage)**
  - Generates food presentation photography with `gemini-3.1-flash-lite-image` (`generate_recipe_image`).
  - Saves binary outputs via `tool_context.save_artifact()` for the Playground Artifacts panel.
  - Uploads image bytes to a public Google Cloud Storage bucket (`smart-recipe-concierge-media-*`) and returns a public HTTPS link.

- **🎥 AI Food Video Generation (Google Omni Model + Cloud Storage)**
  - Generates short presentation videos using Google's Omni model (`gemini-omni-flash-preview`) in the `global` region (`generate_recipe_video`).
  - Saves video bytes as artifacts and uploads to public Cloud Storage.

- **🧠 Cross-Session Memory (Vertex AI Memory Bank)**
  - Uses `VertexAiMemoryBankService` and `PreloadMemoryTool` to persist user dietary preferences, allergies, and kitchen equipment facts across conversations.

- **🎨 Rich Surface UI Cards (A2UI 0.8)**
  - Constructs structured visual display cards using `A2uiSchemaManager` (version 0.8) and `BasicCatalog` rendered via `after_model_callback`.

---

## 📁 Repository Structure

```
.
├── app/
│   ├── agent.py                 # Core ADK agent configuration & tools registration
│   ├── a2ui_utils.py            # A2UI callback handler for structured UI rendering
│   ├── firestore_tools.py       # Firestore database integration for pantry & recipes
│   ├── image_tools.py           # Gemini image generation & Cloud Storage upload
│   ├── video_tools.py           # Gemini Omni video generation & Cloud Storage upload
│   └── online_recipe_tools.py   # DuckDuckGo online recipe search
├── frontend/
│   ├── main.py                  # FastAPI proxy routing A2A traffic to Agent Engine
│   └── static/
│       └── index.html           # Modern custom chat UI with A2UI renderer
├── scripts/
│   └── seed_firestore.py        # Database seed script for pantry & recipe collections
├── agents-cli-manifest.yaml     # Agent deployment manifest & configuration
├── demo.gif                     # Recorded demo walkthrough
└── pyproject.toml               # Python project dependencies
```

---

## 🚀 Running Locally

### Prerequisites
- Python 3.11+
- `uv` package manager installed (`pip install uv`)
- Authentated `gcloud` CLI (`gcloud auth login` and `gcloud auth application-default login`)

### Setup Instructions

1. **Install Dependencies**:
   ```bash
   uv sync
   ```

2. **Seed Firestore Database**:
   ```bash
   uv run python scripts/seed_firestore.py
   ```

3. **Start the Agent Playground (Local ADK Web)**:
   ```bash
   adk web
   ```

4. **Start the Custom Frontend & Proxy**:
   ```bash
   cd frontend
   pip install -r requirements.txt
   uvicorn main:app --port 8080 --reload
   ```

---

## ☁️ Cloud Deployment

The agent is designed to deploy to **Google Cloud Agent Platform (Agent Runtime)** and Cloud Run:

```bash
# Deploy Agent to Agent Runtime
agents-cli deploy agent

# Deploy Frontend to Cloud Run
gcloud run deploy smart-recipe-concierge-frontend \
  --source ./frontend \
  --region us-east1 \
  --allow-unauthenticated
```
