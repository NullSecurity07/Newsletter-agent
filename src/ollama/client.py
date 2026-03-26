import requests
import json
import time
from typing import Dict, Any, Optional
from src.utils.config import config
from src.utils.logger import logger
from datetime import datetime
from rich.console import Console

class OllamaClient:
    """Client for interacting with Ollama API and codellama:7b model."""
    
    def __init__(self):
        self.base_url = config.ollama_host
        self.model = config.ollama_model
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'AI-Newsletter-Generator/1.0'
        })
    
    def generate(self, prompt: str, system_prompt: str = "", max_tokens: int = 2000, console: Optional[Console] = None) -> str:
        """Generate text using codellama:7b model."""
        start_time = datetime.now()
        if console:
            console.print(f"[cyan]Sending prompt to Ollama at {start_time.strftime('%H:%M:%S')}[/cyan]")
            console.print(f"[bold]Prompt:[/bold] {prompt[:300]}{'...' if len(prompt) > 300 else ''}")
            if system_prompt:
                console.print(f"[bold]System Prompt:[/bold] {system_prompt[:300]}{'...' if len(system_prompt) > 300 else ''}")
        logger.debug(f"Sending request to Ollama: {self.base_url}/api/generate at {start_time}")
        response = None
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "system": system_prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40
                }
            }
            req_start = time.time()
            last_msg = req_start
            while True:
                try:
                    response = self.session.post(
                        f"{self.base_url}/api/generate",
                        json=payload,
                        timeout=config.generation_timeout
                    )
                    break
                except requests.exceptions.Timeout:
                    now = time.time()
                    if now - last_msg > 30:
                        if console:
                            console.print(f"[yellow]Still waiting for Ollama response... ({int(now - req_start)}s elapsed)[/yellow]")
                        last_msg = now
            req_end = time.time()
            if console:
                console.print(f"[cyan]Ollama response received in {req_end - req_start:.2f} seconds.[/cyan]")
            if response.status_code == 200:
                result = response.json()
                if not result or not str(result).strip():
                    logger.error("Ollama model returned empty or whitespace response.")
                    if console:
                        console.print("[red]❌ Model returned empty response. Please try again or check your prompt.[/red]")
                    return "[ERROR] Model returned empty response."
                return result.get('response', '')
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                if console:
                    console.print(f"[red]Ollama API error: {response.status_code} - {response.text}[/red]")
                return ""
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            if console:
                console.print(f"[red]Request error: {e}[/red]")
            return ""
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            if console:
                console.print(f"[red]Unexpected error: {e}[/red]")
            return ""
        finally:
            end_time = datetime.now()
            if console:
                console.print(f"[cyan]Request finished at {end_time.strftime('%H:%M:%S')} (duration: {(end_time - start_time).total_seconds():.2f}s)[/cyan]")
    
    def generate_with_retry(self, prompt: str, system_prompt: str = "", max_retries: int = None, console: Optional[Console] = None) -> str:
        """Generate text with retry logic and detailed CLI/log output."""
        max_retries = max_retries or config.max_retries
        for attempt in range(1, max_retries + 1):
            attempt_start = datetime.now()
            if console:
                console.print(f"[bold blue]Ollama generation attempt {attempt}/{max_retries} started at {attempt_start.strftime('%H:%M:%S')}[/bold blue]")
            try:
                result = self.generate(prompt, system_prompt, console=console)
                if not result or not str(result).strip():
                    logger.error(f"Attempt {attempt}: Model returned empty response.")
                    if console:
                        console.print(f"[red]Attempt {attempt}: Model returned empty response.[/red]")
                    continue
                if console:
                    console.print(f"[green]Ollama generation succeeded on attempt {attempt}.[/green]")
                return result
            except Exception as e:
                if attempt == max_retries:
                    if console:
                        console.print(f"[red]❌ Ollama model failed after {max_retries} attempts: {e}[/red]")
                    logger.error(f"Ollama model failed after {max_retries} attempts: {e}")
                    return f"[ERROR] Model failed: {e}"
                logger.error(f"Attempt {attempt} failed: {e}")
                if console:
                    console.print(f"[red]Attempt {attempt} failed: {e}[/red]")
                if attempt < max_retries:
                    time.sleep(1)
        logger.error(f"All {max_retries} attempts failed")
        if console:
            console.print(f"[red]All {max_retries} attempts failed[/red]")
        return ""
    
    def check_model_availability(self) -> bool:
        """Check if the codellama:7b model is available."""
        try:
            response = self.session.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get('models', [])
                return any(model['name'] == self.model for model in models)
            return False
        except Exception as e:
            logger.error(f"Error checking model availability: {e}")
            return False
    
    def health_check(self) -> bool:
        """Check if Ollama service is running."""
        try:
            response = self.session.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False 