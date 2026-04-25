# Multi-Agent Research Assistant

An advanced **Multi-Agent AI Research System** built with **LangChain LCEL**, live web search, autonomous agents, and production-style orchestration.

This system can:

- Think
- Search
- Read
- Write
- Critique

It behaves like a collaborative AI research team instead of a single LLM.

# Live Demo

Try the system here:
https://multiagentsystemgit-v7ufgkt9kcbcgdpgrpnbma.streamlit.app/
---

# Overview

This project uses **4 specialized AI agents** working together:

## 1. Search Agent
Responsible for:
- Searching the web in real time
- Finding relevant sources
- Collecting research signals

Powered by:
- Tavily API
- `web_search_tool`

Output saved into:

```python
state["search_results"]
```

---

## 2. Reader Agent
Responsible for:
- Visiting sources
- Scraping webpages
- Extracting meaningful information
- Converting noisy web data into structured knowledge

Powered by:
- LangChain AgentExecutor
- BeautifulSoup
- `scrape_url_tool`

Output saved into:

```python
state["scraped_content"]
```

---

## 3. Writer Agent
Responsible for:
- Synthesizing all gathered research
- Producing coherent reports
- Turning evidence into written intelligence

---

## 4. Critic Agent
Responsible for:
- Reviewing the full report
- Scoring quality
- Providing feedback
- Improving final output

The Critic acts like an AI reviewer/editor.

---

# Agent Workflow

User gives topic:

```text
User Topic
   ↓
Search Agent
   ↓
Reader Agent
   ↓
Writer Agent
   ↕
Critic Agent
   ↓
Final Research Report
```

### Pipeline Flow

Step 1

```python
Topic Input
→ Search Agent
→ Tavily live web search
→ state["search_results"]
```

Step 2

```python
Search Results
→ Reader Agent
→ scrape_url_tool
→ BeautifulSoup extraction
→ state["scraped_content"]
```

Step 3

```python
Scraped Content
→ Writer Agent
↔ Critic Agent
→ Final Reviewed Report
```

---

# Architecture

This system is powered by:

- LangChain Modern LCEL Pipeline
- AgentExecutor
- Tool Calling Agents
- Multi-Agent State Flow
- Production-style Agentic AI Patterns

This is not a toy chatbot.

It is a **production-level agentic research system.**

---

# Tech Stack

## LLM + Agent Framework
- LangChain
- LangChain Core
- LangChain Community
- LangChain OpenAI
- OpenAI

## Search
- Tavily API

## Scraping
- BeautifulSoup
- Requests
- lxml
- html5lib

## Async + Reliability
- aiohttp
- tenacity
- rich
- orjson

## Data / Utilities
- pandas
- tiktoken
- pydantic
- python-dotenv

---

# Project Structure

```bash
multi_agent_system/
│
├── agents.py           # Agent definitions
├── app.py              # Main application entrypoint
├── pipeline.py         # LCEL multi-agent workflow pipeline
├── tools.py            # Search + scraping tools
├── requirements.txt
├── .gitignore
└── __pycache__/
```

---

# Installation

Clone repo:

```bash
git clone https://github.com/yourusername/multi_agent_system.git
cd multi_agent_system
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create `.env`

```bash
OPENAI_API_KEY=your_key
TAVILY_API_KEY=your_key
```

---

# Run

```bash
python app.py
```

---

# Example Use Cases

Give it topics like:

- AI agents in healthcare
- Future of autonomous systems
- Deep research on climate policy
- Startup market analysis
- Technical literature review

---

# Why This Project Is Interesting

Unlike single-prompt assistants, this system separates cognition into roles:

- Searches like a researcher  
- Reads like an analyst  
- Writes like an author  
- Critiques like an editor  

That creates significantly stronger outputs.

---

# Future Improvements
Planned upgrades:

- Memory-enabled agents
- Vector retrieval (RAG)
- Multi-agent debate loops
- LangGraph orchestration
- Citation generation
- Report export (PDF/Markdown)

---

# Requirements

Main dependencies:

```txt
langchain>=0.2.0
langchain-core>=0.2.0
langchain-community>=0.2.0
langchain-openai>=0.1.0
openai>=1.30.0
tavily-python>=0.3.0
beautifulsoup4>=4.12.0
requests>=2.31.0
lxml>=5.0.0
python-dotenv>=1.0.0
aiohttp>=3.9.0
pandas>=2.0.0
tiktoken>=0.6.0
rich>=13.7.0
tenacity>=8.2.0
orjson>=3.9.0
pydantic>=2.5.0
html5lib>=1.1
```

Install:

```bash
pip install -r requirements.txt
```

---

# Author

Built as an exploration into **production-grade agentic AI systems** using modern LangChain architecture.

```

Optional GitHub repo subtitle idea:

> Multi-Agent Research Assistant powered by LangChain LCEL, Tavily search, autonomous agents and critique-driven report generation.

```

Small note: add `__pycache__/` to `.gitignore` (don’t keep that in repo 😄)

If you want this rewritten in stronger “open-source showcase / recruiter-friendly” style, I can help too.
