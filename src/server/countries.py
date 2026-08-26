# The country codes Brave's search endpoints accept, plus "ALL" for no country targeting.
COUNTRIES: tuple[tuple[str, str], ...] = (
    ("ALL", "All regions"),
    ("AR", "Argentina"),
    ("AU", "Australia"),
    ("AT", "Austria"),
    ("BE", "Belgium"),
    ("BR", "Brazil"),
    ("CA", "Canada"),
    ("CL", "Chile"),
    ("DK", "Denmark"),
    ("FI", "Finland"),
    ("FR", "France"),
    ("DE", "Germany"),
    ("HK", "Hong Kong"),
    ("IN", "India"),
    ("ID", "Indonesia"),
    ("IT", "Italy"),
    ("JP", "Japan"),
    ("KR", "Korea"),
    ("MY", "Malaysia"),
    ("MX", "Mexico"),
    ("NL", "Netherlands"),
    ("NZ", "New Zealand"),
    ("NO", "Norway"),
    ("CN", "People's Republic of China"),
    ("PL", "Poland"),
    ("PT", "Portugal"),
    ("PH", "Republic of the Philippines"),
    ("RU", "Russia"),
    ("SA", "Saudi Arabia"),
    ("ZA", "South Africa"),
    ("ES", "Spain"),
    ("SE", "Sweden"),
    ("CH", "Switzerland"),
    ("TW", "Taiwan"),
    ("TR", "Turkey"),
    ("GB", "United Kingdom"),
    ("US", "United States"),
)

COUNTRY_CODES = frozenset(code for code, _ in COUNTRIES)


def country_name(code: str) -> str:
    return next((name for value, name in COUNTRIES if value == code), code)
