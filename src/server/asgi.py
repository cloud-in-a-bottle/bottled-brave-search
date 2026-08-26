from litestar import Litestar

from server.app import create_app

app: Litestar = create_app()
