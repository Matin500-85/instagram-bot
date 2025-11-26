
import requests
import random

def get_fresh_user_agent():
    """دریافت یک User-Agent تازه از منبع آنلاین"""
    try:
        response = requests.get(
            "https://jnrbsn.github.io/user-agents/user-agents.json",
            timeout=3
        )
        agents = response.json()
        return random.choice(agents) if agents else get_fallback_ua()
    except:
        return get_fallback_ua()

def get_fallback_ua():
    """دریافت User-Agent آفلاین"""
    fallback_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
        "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36"
    ]
    return random.choice(fallback_agents)
