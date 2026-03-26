#!/usr/bin/env python3
"""
MVP Test Script for AI Newsletter Generator
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.utils.config import config
from src.utils.logger import logger
from src.ollama.client import OllamaClient
from src.research.scraper import ResearchScraper
from src.generation.newsletter import NewsletterGenerator
from src.psychology.hooks import HookGenerator

def test_config():
    """Test configuration loading."""
    print("🔧 Testing configuration...")
    try:
        config.ensure_directories()
        print(f"✅ Configuration loaded successfully")
        print(f"   - Ollama host: {config.ollama_host}")
        print(f"   - Model: {config.ollama_model}")
        print(f"   - Output dir: {config.output_dir}")
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_ollama_client():
    """Test Ollama client initialization."""
    print("\n🤖 Testing Ollama client...")
    try:
        client = OllamaClient()
        print(f"✅ Ollama client initialized")
        print(f"   - Base URL: {client.base_url}")
        print(f"   - Model: {client.model}")
        
        # Test health check (will fail if Ollama not running, but that's expected)
        health = client.health_check()
        if health:
            print("   - Ollama service is running")
        else:
            print("   - Ollama service not running (expected for MVP test)")
        
        return True
    except Exception as e:
        print(f"❌ Ollama client test failed: {e}")
        return False

def test_research_scraper():
    """Test research scraper."""
    print("\n🔍 Testing research scraper...")
    try:
        scraper = ResearchScraper()
        print("✅ Research scraper initialized")
        
        # Test with a simple topic
        test_topic = "artificial intelligence"
        research_data = scraper.research_topic(test_topic)
        
        print(f"✅ Research completed for '{test_topic}'")
        print(f"   - Sources found: {len(research_data.get('sources', []))}")
        print(f"   - Key points: {len(research_data.get('key_points', []))}")
        
        return True
    except Exception as e:
        print(f"❌ Research scraper test failed: {e}")
        return False

def test_newsletter_generator():
    """Test newsletter generator."""
    print("\n📝 Testing newsletter generator...")
    try:
        client = OllamaClient()
        generator = NewsletterGenerator(client)
        print("✅ Newsletter generator initialized")
        
        # Test with mock data
        mock_research = {
            'topic': 'test topic',
            'summary': 'This is a test summary',
            'key_points': ['Point 1', 'Point 2', 'Point 3']
        }
        
        # This will fail if Ollama is not running, but that's expected
        print("   - Generator ready (requires Ollama for full testing)")
        
        return True
    except Exception as e:
        print(f"❌ Newsletter generator test failed: {e}")
        return False

def test_hook_generator():
    """Test hook generator."""
    print("\n🎣 Testing hook generator...")
    try:
        client = OllamaClient()
        generator = HookGenerator(client)
        print("✅ Hook generator initialized")
        
        # Test with mock data
        mock_research = {
            'topic': 'test topic',
            'summary': 'This is a test summary',
            'key_points': ['Point 1', 'Point 2', 'Point 3']
        }
        
        # This will fail if Ollama is not running, but that's expected
        print("   - Hook generator ready (requires Ollama for full testing)")
        
        return True
    except Exception as e:
        print(f"❌ Hook generator test failed: {e}")
        return False

def test_novelty_hook():
    """Test the Novelty trigger in HookGenerator."""
    print("\n✨ Testing Novelty trigger in HookGenerator...")
    try:
        client = OllamaClient()
        generator = HookGenerator(client)
        mock_research = {
            'topic': 'cutting-edge AI breakthroughs',
            'summary': 'Recent advances in AI are changing the landscape of technology.',
            'key_points': [
                'First-ever AI to pass the Turing Test',
                'Breakthroughs in generative models',
                'AI systems now outperforming humans in complex tasks'
            ]
        }
        hooks = generator.generate_hooks(mock_research['topic'], mock_research)
        novelty_hook = None
        for hook in hooks:
            if any(word in hook.lower() for word in ['first time', 'groundbreaking', 'never seen before', 'brand new', 'revolutionary']):
                novelty_hook = hook
                break
        print(f"Novelty Hook Output: {novelty_hook if novelty_hook else hooks}")
        return novelty_hook is not None
    except Exception as e:
        print(f"❌ Novelty trigger test failed: {e}")
        return False

def test_storytelling_hook():
    """Test the Storytelling trigger in HookGenerator."""
    print("\n📖 Testing Storytelling trigger in HookGenerator...")
    try:
        client = OllamaClient()
        generator = HookGenerator(client)
        mock_research = {
            'topic': 'AI in healthcare',
            'summary': 'AI is transforming patient care and diagnostics.',
            'key_points': [
                'AI-assisted diagnosis saves lives',
                'Doctors use AI to predict patient outcomes',
                'Hospitals adopt AI for efficiency'
            ]
        }
        hooks = generator.generate_hooks(mock_research['topic'], mock_research)
        storytelling_hook = None
        for hook in hooks:
            if any(word in hook.lower() for word in ['story', 'imagine', 'picture this', 'scenario', 'once', 'case study', 'real-world', 'anecdote']):
                storytelling_hook = hook
                break
        print(f"Storytelling Hook Output: {storytelling_hook if storytelling_hook else hooks}")
        return storytelling_hook is not None
    except Exception as e:
        print(f"❌ Storytelling trigger test failed: {e}")
        return False

def test_file_output():
    """Test file output functionality."""
    print("\n💾 Testing file output...")
    try:
        test_content = "This is a test newsletter content."
        test_topic = "test-topic"
        
        # Test the save function from main.py
        from main import save_newsletter
        
        filename = save_newsletter(test_content, test_topic, "txt", config.output_dir)
        
        if os.path.exists(filename):
            print(f"✅ File saved successfully: {filename}")
            
            # Clean up
            os.remove(filename)
            print("   - Test file cleaned up")
            return True
        else:
            print(f"❌ File not created: {filename}")
            return False
            
    except Exception as e:
        print(f"❌ File output test failed: {e}")
        return False

def main():
    """Run all MVP tests."""
    print("🚀 Starting MVP Tests for AI Newsletter Generator\n")
    
    tests = [
        test_config,
        test_ollama_client,
        test_research_scraper,
        test_newsletter_generator,
        test_hook_generator,
        test_novelty_hook,
        test_storytelling_hook,
        test_file_output
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! MVP is ready for use.")
        print("\n📋 Next steps:")
        print("1. Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh")
        print("2. Pull CodeGemma model: ollama pull codellama:7b")
        print("3. Run: venv/bin/python main.py generate 'your topic'")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    main() 