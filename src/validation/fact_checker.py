import re
from typing import List, Dict

class FactChecker:
    """Extracts and verifies factual claims in text using trusted sources."""
    def __init__(self):
        # Placeholder for API keys or client setup
        pass

    def extract_claims(self, text: str) -> List[str]:
        """
        Extract factual claims from text (simple sentence split for now).
        """
        # TODO: Use NLP for better claim extraction
        sentences = re.split(r'(?<=[.!?]) +', text)
        # Filter for sentences likely to be factual claims (mock: all sentences)
        return [s.strip() for s in sentences if len(s.strip()) > 20]

    def verify_claims(self, claims: List[str]) -> List[Dict]:
        """
        Check each claim against trusted sources (mocked for now).
        Returns a list of dicts: {'claim': str, 'status': 'verified'|'unverified'|'disputed', 'source': str}
        """
        # TODO: Integrate with real fact-checking APIs or search
        results = []
        for claim in claims:
            # Mock: randomly mark as verified/unverified
            import random
            status = random.choice(['verified', 'unverified', 'disputed'])
            source = 'https://example.com/fact' if status == 'verified' else ''
            results.append({'claim': claim, 'status': status, 'source': source})
        return results

    def generate_report(self, verification_results: List[Dict]) -> str:
        """
        Summarize the fact-checking results for CLI or report inclusion.
        """
        if not verification_results:
            return "No factual claims found."
        lines = []
        for r in verification_results:
            if r['status'] == 'verified':
                lines.append(f"[green]✔ Verified:[/green] {r['claim']} (Source: {r['source']})")
            elif r['status'] == 'disputed':
                lines.append(f"[red]✖ Disputed:[/red] {r['claim']}")
            else:
                lines.append(f"[yellow]❓ Unverified:[/yellow] {r['claim']}")
        return '\n'.join(lines) 