# AI Newsletter Generator - Usage Guide

> **Note:** The pipeline has been fully validated. All advanced features (trend analysis, fact-checking, outline, source verification, humanization, references) are working together. The tool is ready for production use and future enhancements.

> Security, reliability, and data quality improvements are now in place. See README for details on API key management, privacy, and new CLI options.

## Quick Start

### Prerequisites
1. **Install Ollama**: `curl -fsSL https://ollama.ai/install.sh | sh`
2. **Pull CodeGemma:7b**: `ollama pull codellama:7b`
3. **Install Python dependencies**: `venv/bin/pip install -r requirements.txt`

### Basic Usage

Generate a newsletter for any topic:
```bash
venv/bin/python main.py generate "artificial intelligence trends 2024"
```

### Advanced Usage

Generate with custom format and output directory:
```bash
venv/bin/python main.py generate "climate change solutions" --format markdown --output-dir ./my-newsletters
```

Enable verbose logging:
```bash
venv/bin/python main.py generate "blockchain technology" --verbose
```

### Command Options

- `--format` or `-f`: Output format (`text` or `markdown`) [default: text]
- `--output-dir` or `-o`: Custom output directory [default: ./output]
- `--verbose` or `-v`: Enable detailed logging
- `--help`: Show help information

### Example Output

The tool will generate a newsletter file with:
1. **Psychological Hook**: An engaging opening line to capture attention
2. **Research-Based Content**: Comprehensive content based on web research
3. **Humanized Writing**: Conversational and engaging tone
4. **Source Integration**: Information from multiple credible sources

### File Naming

Generated files follow the pattern: `{topic}_{timestamp}.{format}`

Example: `artificial-intelligence-trends-2024_20250622_131034.txt`

### Configuration

Copy the environment template and customize:
```bash
cp env.example .env
```

Key settings in `.env`:
- `OLLAMA_HOST`: Ollama service URL (default: http://localhost:11434)
- `OLLAMA_MODEL`: Model name (default: codellama:7b)
- `OUTPUT_DIR`: Default output directory
- `MAX_SOURCES`: Maximum sources to research (default: 10)

### Testing

Run the MVP test suite:
```bash
venv/bin/python test_mvp.py
```

### Troubleshooting

**Ollama not running:**
```bash
ollama serve
```

**Model not found:**
```bash
ollama pull codellama:7b
```

**Permission errors:**
```bash
chmod +x main.py
```

### Performance Tips

1. **Use specific topics**: "AI in healthcare" vs "technology"
2. **Limit sources**: Adjust `MAX_SOURCES` in config for faster generation
3. **Monitor logs**: Check `logs/` directory for detailed information

### Next Steps

The MVP is ready for use! Future enhancements include:
- Enhanced web scraping with better source selection
- Improved prompt engineering for better content quality
- Advanced fact-checking and validation
- Performance optimizations 

## Generating a Newsletter

Run the following command:

    python main.py generate "<TOPIC>" --format text --output-dir output --verbose --validate

- Replace `<TOPIC>` with your desired newsletter topic.
- `--format` can be `text` or `markdown`.
- `--output-dir` specifies where the newsletter file will be saved.
- `--verbose` enables detailed logging.
- `--validate` enables content quality validation and optimization.

## Hook Style Selection

During generation, you will be prompted to select preferred psychological hook styles (e.g., curiosity, urgency, novelty, etc.).
- Enter a comma-separated list (e.g., `curiosity,novelty,urgency`) or press Enter for all styles.
- The system will generate and score multiple hooks using advanced prompt templates for each trigger type.

## CLI Output

- The CLI displays progress, animations, and process details for each step.
- All generated hooks are shown in a table with effectiveness scores (clarity, emotion, relevance, LLM, overall).
- The best hook is highlighted and shown in a dedicated panel.
- Content quality metrics and improvement suggestions are displayed if validation is enabled.

## Output File

- Only the final, polished newsletter (best hook + content) is saved to the output file.
- No scores or process data are included in the saved file.
- The output file is named using the topic and timestamp.

## Section-by-Section Newsletter Structure

- The CLI now displays the generated outline before content generation, so you can see the planned structure for your newsletter.
- Content is generated for each section individually, resulting in a more modular and logically organized newsletter.
- Each section (e.g., Introduction, Main Sections, Conclusion, Call-to-Action) is clearly labeled and follows the outline.
- This improves readability, flow, and user control over the newsletter structure.

## Advanced Source Verification

- Each section of the newsletter now includes inline citations for supporting sources (e.g., [1], [2]).
- The CLI displays a source coverage summary after content generation, showing how many sources were cited.
- If a claim cannot be matched to a source, it may be flagged as [unverified] in the content.
- This ensures transparency and traceability for all key facts and claims in the newsletter.

## Content Humanization

- The newsletter content is now humanized for better engagement and relatability.
- The CLI displays a before/after comparison so you can see the improvements in tone, transitions, and reader engagement.
- The final newsletter is more conversational, uses rhetorical questions, personal touches, and addresses the reader directly, while maintaining professionalism and accuracy.

## References Section

- All sources cited in the newsletter (e.g., [1], [2]) are listed in a References section at the end of the file.
- Only sources actually cited in the content are included, in order of appearance.
- This ensures professional, transparent, and traceable source management for your newsletters.

## Configuration File Management
- Settings can be loaded from `config/config.yaml` (YAML format). If missing or malformed, defaults are used and a warning is shown.
- Example config keys: `output_dir`, `log_dir`, `log_level`, `max_retries`.

## Output File Naming
- Output files are named using the topic slug and a timestamp, e.g., `ai-in-healthcare_20250625_190938.txt`.

## Plagiarism & Duplication Check
- The tool automatically checks for repeated sentences or paragraphs in the generated newsletter and warns in the CLI if detected.

## Source Verification Summary
- After newsletter generation, the CLI displays a summary of which sources were cited and which were not, for transparency.

## Parallel Processing (Planned)
- Batch topic generation and parallel processing are planned for future releases. The codebase includes a placeholder for this feature.

## Performance Monitoring
- The CLI now displays timing for each major pipeline stage and total generation time.

## Content Length Optimization
- The tool warns if the newsletter is too short (<600 words) or too long (>2000 words), suggesting expansion or splitting as needed.

## Engagement Prediction (Planned)
- Future releases may include ML-based engagement prediction models to estimate newsletter impact.

## Plagiarism Detection (Planned)
- Advanced plagiarism detection using third-party APIs/services is planned for future releases. The codebase includes a placeholder for this feature.

## Audit Trails & Privacy
- All newsletter generations are logged in a secure audit log (topic, timestamp, output file).
- No personal data is stored. See the CLI privacy policy and README for details. 