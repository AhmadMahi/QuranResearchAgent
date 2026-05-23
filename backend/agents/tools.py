import requests
from typing import Dict, Any, List


def search_quran(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Free Quran search via api.alquran.cloud — no API key required."""
    try:
        encoded = requests.utils.quote(query)
        url = f"https://api.alquran.cloud/v1/search/{encoded}/all/en.asad"
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        matches = resp.json().get("data", {}).get("matches", [])[:limit]

        results = []
        for m in matches:
            surah = m.get("surah", {})
            results.append({
                "surah_name": surah.get("englishName", "Unknown"),
                "surah_number": surah.get("number", 0),
                "ayah_number": m.get("numberInSurah", 0),
                "text": m.get("text", ""),
                "reference": f"Surah {surah.get('englishName', 'Unknown')} "
                             f"({surah.get('number', 0)}:{m.get('numberInSurah', 0)})",
            })
        return results or [{"reference": "No direct Quranic references found", "text": "", "surah_name": ""}]
    except Exception as e:
        return [{"reference": "Quran API unavailable", "text": str(e), "surah_name": ""}]


def get_prayer_times(city: str, country: str) -> Dict[str, str]:
    """Prayer times via api.aladhan.com — no API key required."""
    try:
        resp = requests.get(
            "https://api.aladhan.com/v1/timingsByCity",
            params={"city": city, "country": country, "method": 2},
            timeout=15,
        )
        resp.raise_for_status()
        timings = resp.json().get("data", {}).get("timings", {})
        keys = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]
        return {k: timings[k] for k in keys if k in timings}
    except Exception as e:
        return {"error": str(e)}


def get_weather(city: str, api_key: str) -> Dict[str, Any]:
    """Current weather via OpenWeatherMap (free tier)."""
    if not api_key:
        return {"note": "No OPENWEATHERMAP_API_KEY set — weather skipped"}
    try:
        resp = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"q": city, "appid": api_key, "units": "metric"},
            timeout=15,
        )
        resp.raise_for_status()
        d = resp.json()
        return {
            "city": d.get("name", city),
            "temperature": d.get("main", {}).get("temp"),
            "feels_like": d.get("main", {}).get("feels_like"),
            "humidity": d.get("main", {}).get("humidity"),
            "description": d.get("weather", [{}])[0].get("description", ""),
            "wind_speed": d.get("wind", {}).get("speed"),
            "icon": d.get("weather", [{}])[0].get("icon", ""),
        }
    except Exception as e:
        return {"error": str(e), "city": city}


def web_search(query: str, max_results: int = 5) -> List[str]:
    """DuckDuckGo search — free, no API key required."""
    try:
        from duckduckgo_search import DDGS
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append(
                    f"**{r['title']}**\n{r['body']}\n_Source: {r['href']}_"
                )
        return results or ["No web results found"]
    except Exception as e:
        return [f"Web search unavailable: {e}"]
