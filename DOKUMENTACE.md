# Workia Job Researcher – Dokumentace aplikace

## Co aplikace dělá

**Workia Job Researcher** je automatizovaný nástroj pro vyhledávání pracovních nabídek na firemních webech. Zaměřuje se na **blue-collar pozice** (řidiči, skladníci, výrobní dělníci, kurýři, uklízeči, kuchaři atd.) a vyhledává je přímo na stránkách firem, ne na job boardech jako jobs.cz nebo Prace.cz.

---

## Jak to funguje – přehled pipeline

Aplikace používá **LangGraph** – graf stavů, kde každý uzel (node) provede jeden krok a předá výsledek dalšímu. Tok dat je lineární:

```
exa_query_gen → find_companies → company_triage → find_career_pages → filter_career_urls_llm → analyze_initial → filter_nav_links_llm → crawl_deep → validate_filter → export_csv → [END]
```

---

## Popis jednotlivých nodů

### 1. `exa_query_gen` – Generování vyhledávacího dotazu

**Účel:** Připraví sémantický vyhledávací dotaz pro Exa.ai podle zadané pozice a města.

**Jak funguje:**
- Načte z uživatelského vstupu `position` (např. „řidič“, „skladník“) a `city` (např. „Praha“)
- Pošle prompt do **Gemini 2.5 Flash** (LLM)
- LLM vygeneruje dotaz zaměřený na weby firem v daném městě, které zaměstnávají danou pozici
- Explicitně vylučuje job boardy (jobs.cz, Prace.cz, Indeed, LinkedIn atd.)

**Vstup:** `user_input` (position, city)  
**Výstup:** `exa_query` – textový dotaz pro Exa

---

### 2. `find_companies` – Hledání firemních domén

**Účel:** Najde domény firem pomocí **Exa.ai** (sémantické vyhledávání).

**Jak funguje:**
- Zavolá Exa API s vygenerovaným dotazem
- Z výsledků extrahuje domény (např. `dopravni-firma.cz`)
- Vyřadí domény z `blocked_domains` (job portály, zpravodajství, vzdělávací weby)
- Vyřadí již zpracované domény (`dynamic_exclude_domains`)
- Omezí počet firem podle `companies_per_run` (default 10)

**Vstup:** `exa_query`, `user_input`, `dynamic_exclude_domains`  
**Výstup:** `company_domains`, aktualizace `dynamic_exclude_domains`, vynulování přechodných polí

---

### 3. `find_career_pages` – Hledání kariérních stránek firem

**Účel:** Pro každou nalezenou firmu najde URL jejich kariérních stránek pomocí **Serper** (Google Search API).

**Jak funguje:**
- Pro každou doménu spustí Serper dotaz: `site:{domain} (kariéra OR práce OR volná místa OR jobs)`
- Z organických výsledků vezme URL (max. `max_career_links` na firmu, default 5)
- Pokud Serper nic nenajde, použije fallback `https://{domain}` (hlavní stránka)
- Vyřadí již zpracované URL (`excluded_urls`) a blokované domény

**Vstup:** `company_domains`, `user_input`, `excluded_urls`  
**Výstup:** `career_candidate_urls` – seznam URL ze Serperu (před LLM filtrem)

---

### 4. `filter_career_urls_llm` – LLM filtr kariérních URL

**Účel:** Z `career_candidate_urls` ponechá jen URL, které pravděpodobně vedou na kariéru nebo seznam pracovních pozic.

**Jak funguje:**
- Pošle seznam URL do **Gemini 2.5 Flash Lite** s promptem
- LLM vyřadí URL vedoucí na: GDPR, cookies, služby, produkty, e-shop, novinky, blog, kontakt, reference
- Zpracovává URL po dávkách (BATCH_SIZE = 60)

**Vstup:** `career_candidate_urls`  
**Výstup:** `career_candidate_urls` (přepsáno filtrovaným seznamem pro Crawl4AI)

---

### 5. `analyze_initial` – Analýza kariérních stránek (Crawl4AI + LLM)

**Účel:** Projde kariérní stránky, stáhne jejich obsah a pomocí LLM z nich extrahuje pracovní nabídky a odkazy na seznamy pozic.

**Jak funguje:**
- Pro každou URL z `career_candidate_urls`:
  - **Crawl4AI** (headless browser) načte stránku a vrátí Markdown
  - **Gemini 2.5 Flash Lite** analyzuje obsah a vrátí strukturovaný výstup:
    - `direct_offers` – pozice přímo na stránce (název, popis, plat, URL, firma)
    - `navigation_links` – odkazy typu „Aktuální volná místa“, „Všechny pozice“
- Odkazy projdou `nav_link_filter` – vyřadí se produkty, e-shop, blog, GDPR atd.
- Pro každou doménu se ponechá max. `max_nav_links_per_domain` odkazů (default 5)

**Vstup:** `career_candidate_urls`, `excluded_urls`, `user_input`  
**Výstup:** `raw_extracted_jobs`, `discovered_nav_links`

---

### 6. `filter_nav_links_llm` – LLM filtr odkazů

**Účel:** Z `discovered_nav_links` ponechá jen URL, které pravděpodobně vedou na seznam pracovních pozic.

**Jak funguje:**
- Pošle seznam URL do **Gemini 2.5 Flash Lite** s promptem
- LLM vyřadí URL vedoucí na: GDPR, cookies, služby, produkty, e-shop, novinky, blog, kontakt, reference
- Zpracovává URL po dávkách (BATCH_SIZE = 60)

**Vstup:** `discovered_nav_links`  
**Výstup:** `discovered_nav_links` (přepsáno filtrovaným seznamem)

---

### 7. `crawl_deep` – Hluboký crawl seznamů pozic

**Účel:** Projde odkazy na seznamy pozic a z každé stránky extrahuje všechny nabízené pozice.

**Jak funguje:**
- Pro každou URL z `discovered_nav_links`:
  - **Crawl4AI** načte stránku
  - **Gemini 2.5 Flash Lite** extrahuje všechny pozice (position, description, salary, url, company)
- Výsledky se **sloučí** s `raw_extracted_jobs` z `analyze_initial` (pozice z prvního kroku + z hlubokých odkazů)

**Vstup:** `discovered_nav_links`, `excluded_urls`, `raw_extracted_jobs`  
**Výstup:** `raw_extracted_jobs` (rozšířené o nové pozice)

---

### 8. `validate_filter` – Validace a filtrování (Blue-Collar Bouncer)

**Účel:** Z extrahovaných pozic ponechá jen **blue-collar** (manuální) práce a odstraní duplicity.

**Jak funguje:**
- **Gemini 2.5 Flash Lite** dostane seznam pozic a prompt s pravidly:
  - **PONECHAT:** řidiči, skladníci, výrobní dělníci, kurýři, uklízeči, prodejní personál, kuchaři, řemeslníci…
  - **ODSTRANIT:** IT, HR, marketing, management, administrativa, pozice vyžadující VŠ
- Deduplikace podle kombinace (position, company)
- Vyřadí pozice z blokovaných domén

**Vstup:** `raw_extracted_jobs`, `career_candidate_urls`, `discovered_nav_links`  
**Výstup:** `formatted_results`, `all_formatted_results`, `excluded_urls`, `loop_count`

---

### 9. `export_csv` – Export do CSV

**Účel:** Uloží `all_formatted_results` do souboru `vysledky.csv`.

**Jak funguje:**
- Zapíše CSV s hlavičkou: position, company, description, salary, url, source_url
- Po `validate_filter` jde tok na `export_csv` a pak na END

---

## Pomocné moduly

### `blocked_domains.py`
- Seznam domén, které se ignorují (job portály, zpravodajství, vzdělávací weby)
- Funkce `is_domain_blocked(url)` – vrátí True, pokud je doména v blacklistu

### `nav_link_filter.py`
- `filter_career_candidates(urls)` – vyřadí URL s cestami typu /produkt, /eshop, /blog, /gdpr atd.
- `limit_per_domain(urls, max)` – pro každou doménu ponechá max N odkazů

### `url_utils.py`
- `normalize_url(url)` – normalizace pro porovnávání (lowercase, bez fragmentu)
- `is_url_excluded(url, excluded_set)` – kontrola, zda URL už byla zpracována

### `models.py` (Pydantic)
- `ExtractedJob` – jedna extrahovaná pozice
- `PageAnalysisResult` – direct_offers + navigation_links z analýzy stránky
- `ValidatedJob` – finální validovaná pozice pro export
- `FilteredUrlsResult` – výstup LLM filtru URL
- `ValidatedJobsList` – wrapper pro seznam validovaných pozic

---

## Stav (JobScoutState)

Graf předává mezi uzly sdílený stav:

| Pole | Popis |
|------|-------|
| `user_input` | Parametry od uživatele (position, city, limity) |
| `exa_query` | Vygenerovaný dotaz pro Exa |
| `loop_count` | Počet iterací smyčky (pro budoucí opakování) |
| `dynamic_exclude_domains` | Domény už zpracované (přidává se) |
| `excluded_urls` | URL už zpracované (přidávají se) |
| `all_formatted_results` | Všechny validované pozice (přidávají se) |
| `company_domains` | Aktuální seznam firemních domén |
| `career_candidate_urls` | URL kariérních stránek k analýze |
| `discovered_nav_links` | Odkazy na seznamy pozic |
| `raw_extracted_jobs` | Všechny extrahované pozice (před validací) |
| `formatted_results` | Validované pozice z aktuální iterace |

---

## Spuštění

1. Nastavte v `.env`:
   - `EXA_API_KEY` – API klíč pro Exa.ai
   - `SERPER_API_KEY` – API klíč pro Serper (Google Search)
   - `GOOGLE_API_KEY` – pro Gemini (LangChain)

2. Spusťte: `python main.py`

3. Zadejte parametry:
   - Pozice (např. řidič, skladník)
   - Město
   - Počet firem na běh
   - Max. odkazů na kariéru na firmu
   - Max. odkazů na crawl na doménu
   - Počet opakování smyčky

4. Výsledky se vypíší do konzole (validované blue-collar pozice).
