# bottled-brave-search

A web search app for [OpenHost](https://github.com/imbue-openhost/openhost), backed by the
[Brave Search API](https://brave.com/search/api/) and styled to look like Google's results page.

- **All / Images / News** tabs, backed by Brave's `/web/search`, `/images/search` and `/news/search` endpoints.
- Google-style SERP: result column with favicon + breadcrumb source rows, knowledge panel, Top stories,
  People also ask, Discussions and forums, time filters under **Tools**, and the coloured page pager.
- Light and dark themes, following the browser's `prefers-color-scheme`.
- "I'm Feeling Lucky" redirects to the top result.

The app is login-gated by the OpenHost router — `openhost.toml` declares no `public_paths`, so only the
instance owner can reach it.

## First boot

The app has no API key of its own. On first load it redirects to `/setup`, which walks through creating a
Brave Search API account, picking a plan, and generating a key. The key is verified with a single live
query before being written to the app's OpenHost-provisioned SQLite database (`OPENHOST_SQLITE_MAIN`); it
never leaves the instance. `/settings` can replace or remove it later, and holds the SafeSearch and region
preferences.

Brave's free "Data for Search" plan allows 2,000 queries a month at one query per second, and requires a
card on file for identity verification. Image and news results need a plan that covers those endpoints.

## Development

```bash
just setup   # install deps, pre-commit hooks, and the playwright chromium browser
just run     # run locally on http://localhost:8080 (writes to .local/main.db)
just test    # run the test suite
just check   # lint, format, typecheck
```

Python work uses [uv](https://docs.astral.sh/uv/). Use `uv add <pkg>` to add a dependency and
`uv add --group dev <pkg>` for a dev-only one.

### Tests

`just test` has two layers:

- **In-process tests** (`test_search.py`, `test_setup_flow.py`, `test_html_helpers.py`) run the Litestar app
  against `tests/brave_stub.py`, a local HTTP server that serves the recorded Brave payloads in
  `tests/fixtures/` and generates placeholder images. `BRAVE_API_BASE_URL` points the client at it.
- **Containerized tests** (`test_app.py`) use the OpenHost test harness, which builds the Dockerfile, runs
  the app under **podman** per `openhost.toml`, and fronts it with the real OpenHost router. Podman must be
  running. The harness can't inject env vars into the container, so these cover boot, auth-gating and static
  assets rather than search itself.

To see the real UI locally without a Brave key, run the stub and point the app at it:

```bash
uv run python -c "import time; from tests.brave_stub import run_brave_stub; \
  (lambda s: (print(s.base_url, flush=True), time.sleep(3600)))(run_brave_stub().__enter__())"
OPENHOST_SQLITE_MAIN=.local/main.db BRAVE_API_BASE_URL=<printed url> \
  uv run hypercorn server.asgi:app --bind 127.0.0.1:8080
```

## Layout

```
src/server/
  app.py              Litestar app factory; asgi.py is the entrypoint
  config.py           env-derived config (OPENHOST_SQLITE_MAIN)
  database.py         sqlite settings table
  settings_store.py   typed accessors for the API key + preferences
  search_params.py    query/tab/page/freshness parsing
  countries.py        the region codes Brave accepts
  brave/              API client, response models, JSON parsing, error mapping
  routes/             health, search, setup, settings
  views/              HTML rendering, one module per page or SERP block
  static/             style.css, app.js, favicon.svg
```

Pages are rendered server-side as HTML strings; `views/html.py` holds the escaping helpers. Brave's snippet
text arrives with `<strong>` markup around matched terms, so `sanitize_markup` escapes everything and then
restores just those tags, and `safe_url` neutralises non-http(s) URLs before they reach an `href` or `src`.
