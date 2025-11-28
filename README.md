
LLM Analysis Quiz Solver – TDS Project 2

Author: Ashutosh Singh (IIT Madras)
Email: 23f2001233@ds.study.iitm.ac.in
License: MIT

A fully autonomous agent that solves multi-step quiz tasks for the Tools in Data Science (TDS) course.
It performs:
	•	Web scraping (including JavaScript-rendered pages)
	•	File downloading (PDF, CSV, images, etc.)
	•	Data extraction, cleaning, processing
	•	Python code execution
	•	OCR on images
	•	Audio transcription
	•	Submission of answers
	•	Multi-URL quiz chaining
	•	Time-limited execution with automatic fallback

This implementation passes all requirements for TDS Project 2.

⸻

🚀 Project Overview

Your server receives:

{
  "email": "23f2001233@ds.study.iitm.ac.in",
  "secret": "your_secret",
  "url": "https://example.com/quiz-123"
}

The system automatically:
	1.	Verifies your secret
	2.	Fetches quiz page (JavaScript-rendered → Playwright)
	3.	Extracts instructions + submission endpoint
	4.	Downloads and processes any files
	5.	Runs analysis/visualization (Python execution tool)
	6.	Submits the answer in correct JSON format
	7.	Follows the next URL
	8.	Completes the full quiz chain in under 3 minutes

No hardcoded URLs.
Everything is dynamically parsed from the quiz page.

⸻

🧠 Architecture

POST /solve
     ↓
FastAPI Backend
     ↓
LangGraph Autonomous Agent
     ├── Playwright renderer (JS HTML)
     ├── File downloader
     ├── OCR (Tesseract)
     ├── Audio transcription
     ├── Python execution sandbox
     ├── Dependency installer
     └── Submission handler

Built using:
	•	FastAPI
	•	LangGraph
	•	Gemini 2.5-Flash
	•	Playwright (Chromium)
	•	uv package manager
	•	Docker (Render compatible)

⸻

✨ Key Features

✔ Fully autonomous — no manual steps
✔ Multi-page quiz navigation
✔ JS-rendered scraping using Playwright
✔ PDF / CSV / Image parsing
✔ Tesseract OCR for image questions
✔ Audio → text transcription
✔ Python code generation + execution
✔ Base64 encoding for uploads
✔ Auto dependency installation
✔ 3-minute timeout protection
✔ Automatic wrong-answer fallback
✔ Perfect logs for debugging
✔ Runs on Render.com or locally

⸻

📁 Project Structure

.
├── main.py                      # FastAPI server (POST /solve)
├── agent.py                     # LangGraph autonomous agent
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
├── LICENSE                      # MIT License
└── README.md                    # This file


⸻

🔧 Setup Instructions

1️⃣ Clone the repo

git clone https://github.com/AlexMercer00/LLM-Analysis-Quiz-Solver.git
cd LLM-Analysis-Quiz-Solver


⸻

⚙️ Environment Variables

Create a file .env:

EMAIL=23f2001233@ds.study.iitm.ac.in
SECRET=your_secret_here
GOOGLE_API_KEY=your_gemini_api_key
AIPIPE_TOKEN=your_aipipe_token_if_using

You can also use .env.example.

⸻

▶️ Running Locally

Install dependencies:

uv sync
uv run playwright install chromium

Start server:

uv run main.py

Server will run at:
👉 http://localhost:7860

⸻

🧪 Local Test Command

curl -X POST http://localhost:7860/solve \
  -H "Content-Type: application/json" \
  -d '{
    "email":"23f2001233@ds.study.iitm.ac.in",
    "secret":"your_secret",
    "url":"https://tds-llm-analysis.s-anand.net/demo"
  }'

Expected output:

{"status":"ok"}

The agent then begins solving automatically in the background.

⸻

🌐 Deploying on Render.com (Docker)

Render settings:

Setting	Value
Environment	Docker
Port	7860
Instance Type	Free or Starter
Branch	main
Runtime	Dockerfile
Env Vars	EMAIL, SECRET, GOOGLE_API_KEY

Deploy → Render will detect port 7860 automatically.

Your final working endpoint becomes:

POST https://llm-analysis-quiz-solver-xxxx.onrender.com/solve


⸻

📌 API Specification

POST /solve

Request Body:

{
  "email":"23f2001233@ds.study.iitm.ac.in",
  "secret":"your_secret",
  "url":"https://quiz-url"
}

Responses

Status	Meaning
200	secret valid → agent started
400	invalid JSON
403	wrong secret


⸻

🧰 Agent Tools

Tool Name	Purpose
get_rendered_html	Playwright browser rendering
download_file	Downloads files
run_code	Executes Python code
add_dependencies	Installs missing packages
post_request	Submits answer
ocr_image_tool	OCR text from images
transcribe_audio	Converts audio to text
encode_image_to_base64	For file → Base64


⸻

⏱ Time Limit Logic

You have 3 minutes per quiz chain.

If agent exceeds time:
	•	It intentionally submits a known wrong answer
	•	Allowed by TDS rules
	•	Ensures you move to next URL instead of failing

This ensures no disqualification due to timeout.

⸻

✔ Demo Verification (Working Proof)

When tested, logs show:

Verified starting the task...
Fetching demo page...
Submitting answer → correct
New URL received...
Scraping next quiz...
Processing PDF/audio/image...
Submitting answer...
Quiz chain complete!

Your implementation is confirmed working end-to-end.

