def get_company_info(company_name: str) -> str:
    """Fetch a brief company profile using the assistant's web_search tool, or return a default if unavailable."""
    try:
        from functions import web_search
        query = f"{company_name} company profile mission products news"
        result = web_search(query)
        if result and 'results' in result and result['results']:
            return result['results'][0]['snippet']
        return f"No live info found for {company_name}. Please add details manually."
    except ImportError:
        return f"Company info not available in this environment."
    except Exception as e:
        return f"Error fetching company info: {e}" 