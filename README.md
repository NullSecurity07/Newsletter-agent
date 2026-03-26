<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0a0a0f,50:0f172a,100:4f46e5&height=220&section=header&text=NEWSLETTER-AGENT&fontSize=64&fontColor=ffffff&fontAlignY=38&fontAlign=50&desc=Automated%20AI-Driven%20Content%20Curation%20and%20Generation&descSize=16&descAlignY=58&descAlign=50&descColor=818cf880&animation=fadeIn&v=2" width="100%"/>

</div>

<br/>

<div align="center">

*An autonomous engine for scraping, validating, and synthesizing high-engagement newsletters using local LLMs.*

</div>

<br/>

<div align="center">
<img src="https://capsule-render.vercel.app/api?type=rect&color=0:4f46e5,100:0f172a&height=1&section=header" width="40%"/>
</div>

<br/>

<div align="center">

### — Overview —

</div>

<br/>

Newsletter Agent is an automated intelligence tool built to replace manual content curation. It operates by orchestrating advanced web scraping, factual validation, and psychological engagement principles, feeding the refined data into a local Large Language Model (Ollama) to synthesize highly targeted, ready-to-publish newsletters.

The goal is to create a zero-click pipeline from raw internet noise to high-quality, verified, and structured reading material.

<br/>

<div align="center">
<img src="https://capsule-render.vercel.app/api?type=rect&color=0:4f46e5,100:0f172a&height=1&section=header" width="40%"/>
</div>

<br/>

<div align="center">

### — Architecture —

</div>

<br/>

| Component | Layer | Function |
|:---|:---|:---|
| `main.py` | Controller | CLI interface and pipeline orchestration |
| `research/` | Ingestion | Scrapes raw articles, trends, and NewsAPI data |
| `validation/` | Quality Control | Cross-references claims for factual accuracy and quality |
| `psychology/` | Optimization | Injects structural hooks to maximize reader engagement |
| `ollama/` | Synthesis | Interfaces with local LLMs (e.g., Llama2) for final generation |

<br/>

**Execution Pipeline**

```text
Operator (CLI)
    └─ Executes generation command (Topic + Date)
            └─ Scraper ingests raw web & API news data
                    └─ Validation layer filters hallucinations & low-quality sources
                            └─ Psychological hooks format the narrative structure
                                    └─ Ollama LLM synthesizes the final text
                                            └─ Output logged to SQLite & delivered to Operator
```

<br/>

**Why local validation and psychological hooks?**

Raw LLM outputs are often dry or prone to hallucination when summarizing current events. By decoupling the *fact-finding* (Scraper/NewsAPI), *fact-checking* (Validation), and *formatting* (Hooks) from the core generation, the local LLM is constrained to simply synthesizing verified data into an engaging format.

> This architecture ensures factual density while keeping sensitive operational data completely local via Ollama.

<br/>

<div align="center">
<img src="https://capsule-render.vercel.app/api?type=rect&color=0:4f46e5,100:0f172a&height=1&section=header" width="40%"/>
</div>

<br/>

<div align="center">

### — Capabilities —

</div>

<br/>

| Feature | Detail |
|:---|:---|
| Autonomous Generation | End-to-end newsletter creation based on a single topic prompt |
| Advanced Scraping | Gathers and parses relevant articles from distributed sources |
| Factual Validation | Built-in checkers to ensure output accuracy and quality |
| Engagement Engineering | Applies proven psychological hooks to written output |
| Local AI | Fully integrates with local or remote Ollama instances |
| Data Persistence | SQLite logging for historical trend tracking |

<br/>

<div align="center">
<img src="https://capsule-render.vercel.app/api?type=rect&color=0:4f46e5,100:0f172a&height=1&section=header" width="40%"/>
</div>

<br/>

<div align="center">

### — Setup —

</div>

<br/>

**Requirements**

- Python 3.8+
- [Ollama](https://ollama.ai/) installed locally
- *Optional:* NewsAPI Key for enhanced aggregation

<br/>

**Configuration**

```bash
# 1. Clone the repository and setup environment
git clone [https://github.com/your-username/newsletter-agent.git](https://github.com/your-username/newsletter-agent.git)
cd newsletter-agent
python -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Pull the required local LLM model (e.g., Llama2)
ollama pull llama2

# 4. Configure Environment
# Create a .env file in the root directory:
echo 'OLLAMA_BASE_URL="http://localhost:11434"' > .env
echo 'NEWS_API_KEY="YOUR_NEWS_API_KEY"' >> .env
```

<br/>

**Running**

```bash
# Generate a newsletter via the CLI
python main.py newsletter generate --topic "AI in Healthcare" --date "2024-03-26" --format "text"

# View available commands
python main.py newsletter generate --help
```

<br/>

<div align="center">
<img src="https://capsule-render.vercel.app/api?type=rect&color=0:4f46e5,100:0f172a&height=1&section=header" width="40%"/>
</div>

<br/>

<div align="center">

### — Stack —

</div>

<br/>

**Core** &nbsp;&nbsp; Python · SQLite · CLI

**AI Engine** &nbsp;&nbsp; Ollama · Llama2

**Data Processing** &nbsp;&nbsp; Web Scraping · REST APIs · Fact Checking Logic

<br/>

<div align="center">
<img src="https://capsule-render.vercel.app/api?type=rect&color=0:4f46e5,100:0f172a&height=1&section=header" width="40%"/>
</div>

<br/>

<div align="center">

### — Note —

</div>

<br/>

<div align="center">

```text
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║   Web scraping operations are subject to target site rate limits     ║
║   and terms of service. Adjust scraper concurrency accordingly.      ║
║                                                                      ║
║   The quality of the final synthesis depends heavily on the chosen   ║
║   Ollama model's parameter count and your local hardware limits.     ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

</div>

<br/>

<div align="center">

*Automated via Newsletter Agent*
&nbsp;·&nbsp;
[Report an Issue](https://github.com/your-username/newsletter-agent/issues)

<br/>

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:4f46e5,50:0f172a,100:0a0a0f&height=120&section=footer&animation=fadeIn&v=2" width="100%"/>

</div>
