import attr

from server.database import Database

_API_KEY = "brave_api_key"
_SAFESEARCH = "safesearch"
_COUNTRY = "country"

SAFESEARCH_CHOICES = ("off", "moderate", "strict")
DEFAULT_SAFESEARCH = "moderate"
# Brave treats "ALL" as "no country targeting".
DEFAULT_COUNTRY = "ALL"


@attr.s(auto_attribs=True, frozen=True)
class AppSettings:
    brave_api_key: str | None
    safesearch: str
    country: str

    @property
    def is_configured(self) -> bool:
        return self.brave_api_key is not None


@attr.s(auto_attribs=True, frozen=True)
class SettingsStore:
    database: Database

    def load(self) -> AppSettings:
        safesearch = self.database.get(_SAFESEARCH)
        return AppSettings(
            brave_api_key=self.database.get(_API_KEY),
            safesearch=safesearch if safesearch in SAFESEARCH_CHOICES else DEFAULT_SAFESEARCH,
            country=self.database.get(_COUNTRY) or DEFAULT_COUNTRY,
        )

    def save_api_key(self, api_key: str) -> None:
        self.database.set(_API_KEY, api_key.strip())

    def clear_api_key(self) -> None:
        self.database.delete(_API_KEY)

    def save_preferences(self, safesearch: str, country: str) -> None:
        if safesearch not in SAFESEARCH_CHOICES:
            raise ValueError(f"unknown safesearch value {safesearch!r}")
        self.database.set(_SAFESEARCH, safesearch)
        self.database.set(_COUNTRY, country.strip().upper() or DEFAULT_COUNTRY)
