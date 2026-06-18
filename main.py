from nicegui import ui, app
import os

from searchGames import search_games_router

app.include_router(search_games_router)

@ui.page('/')
def index_page():
    ui.label('Placeholder Login Page')
    ui.link('Go to search games', '/search_games')

# ── run ───────────────────────────────────────────────────────────

ui.run(
    host='0.0.0.0',
    port=int(os.environ.get('PORT', 8080)),
    dark=True,
    title='Casino Config'
)