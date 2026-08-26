from pathlib import Path

from litestar import Litestar
from litestar.di import Provide
from litestar.static_files import create_static_files_router

from server.config import Config
from server.config import load_config
from server.database import Database
from server.routes.health import health
from server.routes.search import index
from server.routes.search import lucky
from server.routes.search import search
from server.routes.settings import remove_key
from server.routes.settings import settings_page
from server.routes.settings import update_key
from server.routes.settings import update_preferences
from server.routes.setup import setup_page
from server.routes.setup import submit_setup
from server.settings_store import SettingsStore

STATIC_DIR = Path(__file__).parent / "static"


def create_app(config: Config | None = None) -> Litestar:
    resolved = config if config is not None else load_config()
    database = Database(path=resolved.database_path)
    database.initialize()
    store = SettingsStore(database=database)

    def provide_store() -> SettingsStore:
        return store

    return Litestar(
        route_handlers=[
            health,
            index,
            search,
            lucky,
            setup_page,
            submit_setup,
            settings_page,
            update_key,
            remove_key,
            update_preferences,
            create_static_files_router(path="/static", directories=[STATIC_DIR], name="static"),
        ],
        dependencies={"store": Provide(provide_store, sync_to_thread=False)},
    )
