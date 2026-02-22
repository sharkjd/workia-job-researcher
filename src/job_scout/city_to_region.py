"""Mapa českých měst na kraje. Fallback pro doplnění regionu, když LLM ho neextrahuje."""

# Město (normalizované lowercase) -> kraj
CITY_TO_REGION: dict[str, str] = {
    # Praha
    "praha": "Praha",
    # Středočeský kraj
    "beroun": "Středočeský kraj",
    "kladno": "Středočeský kraj",
    "kolín": "Středočeský kraj",
    "kutná hora": "Středočeský kraj",
    "mělník": "Středočeský kraj",
    "mladá boleslav": "Středočeský kraj",
    "neratovice": "Středočeský kraj",
    "příbram": "Středočeský kraj",
    "říčany": "Středočeský kraj",
    "slaný": "Středočeský kraj",
    "benátky nad jizerou": "Středočeský kraj",
    "brandýs nad labem": "Středočeský kraj",
    "čelákovice": "Středočeský kraj",
    "dobříš": "Středočeský kraj",
    "hořovice": "Středočeský kraj",
    "kralupy nad vltavou": "Středočeský kraj",
    "lysá nad labem": "Středočeský kraj",
    "nepomuk": "Plzeňský kraj",  # Nepomuk je v Plzeňském kraji
    # Jihočeský kraj
    "české budějovice": "Jihočeský kraj",
    "tábor": "Jihočeský kraj",
    "písek": "Jihočeský kraj",
    "strakonice": "Jihočeský kraj",
    "jindřichův hradec": "Jihočeský kraj",
    "český krumlov": "Jihočeský kraj",
    "prachatice": "Jihočeský kraj",
    # Plzeňský kraj
    "plzeň": "Plzeňský kraj",
    "domažlice": "Plzeňský kraj",
    "klatovy": "Plzeňský kraj",
    "rokycany": "Plzeňský kraj",
    "tachov": "Plzeňský kraj",
    # Karlovarský kraj
    "karlovy vary": "Karlovarský kraj",
    "cheb": "Karlovarský kraj",
    "sokolov": "Karlovarský kraj",
    # Ústecký kraj
    "ústí nad labem": "Ústecký kraj",
    "děčín": "Ústecký kraj",
    "teplice": "Ústecký kraj",
    "most": "Ústecký kraj",
    "chomutov": "Ústecký kraj",
    "litoměřice": "Ústecký kraj",
    "louny": "Ústecký kraj",
    "žatec": "Ústecký kraj",
    # Liberecký kraj
    "liberec": "Liberecký kraj",
    "jablonec nad nisou": "Liberecký kraj",
    "česká lípa": "Liberecký kraj",
    "semily": "Liberecký kraj",
    "turnov": "Liberecký kraj",
    "tanvald": "Liberecký kraj",
    "frýdlant": "Liberecký kraj",
    # Královéhradecký kraj
    "hradec králové": "Královéhradecký kraj",
    "trutnov": "Královéhradecký kraj",
    "náchod": "Královéhradecký kraj",
    "rychnov nad kněžnou": "Královéhradecký kraj",
    "jičín": "Královéhradecký kraj",
    # Pardubický kraj
    "pardubice": "Pardubický kraj",
    "chrudim": "Pardubický kraj",
    "svitavy": "Pardubický kraj",
    "ústí nad orlicí": "Pardubický kraj",
    "litomyšl": "Pardubický kraj",
    "moravská třebová": "Pardubický kraj",
    # Kraj Vysočina
    "jihlava": "Kraj Vysočina",
    "havlíčkův brod": "Kraj Vysočina",
    "pelhřimov": "Kraj Vysočina",
    "třebíč": "Kraj Vysočina",
    "žďár nad sázavou": "Kraj Vysočina",
    "telč": "Kraj Vysočina",
    "nové město na moravě": "Kraj Vysočina",
    # Jihomoravský kraj
    "brno": "Jihomoravský kraj",
    "blansko": "Jihomoravský kraj",
    "břeclav": "Jihomoravský kraj",
    "hodonín": "Jihomoravský kraj",
    "vyškov": "Jihomoravský kraj",
    "znojmo": "Jihomoravský kraj",
    "kroměříž": "Zlínský kraj",  # Kroměříž je ve Zlínském kraji
    # Olomoucký kraj
    "olomouc": "Olomoucký kraj",
    "prostějov": "Olomoucký kraj",
    "přerov": "Olomoucký kraj",
    "šumperk": "Olomoucký kraj",
    "jeseník": "Olomoucký kraj",
    # Moravskoslezský kraj
    "ostrava": "Moravskoslezský kraj",
    "opava": "Moravskoslezský kraj",
    "havířov": "Moravskoslezský kraj",
    "karviná": "Moravskoslezský kraj",
    "frýdek-místek": "Moravskoslezský kraj",
    "nový jičín": "Moravskoslezský kraj",
    "třinec": "Moravskoslezský kraj",
    "bohumín": "Moravskoslezský kraj",
    "kopřivnice": "Moravskoslezský kraj",
    # Zlínský kraj
    "zlín": "Zlínský kraj",
    "uherské hradiště": "Zlínský kraj",
    "uherský brod": "Zlínský kraj",
    "valašské meziříčí": "Zlínský kraj",
    "vsetín": "Zlínský kraj",
}


def get_region(city: str) -> str:
    """Vrátí kraj pro dané město, nebo prázdný řetězec pokud město není v mapě."""
    if not city or not isinstance(city, str):
        return ""
    key = city.strip().lower()
    return CITY_TO_REGION.get(key, "")
