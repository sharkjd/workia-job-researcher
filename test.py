#!/usr/bin/env python3
"""Test různých variant Serper dotazů pro doménu cova.cz."""

import asyncio
import os
import httpx
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("SERPER_API_KEY")
if not api_key:
    print("CHYBA: SERPER_API_KEY není v .env")
    exit(1)

SERPER_URL = "https://google.serper.dev/search"
DOMAIN = "cova.cz"

QUERY_VARIANTS = [
    ('Aktuální (OR s uvozovkami)', f'site:{DOMAIN} (kariéra OR práce OR "volná místa" OR jobs)'),
    ('Jen kariéra', f'site:{DOMAIN} kariéra'),
    ('Kariéra bez diakritiky', f'site:{DOMAIN} kariera'),
    ('Hledáme', f'site:{DOMAIN} hledáme'),
    ('Volná místa', f'site:{DOMAIN} volná místa'),
    ('Práce', f'site:{DOMAIN} práce'),
    ('Bez site: - cova kariéra', f'cova.cz kariéra'),
    ('OR bez uvozovek', f'site:{DOMAIN} (kariéra OR práce OR volná místa OR hledáme)'),
    ('site: s https', f'site:https://{DOMAIN} kariéra'),
]


async def search(query: str) -> list[dict]:
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.post(
            SERPER_URL,
            json={"q": query, "num": 10, "gl": "cz", "hl": "cs"},
            headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
        )
        r.raise_for_status()
        return r.json().get("organic", [])


async def main():
    for name, query in QUERY_VARIANTS:
        print("=" * 70)
        print(f"VARIANT: {name}")
        print("=" * 70)
        print(f"DOTAZ: {query}")
        print()
        try:
            results = await search(query)
            if results:
                print("VÝSLEDKY:")
                for i, item in enumerate(results, 1):
                    link = item.get("link", "N/A")
                    title = (item.get("title") or "")[:65]
                    print(f"  {i}. {link}")
                    print(f"     {title}")
            else:
                print("  (žádné výsledky)")
        except Exception as e:
            print(f"  CHYBA: {e}")
        print()
        await asyncio.sleep(1.5)


if __name__ == "__main__":
    asyncio.run(main())