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


def web_search(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """DuckDuckGo search focused on IslamQA references."""

    def _normalize(items) -> List[Dict[str, str]]:
        out: List[Dict[str, str]] = []
        for r in items:
            title = str(r.get("title") or "Untitled").strip()
            snippet = str(r.get("body") or r.get("snippet") or "").strip()
            url = str(r.get("href") or r.get("url") or "").strip()
            out.append({"title": title, "snippet": snippet, "url": url})
        return out

    def _search_ddg(ddg_query: str, limit: int):
        try:
            from ddgs import DDGS  # preferred package name
        except Exception:
            from duckduckgo_search import DDGS  # backward compatibility

        with DDGS() as ddgs:
            return list(ddgs.text(ddg_query, max_results=limit))

    try:
        # Prioritize IslamQA references as requested.
        primary_query = f"site:islamqa.info {query}"
        primary = _normalize(_search_ddg(primary_query, max_results))
        islamqa = [r for r in primary if "islamqa.info" in r.get("url", "")]

        if len(islamqa) < max_results:
            backup_query = f"islamqa {query}"
            backup = _normalize(_search_ddg(backup_query, max_results * 2))
            for r in backup:
                if "islamqa.info" in r.get("url", ""):
                    islamqa.append(r)
                if len(islamqa) >= max_results:
                    break

        deduped: List[Dict[str, str]] = []
        seen = set()
        for r in islamqa:
            key = r.get("url", "")
            if not key or key in seen:
                continue
            seen.add(key)
            deduped.append(r)

        if deduped:
            return deduped[:max_results]

        return [{
            "title": "No IslamQA references found",
            "snippet": "DuckDuckGo returned no matching islamqa.info pages for this topic.",
            "url": "",
        }]
    except Exception as e:
        return [{
            "title": "Web search unavailable",
            "snippet": str(e),
            "url": "",
        }]
