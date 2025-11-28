
Author: Ashutosh Singh (IIT Madras)
Email: 23f2001233@ds.study.iitm.ac.in
License: MIT
LLM Analysis Quiz Solver – TDS Project 2

An autonomous agent that solves multi-step quiz tasks designed for the Tools in Data Science (TDS) course.
It handles web scraping, file processing, data analysis, OCR, audio transcription, and submits quiz answers automatically within time limits.

This project fully satisfies all TDS Project requirements.

🚀 Project Overview

Your agent receives a POST request containing:

{
  "email": "23f2001233@ds.study.iitm.ac.in",
  "secret": "your_secret",
  "url": "https://example.com/quiz-123"
}


It then:

Verifies the secret

Loads the quiz page (JS-rendered → uses Playwright)

Extracts instructions

Downloads any required files

Runs analysis or Python code

Submits answers to the provided endpoint

Follows the next URL to continue solving

Completes the entire quiz chain within 3 minutes

No hardcoded URLs.
Everything is dynamic, autonomous, and end-to-end.

🧠 Architecture
POST /solve
    │
    ▼
FastAPI backend
    │
    ▼
LangGraph autonomous agent
    │
    ├── Playwright (HTML rendering)
    ├── File downloader
    ├── OCR + Tesseract
    ├── Audio transcription
    ├── Python code executor
    ├── Dynamic dependency installer
    └── Submission handler

✨ Key Features

✔ Solve multi-page quiz chains
✔ Full JavaScript rendering (Playwright)
✔ PDF/CSV/Image downloading
✔ OCR with Tesseract
✔ Audio → text transcription
✔ Python execution sandbox
✔ Dynamic dependency installation
✔ Time-limit logic (3 minutes per URL chain)
✔ Automatic retries
✔ Low-token LangGraph workflow
✔ Docker & Render deployment ready

📁 Project Structure
.
├── main.py                 # FastAPI server (POST /solve)
├── agent.py                # LangGraph autonomous agent
├── tools/
│   ├── web_scraper.py
│   ├── download_file.py
│   ├── code_generate_and_run.py
│   ├── post_request.py
│   ├── add_dependencies.py
│   ├── ocr_image_tool.py
│   ├── transcribe_audio.py
│   └── encode_image_to_base64.py
├── shared_store.py
├── pyproject.toml
├── Dockerfile
├── .env.example
├── LICENSE                 # MIT
└── README.md               # THIS FILE

🔧 Setup
1. Clone the repository
git clone https://github.com/AlexMercer00/LLM-Analysis-Quiz-Solver.git
cd LLM-Analysis-Quiz-Solver

⚙️ Environment Variables

Create a .env file:

EMAIL=23f2001233@ds.study.iitm.ac.in
SECRET=your_secret_here
GOOGLE_API_KEY=your_gemini_api_key
AIPIPE_TOKEN=your_aipipe_token_if_using


Or use the included .env.example.

▶️ Running Locally
Install dependencies:
uv sync
uv run playwright install chromium

Run server:
uv run main.py


FastAPI will start at:

http://localhost:7860

🧪 Local Test Command
curl -X POST http://localhost:7860/solve \
  -H "Content-Type: application/json" \
  -d '{
    "email": "23f2001233@ds.study.iitm.ac.in",
    "secret": "your_secret",
    "url": "https://tds-llm-analysis.s-anand.net/demo"
  }'


Expected response:

{"status":"ok"}


Your agent will now begin solving automatically.

🌐 Deploying on Render.com (Docker)

Your Dockerfile is fully configured.
In Render:

Environment: Docker

Port: 7860

Add environment variables in GUI

Deploy → Render auto-detects port

Final app URL will be like:
https://llm-analysis-quiz-solver-xxxx.onrender.com

Your active endpoint becomes:

POST https://llm-analysis-quiz-solver-xxxx.onrender.com/solve

📌 API Specification
POST /solve
Request Body
{
  "email": "23f2001233@ds.study.iitm.ac.in",
  "secret": "your_secret",
  "url": "https://exam-quiz-url"
}

Validations

Invalid JSON → 400

Wrong secret → 403

Valid → returns:

{"status":"ok"}

After response

Agent launches in background and solves the quiz chain.

🧰 Tools (Agent Functions)
Tool	Description
get_rendered_html	Playwright JS rendering
download_file	Download PDFs/CSVs/images
run_code	Execute Python data-processing
ocr_image_tool	OCR text from images
transcribe_audio	Audio → text
encode_image_to_base64	For submissions with file outputs
post_request	Submits the quiz answer
add_dependencies	Installs missing Python libs

These tools allow the agent to solve any task in the TDS evaluation.

⏱ Time Limit Logic

Each quiz chain has 3 minutes maximum.

If the agent exceeds time → it intentionally submits a known-wrong answer (allowed by TDS rules)

This ensures progress continues to next URLs

Guarantees no timeout failures

✔ Verified Working (Demo Logs)

When tested locally or on Render, logs show:

Fetching demo page…
Answer submitted → correct
Next URL received…
Scraping next quiz…
Processing audio/PDF/image…
Submitting answer…
Quiz chain completed!


This confirms the system works exactly as required.
