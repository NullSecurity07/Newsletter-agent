# Privacy Notice: This module manages sensitive configuration, including API keys. Keys are loaded securely from environment variables only.
import os
import yaml
from typing import Optional
from dotenv import load_dotenv

class Config:
    """Configuration management for the newsletter generator."""
    
    def load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    data = yaml.safe_load(f)
                if data:
                    for k, v in data.items():
                        setattr(self, k, v)
            except Exception as e:
                print(f"[Warning] Could not load config file: {e}. Using defaults.")
        else:
            print(f"[Warning] Config file '{self.config_path}' not found. Using defaults.")

    def __init__(self):
        self.config_path = os.path.join("config", "config.yaml")
        self.load_config()
        self.log_dir = getattr(self, 'log_dir', "logs")
        self.output_dir = getattr(self, 'output_dir', "output")
        self.log_level = getattr(self, 'log_level', "INFO")
        load_dotenv()
        
        # Ollama Configuration
        self.ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        self.ollama_model = os.getenv('OLLAMA_MODEL', 'codellama:7b')
        
        # Output Configuration
        self.output_dir = os.getenv('OUTPUT_DIR', './output')
        self.log_dir = os.getenv('LOG_DIR', './logs')
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        
        # Web Scraping Configuration
        self.scraping_delay = int(os.getenv('SCRAPING_DELAY', '1'))
        self.max_sources = int(os.getenv('MAX_SOURCES', '10'))
        self.user_agent = os.getenv('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        # Content Generation Configuration
        self.max_content_length = int(os.getenv('MAX_CONTENT_LENGTH', '2000'))
        self.min_content_length = int(os.getenv('MIN_CONTENT_LENGTH', '500'))
        self.generation_timeout = int(os.getenv('GENERATION_TIMEOUT', '300'))
        
        # Rate Limiting
        self.requests_per_minute = int(os.getenv('REQUESTS_PER_MINUTE', '60'))
        self.max_retries = int(os.getenv('MAX_RETRIES', '3'))
        
        # News API Key
        self.newsapi_key = os.getenv('NEWSAPI_KEY', None)
    
    def ensure_directories(self):
        """Ensure all required directories exist."""
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)

def get_api_key(service_name):
    """Retrieve API key for a given service from environment variables."""
    env_var = f"{service_name.upper()}_API_KEY"
    return os.environ.get(env_var)

# Global config instance
config = Config() 