<p align="center"><a href="https://adithyapoojary.is-a.dev"><picture><source media="(prefers-color-scheme: light)" srcset=".github/readme/banner-light.svg"><img src=".github/readme/banner-dark.svg" alt="Newsletter-agent: From a topic to a scored newsletter issue, locally" width="100%"></picture></a></p>
<p align="center"><picture><source media="(prefers-color-scheme: light)" srcset=".github/readme/badges-light.svg"><img src=".github/readme/badges-dark.svg" alt="python: 3.8+, runs: local LLMs, status: prototype" height="30"></picture></p>

Newsletter Agent turns a topic into a finished newsletter issue from the command line: it gathers articles, drafts with a local LLM, scores the draft and rewrites it if it falls short. For small teams that want a weekly issue without hand-curating links.

## Highlights

- **Four kinds of sources.** Pulls from NewsAPI, Google News, RSS feeds and the open web, then tags sources against a credibility list.
- **Outline first.** The model writes an outline, then drafts each section from the research.
- **Scored and rewritten.** Every draft is scored for readability, coherence, engagement and alignment with the sources. Anything under 70/100 goes back for a rewrite.
- **Hooks that fit the topic.** Picks from 11 opening styles (curiosity, storytelling, novelty and more), or uses the ones you ask for.
- **Local model.** Generation runs on Ollama, so drafts stay on your machine.

## How it works

1. `main.py generate` takes the topic, plus company, purpose, audience and tone (asked interactively if you leave them out).
2. The research scraper collects articles and ranks sources.
3. The generator writes an outline and drafts each section through Ollama.
4. The quality checker scores the draft and triggers a rewrite below 70.
5. Hooks are added and the issue is saved as text or Markdown to `./output`. Research runs are logged to SQLite.

## Quick start

Needs Python 3.8+ and [Ollama](https://ollama.com). A NewsAPI key is optional.

```bash
git clone https://github.com/NullSecurity07/Newsletter-agent.git
cd Newsletter-agent
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
ollama pull codellama:7b          # default model; set OLLAMA_MODEL in .env to use another
echo 'NEWSAPI_KEY=your_key' > .env  # optional
python main.py generate "AI in healthcare" --format markdown
```

See all options with `python main.py generate --help`.

## Project layout

```
main.py              CLI (generate, version, privacy)
src/research/        scrapers and trend analysis
src/generation/      outline, sections, rewrite loop
src/validation/      quality scoring
src/psychology/      hook styles and scoring
src/ollama/          Ollama client with retries
prompts/             prompt templates
```

## Status

Prototype. The quality scoring and rewrite loop work end to end. The claim-level fact checker in `src/validation/fact_checker.py` is still a placeholder: it splits out claims but assigns verdicts at random, so ignore its "Fact-Checking" panel for now. Connecting it to a real source check is the next step.

## Built by

Built by [Adithya Poojary](https://adithyapoojary.is-a.dev), founder of ThreatScope. [More projects](https://adithyapoojary.is-a.dev/work/) · [LinkedIn](https://www.linkedin.com/in/adithyapoojary/)
