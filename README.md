# 🌊 Operation Ditwah: Crisis Intelligence Pipeline

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=flat-square&logo=python&logoColor=white) ![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-412991?style=flat-square&logo=openai&logoColor=white) ![Gemini](https://img.shields.io/badge/Google-Gemini-8E75B2?style=flat-square&logo=google) ![Pydantic](https://img.shields.io/badge/Pydantic-Validation-E92063?style=flat-square) ![Pandas](https://img.shields.io/badge/Pandas-Data_Handling-150458?style=flat-square&logo=pandas&logoColor=white) ![Prompt Engineering](https://img.shields.io/badge/Prompt_Engineering-Advanced-0052CC?style=flat-square)

**AI Engineer Essentials | Mini Project 0** *Scenario: Post-Cyclone Ditwah Relief (Sri Lanka) - December 2025*

## 📌 Project Overview
Operation Ditwah is a specialized AI pipeline designed for the **Disaster Management Center (DMC) of Sri Lanka**. Following the devastation of Cyclone Ditwah, this system filters, categorizes, and prioritizes incoming emergency messages to streamline rescue operations and optimize resource allocation.

The core objective is to build a **Reliable, Safe, and Efficient** intelligence system using Advanced Prompt Engineering and robust LLM orchestration.

live: https://crisis-intelligence-pipeline-7eorjc4gv7pgjus75kqdxf.streamlit.app/

## 🚀 Key Features

* 🚨 **Few-Shot SOS Classification:** Distinguishes real emergency calls from general news noise with high accuracy.
* 🛡️ **Hallucination Control:** Utilizes strict temperature settings to ensure the system provides factual, reliable rescue data.
* 🗺️ **Strategic Logistics Planning:** Implements **Chain-of-Thought (CoT)** and **Tree-of-Thought (ToT)** reasoning to effectively plan rescue routes.
* 💰 **Token Economics (Budget Keeper):** Optimizes API costs by dynamically truncating or summarizing long, spammy messages.
* 📊 **Structured Data Extraction:** Converts raw text feeds into validated Excel reports using **Pydantic** and **Pandas**.

## ⚙️ Logic Flow

The pipeline processes data through a structured, 5-step lifecycle:

`📥 Input` ➔ `🛡️ Filter` ➔ `🧠 Classify` ➔ `🏗️ Extract` ➔ `📊 Output`

1. **Input:** Raw messages and news feeds are ingested.
2. **Filter:** Token checks identify and truncate spam/noise.
3. **Classify:** Few-shot prompting categorizes the core intent (e.g., Rescue, Supply, Info).
4. **Extract:** Critical JSON data is extracted and strictly validated via Pydantic.
5. **Output:** A structured Excel report is generated for DMC decision-makers.

## 🛠️ Tech Stack

* **Language:** Python 3.x
* **AI Models:** OpenAI GPT-4o / Google Gemini (via API)
* **Validation:** Pydantic (for strict schema enforcement)
* **Data Handling:** Pandas, Openpyxl (Excel export)
* **Prompting Techniques:** Few-Shot, Chain-of-Thought (CoT), Tree-of-Thought (ToT)

## 📂 Project Structure

```text
├── data/
│   ├── sample_messages.txt   # Raw incoming emergency feeds
│   └── news_feed.txt         # Background noise and general updates
├── utils/
│   └── helper_functions.py   # Utility functions for token counting and API calls
├── output/                   # Final generated reports (e.g., flood_report.xlsx)
├── main.py                   # The primary execution script for the pipeline
├── requirements.txt
└── .env.example
