#!/usr/bin/env python3
"""
AI Newsletter Generator CLI
"""

import sys
import os
import logging
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
import time

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.utils.config import config
from src.utils.logger import logger
from src.ollama.client import OllamaClient
from src.research.enhanced_scraper import EnhancedResearchScraper
from src.generation.newsletter import NewsletterGenerator
from src.psychology.hooks import HookGenerator
from src.validation.fact_checker import FactChecker
from src.utils.company_info import get_company_info

app = typer.Typer()
console = Console()

# Define hook styles before any reference
all_styles = [
    'curiosity', 'urgency', 'emotional', 'benefit', 'question',
    'fomo', 'authority', 'social_proof', 'scarcity', 'novelty', 'storytelling'
]
style_map = {
    'curiosity': 'curiosity',
    'urgency': 'urgency',
    'emotional': 'emotional',
    'benefit': 'benefit',
    'question': 'question',
    'fomo': 'fomo',
    'authority': 'authority',
    'social_proof': 'social_proof',
    'scarcity': 'scarcity',
    'novelty': 'novelty',
    'storytelling': 'storytelling'
}

@app.command()
def generate(
    topic: str = typer.Argument(..., help="Topic for newsletter generation (e.g., 'AI in Healthcare')"),
    format: str = typer.Option("text", "--format", "-f", help="Output format: 'text' or 'markdown' [default: text]"),
    output_dir: str = typer.Option(None, "--output-dir", "-o", help="Directory to save generated newsletters [default: ./output]"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging for debugging and transparency"),
    validate: bool = typer.Option(True, "--validate/--no-validate", help="Enable/disable content validation and optimization [default: enabled]"),
    company: str = typer.Option(None, "--company", help="Company for which the newsletter is generated. If not provided, will prompt interactively."),
    purpose: str = typer.Option(None, "--purpose", help="Main purpose or goal of the newsletter. If not provided, will prompt interactively."),
    audience: str = typer.Option(None, "--audience", help="Target audience for the newsletter. If not provided, will use context or prompt interactively."),
    tone: str = typer.Option(None, "--tone", help="Tone of the newsletter. If not provided, will use context or prompt interactively."),
    hook_styles: str = typer.Option(None, "--hook-styles", help="Comma-separated list of preferred hook styles. If not provided, will prompt interactively."),
    no_interactive: bool = typer.Option(False, "--no-interactive", help="If set, error if any required value is missing instead of prompting.")
):
    """Generate a newsletter for the given topic."""
    import os
    # Warn if config file is missing
    config_path = os.path.join("config", "config.yaml")
    if not os.path.exists(config_path):
        console.print(f"[yellow]Warning: Config file '{config_path}' not found. Using default settings.[/yellow]")
    
    if verbose:
        logger.setLevel(logging.DEBUG)
    
    # Ensure directories exist
    config.ensure_directories()
    
    # Use provided output directory or default
    final_output_dir = output_dir or config.output_dir
    
    console.print(Panel.fit(f"[bold blue]🎯 Generating newsletter for: [white]{topic}[/white][/bold blue]", title="[bold]AI Newsletter Generator[/bold]", border_style="blue"))
    
    try:
        # Step indicator helper
        def step_header(n, label):
            console.print(f"\n[bold blue]Step {n}: {label}[/bold blue]")
        def print_duration(label, start, end):
            console.print(f"[cyan]{label} took {end - start:.2f} seconds.[/cyan]")

        # Prompt for company and purpose
        if not company:
            if no_interactive:
                console.print("[red]❌ --company is required in --no-interactive mode.[/red]")
                raise typer.Exit(1)
            company_val = Prompt.ask("[bold green]What company is this newsletter for?[/bold green]")
        else:
            company_val = company
        if not purpose:
            if no_interactive:
                console.print("[red]❌ --purpose is required in --no-interactive mode.[/red]")
                raise typer.Exit(1)
            purpose_val = Prompt.ask("[bold green]What is the main purpose or goal of this newsletter? (e.g., sell a course, promote a webinar, drive signups, etc.)[/bold green]")
        else:
            purpose_val = purpose
        # Live web search for company info
        console.print(f"[cyan]Researching company: {company_val}...[/cyan]")
        company_info = get_company_info(company_val)
        console.print(f"[cyan]Company info: {company_info}[/cyan]")

        # Audience and tone (optional, can use context)
        if not audience:
            audience_val = None
        else:
            audience_val = audience
        if not tone:
            tone_val = None
        else:
            tone_val = tone

        # Initialization and research (with progress)
        step_header(1, "Research")
        start_research = time.time()
        console.print(Panel.fit("[bold]Researching topic...[/bold]", border_style="magenta"))
        ollama_client = OllamaClient()
        scraper = EnhancedResearchScraper()
        newsletter_gen = NewsletterGenerator(ollama_client)
        hook_gen = HookGenerator(ollama_client)
        research_data = scraper.research_topic(topic)
        research_data['company'] = company_val
        research_data['company_info'] = company_info
        research_data['purpose'] = purpose_val
        if audience_val:
            research_data['audience'] = audience_val
        if tone_val:
            research_data['tone'] = tone_val
        end_research = time.time()
        print_duration("Research", start_research, end_research)

        # Fail fast if no research data or sources
        if not research_data or (isinstance(research_data, dict) and not research_data.get('sources')):
            console.print(Panel.fit("[red]❌ No research data or sources found for this topic. Please try a different topic or check your data sources.[/red]", border_style="red"))
            raise typer.Exit(1)
        console.print(Panel.fit(f"[green]Research complete in {end_research - start_research:.2f} seconds. Sources found: {len(research_data.get('sources', []))}[/green]", border_style="magenta"))

        # Display trend summary in CLI
        if research_data.get('trend_summary'):
            console.print(Panel.fit(f"[bold cyan]Latest Trends:[/bold cyan]\n\n{research_data['trend_summary']}", title="[bold cyan]Trend Analysis[/bold cyan]", border_style="cyan"))

        # Hook style selection
        if not hook_styles:
            if no_interactive:
                selected_styles = set(all_styles)
            else:
                console.print(Panel.fit(
                    f"[bold yellow]HOOK STYLE SELECTION[/bold yellow]\n\n"
                    f"Select preferred hook styles (comma-separated, or press Enter for all):\n"
                    f"[white]{', '.join(all_styles)}[/white]",
                    title="[bold yellow]Step: Choose Hook Styles[/bold yellow]",
                    border_style="yellow"
                ))
                user_styles = Prompt.ask("[bold green]Enter hook styles[/bold green]", default="all")
                console.print("[yellow]───────────────────────────────────────────────────────────────[/yellow]")
                if user_styles.strip().lower() == "all" or not user_styles.strip():
                    selected_styles = set(all_styles)
                else:
                    selected_styles = set(s.strip().lower() for s in user_styles.split(",") if s.strip().lower() in all_styles)
                    if not selected_styles:
                        selected_styles = set(all_styles)
        else:
            if hook_styles.strip().lower() == "all":
                selected_styles = set(all_styles)
            else:
                selected_styles = set(s.strip().lower() for s in hook_styles.split(",") if s.strip().lower() in all_styles)
                if not selected_styles:
                    selected_styles = set(all_styles)

        # Resume progress for the rest of the steps
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            # Content generation
            step_header(2, "Content Generation")
            start_content = time.time()
            console.print(Panel.fit("[bold]Generating newsletter content...[/bold]", border_style="green"))
            progress.update(progress.add_task("Generating newsletter content...", total=None), description="Generating newsletter content...")
            content_msg_time = start_content
            if validate:
                newsletter_content, quality_report = newsletter_gen.generate(topic, research_data, console=console)
            else:
                newsletter_content, quality_report = newsletter_gen.generate(topic, research_data, console=console)
            end_content = time.time()
            print_duration("Content Generation", start_content, end_content)
            console.print(Panel.fit(f"[green]Content generation complete in {end_content - start_content:.2f} seconds.[/green]", border_style="green"))

            # Fact-checking summary
            step_header(3, "Fact-Checking")
            start_fact = time.time()
            fact_checker = FactChecker()
            claims = fact_checker.extract_claims(newsletter_content)
            verification_results = fact_checker.verify_claims(claims)
            fact_report = fact_checker.generate_report(verification_results)
            end_fact = time.time()
            print_duration("Fact-Checking", start_fact, end_fact)
            console.print(Panel.fit(f"[bold magenta]Fact-Checking Summary:[/bold magenta]\n\n{fact_report}", title="[bold magenta]Fact-Checking[/bold magenta]", border_style="magenta"))

            # Hook generation
            step_header(4, "Hook Generation")
            start_hooks = time.time()
            console.print(Panel.fit("[bold]Generating psychological hooks...[/bold]", border_style="blue"))
            progress.update(progress.add_task("Generating psychological hooks...", total=None), description="Generating psychological hooks...")
            hooks_msg_time = start_hooks
            hooks = hook_gen.generate_hooks(topic, research_data, preferred_styles=selected_styles, console=console)
            end_hooks = time.time()
            print_duration("Hook Generation", start_hooks, end_hooks)
            console.print(Panel.fit(f"[green]Hook generation complete in {end_hooks - start_hooks:.2f} seconds.[/green]", border_style="blue"))

            # Display hook effectiveness scores
            display_hook_scores(hooks)

            # Combine content
            step_header(5, "Combining Content")
            start_combine = time.time()
            console.print(Panel.fit("[bold]Combining content...[/bold]", border_style="cyan"))
            progress.update(progress.add_task("Combining content...", total=None), description="Combining content...")
            final_newsletter = combine_content(hooks, newsletter_content)
            end_combine = time.time()
            print_duration("Combining Content", start_combine, end_combine)
            console.print(Panel.fit(f"[green]Content combined in {end_combine - start_combine:.2f} seconds.[/green]", border_style="cyan"))

            # Ensure output directory exists
            if not os.path.exists(final_output_dir):
                try:
                    os.makedirs(final_output_dir, exist_ok=True)
                    console.print(f"[green]Created output directory: {final_output_dir}[/green]")
                except Exception as e:
                    console.print(f"[red]❌ Could not create output directory: {final_output_dir} ({e})[/red]")
                    raise typer.Exit(1)
            elif not os.access(final_output_dir, os.W_OK):
                console.print(f"[red]❌ Output directory is not writable: {final_output_dir}[/red]")
                raise typer.Exit(1)

            # Save to file
            step_header(6, "Saving Newsletter")
            start_save = time.time()
            console.print(Panel.fit("[bold]Saving newsletter...[/bold]", border_style="magenta"))
            progress.update(progress.add_task("Saving newsletter...", total=None), description="Saving newsletter...")
            filename = save_newsletter(final_newsletter, topic, format, final_output_dir)
            end_save = time.time()
            print_duration("Saving Newsletter", start_save, end_save)

            # Display quality metrics
            if validate and quality_report:
                display_quality_metrics(quality_report)

            # Final summary panel
            total_time = end_save - start_research
            console.print(f"[bold green]Total generation time: {total_time:.2f} seconds[/bold green]")
            console.print(Panel.fit(f"[green]✅ Newsletter generated successfully!\n📄 Saved to: [white]{filename}[/white]\n⏱️ Total time: {total_time:.2f} seconds[/green]", title="[bold green]Success[/bold green]", border_style="green"))
            
    except Exception as e:
        logger.error(f"Error generating newsletter: {e}")
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1)

def display_quality_metrics(quality_report: dict):
    """Display content quality metrics in a formatted table."""
    console.print("\n[bold cyan]📊 Content Quality Assessment[/bold cyan]")
    
    # Create quality metrics table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Score", style="green")
    table.add_column("Status", style="yellow")
    
    metrics = [
        ("Overall Score", quality_report.get('overall_score', 0), "Overall Quality"),
        ("Readability", quality_report.get('readability_score', 0), "Ease of Reading"),
        ("Factual Accuracy", quality_report.get('factual_accuracy', 0), "Information Accuracy"),
        ("Coherence", quality_report.get('coherence_score', 0), "Logical Flow"),
        ("Engagement", quality_report.get('engagement_score', 0), "Reader Interest"),
        ("Source Alignment", quality_report.get('source_alignment', 0), "Research Alignment")
    ]
    
    for metric, score, description in metrics:
        status = get_quality_status(score)
        table.add_row(f"{description}", f"{score:.1f}/100", status)
    
    console.print(table)
    
    # Display suggestions if any
    suggestions = quality_report.get('suggestions', [])
    if suggestions:
        console.print("\n[bold yellow]💡 Improvement Suggestions:[/bold yellow]")
        for suggestion in suggestions:
            console.print(f"  • {suggestion}")
    
    # Overall assessment
    overall_score = quality_report.get('overall_score', 0)
    if overall_score >= 80:
        console.print("\n[bold green]🎉 Excellent quality! Content is ready for publication.[/bold green]")
    elif overall_score >= 60:
        console.print("\n[bold yellow]⚠️  Good quality with room for improvement.[/bold yellow]")
    else:
        console.print("\n[bold red]❌ Quality below threshold. Consider significant revision.[/bold red]")

def get_quality_status(score: float) -> str:
    """Get status indicator for quality score."""
    if score >= 80:
        return "[green]Excellent[/green]"
    elif score >= 60:
        return "[yellow]Good[/yellow]"
    elif score >= 40:
        return "[orange]Fair[/orange]"
    else:
        return "[red]Poor[/red]"

def display_hook_scores(hooks: list):
    """Display hook effectiveness scores in a formatted, engaging table, highlighting the best hook."""
    if not hooks or not isinstance(hooks[0], dict) or 'score' not in hooks[0]:
        return
    console.print("\n[bold cyan]🎣 Hook Effectiveness Scores[/bold cyan]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=3)
    table.add_column("Style", style="bold yellow", width=12)
    table.add_column("Hook", style="cyan", overflow="fold")
    table.add_column("Clarity", style="green")
    table.add_column("Emotion", style="red")
    table.add_column("Relevance", style="blue")
    table.add_column("LLM", style="magenta")
    table.add_column("Overall", style="yellow")
    for idx, h in enumerate(hooks):
        s = h['score']
        is_best = idx == 0
        style = h.get('style', '')
        row_style = "bold white on green" if is_best else ""
        table.add_row(
            f"{idx+1}",
            f"{style.title()}",
            f"[bold]{h['hook']}[/bold]" if is_best else h['hook'],
            f"{s.get('clarity', 0):.1f}",
            f"{s.get('emotional_impact', 0):.1f}",
            f"{s.get('relevance', 0):.1f}",
            f"{s.get('llm_score', 0):.1f}",
            f"[bold yellow]{s.get('overall_score', 0):.1f}[/bold yellow]" if is_best else f"{s.get('overall_score', 0):.1f}",
            style=row_style
        )
    console.print(table)
    # Highlight the best hook
    best = hooks[0]
    console.print(Panel.fit(f"[bold green]🏆 Best Hook:[/bold green]\n[white]{best['hook']}[/white]", border_style="green"))

def combine_content(hooks: list, newsletter_content: str) -> str:
    """Combine hooks and newsletter content, only including the best hook and cleaned newsletter body. Append a References section for all cited sources."""
    import re
    combined = ""
    # Add the best hook at the beginning
    if hooks:
        best_hook = hooks[0]['hook'] if isinstance(hooks[0], dict) and 'hook' in hooks[0] else str(hooks[0])
        combined += f"🎣 {best_hook.strip()}\n\n"
    # Remove meta-comments, repeated hooks, and duplicate content
    body = newsletter_content.strip()
    # Remove lines like "Here's the polished version..." and repeated hooks
    lines = body.splitlines()
    cleaned_lines = []
    seen_hook = False
    for line in lines:
        if line.strip().lower().startswith("here's the polished version"):
            continue
        if line.strip().lower().startswith("hook:"):
            if seen_hook:
                continue
            seen_hook = True
            continue  # The best hook is already at the top
        cleaned_lines.append(line)
    cleaned_body = '\n'.join(cleaned_lines).strip()
    combined += cleaned_body
    # Find all cited source numbers in the content
    cited_nums = set(int(m) for m in re.findall(r'\[(\d+)\]', cleaned_body))
    # Find the sources list in the content (if present)
    sources_section = re.search(r'Sources:\n((?:\[\d+\].*\n?)+)', cleaned_body)
    sources = []
    if sources_section:
        for line in sources_section.group(1).splitlines():
            m = re.match(r'\[(\d+)\]\s*(.+)', line)
            if m:
                num, url = int(m.group(1)), m.group(2).strip()
                if num in cited_nums:
                    sources.append((num, url))
    # Append References section if there are cited sources
    if sources:
        combined += "\n\n## References\n"
        for num, url in sorted(sources):
            combined += f"[{num}] {url}\n"
    return combined

def save_newsletter(content: str, topic: str, format: str, output_dir: str) -> str:
    """Save newsletter to file."""
    import re
    from datetime import datetime
    
    # Clean topic for filename
    safe_topic = re.sub(r'[^\w\s-]', '', topic).strip()
    safe_topic = re.sub(r'[-\s]+', '-', safe_topic)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_topic}_{timestamp}.{format}"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filepath

@app.command()
def version():
    """Show version information."""
    console.print("[bold blue]AI Newsletter Generator v1.0.0[/bold blue]")
    console.print("Powered by CodeGemma:7b via Ollama")
    console.print("Enhanced with quality validation and optimization")

@app.command()
def privacy():
    """Show privacy policy."""
    console.print("""
[bold blue]Privacy Policy[/bold blue]
- No personal user data is stored or shared.
- Only minimal audit logs (topic, timestamp, output file) are kept for troubleshooting and transparency.
- No newsletter content or sensitive information is retained beyond the output file.
- You control all input and output locations.
- For questions, see the README or contact the maintainer.
""")

if __name__ == "__main__":
    console.print("[green]Privacy Notice: No personal data is stored. Minimal audit logs are kept for transparency. Use '--privacy' for details.[/green]")
    app() 