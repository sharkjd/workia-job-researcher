# Workia Job Researcher (Blue-Collar Edition)

Automatizovaný nástroj pro výzkum trhu práce v modrých límečcích. Vyhledává lokální firmy, objevuje jejich kariérní stránky a extrahuje strukturovaná data o volných místech.

## Požadavky

- Python 3.11+

## Instalace

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

## Konfigurace

Zkopírujte `.env.example` do `.env` a vyplňte API klíče:

```
EXA_API_KEY=...
SERPER_API_KEY=...
GOOGLE_API_KEY=...
LANGCHAIN_API_KEY=...
LANGCHAIN_TRACING_V2=true
```

## Spuštění

```bash
python main.py
```

## Výstup

Výsledky se ukládají do `vysledky.csv`. Při opakovaném spuštění se data přidávají (append).
