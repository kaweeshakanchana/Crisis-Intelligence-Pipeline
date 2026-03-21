🌊 Operation Ditwah: Crisis Intelligence Pipeline
AI Engineer Essentials | Mini Project 0 Scenario: Post-Cyclone Ditwah Relief (Sri Lanka) - December 2025

📌 Project Overview
Operation Ditwah is a specialized AI pipeline designed for the Disaster Management Center (DMC) of Sri Lanka. Following the devastation of Cyclone Ditwah, this system filters, categorizes, and prioritizes incoming emergency messages to streamline rescue operations and resource allocation.

The core objective is to build a Reliable, Safe, and Efficient intelligence system using Advanced Prompt Engineering and LLM orchestration.

🚀 Key Features
Few-Shot SOS Classification: Distinguishes real emergency calls from general news noise with high accuracy.

Hallucination Control: Uses strict temperature settings to ensure the system provides factual, reliable rescue data.

Strategic Logistics Planning: Implements Chain-of-Thought (CoT) and Tree-of-Thought (ToT) reasoning to plan rescue routes.

Token Economics (Budget Keeper): Optimizes API costs by truncating or summarizing long, spammy messages.

Structured Data Extraction: Converts raw text feeds into validated Excel reports using Pydantic and Pandas.

🛠️ Tech Stack
Language: Python 3.x

AI Models: OpenAI GPT-4o / Gemini (via API)

Validation: Pydantic (for schema enforcement)

Data Handling: Pandas, Openpyxl (Excel export)

Prompting Techniques: Few-Shot, CoT, ToT

📂 Project Structure
data/ : Contains sample_messages.txt and news_feed.txt.

utils/ : Utility functions for token counting and API calls.

output/ : Final generated reports (e.g., flood_report.xlsx).

main.py : The primary execution script for the pipeline.

⚙️ Setup & Installation
Clone the Repository:

Bash
git clone https://github.com/kaweeshakanchana/Intelligent-Knowledge-Management-Multi-RAG-System.git
cd ikms-rag-agent-system
Install Dependencies:

Bash
pip install -r requirements.txt
Configure Environment Variables:
Create a .env file in the root directory and add your API key:

Code snippet
OPENAI_API_KEY=your_secret_key_here
(Note: Ensure .env is added to your .gitignore to prevent leaking keys!)

Run the Pipeline:

Bash
python main.py
📊 Logic Flow
Input: Raw messages/feeds are ingested.

Filter: Token check identifies and truncates spam.

Classify: Few-shot prompting categorizes intent (Rescue, Supply, Info, etc.).

Extract: JSON data is extracted and validated via Pydantic.

Output: A structured Excel report is generated for the DMC decision-makers.
