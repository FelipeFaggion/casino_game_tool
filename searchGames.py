from nicegui import ui, APIRouter
from helper import get_casino_games
import pandas as pd
import tempfile

search_games_router = APIRouter()

@search_games_router.page('/search_games')
def search_games():
    df_tables = pd.DataFrame()

    ui.add_css("searchGames.css")

    # ── filter toggle chip ───────────────────────────────────────────────────────
    class FilterChip(ui.button):

        def __init__(self, label: str, group: 'ToggleGroup') -> None:
            super().__init__(label)
            self._selected = False
            self._group = group
            self.classes('filter-chip')
            self.props('flat no-caps unelevated dense')
            self.on('click', self._handle_click)

        def _handle_click(self):
            if self._group.multi:
                # multi: just flip this chip
                self.set_selected(not self._selected)
            else:
                # single: deselect all others, select this
                for chip in self._group.chips:
                    chip.set_selected(False)
                self.set_selected(True)
            self._group._notify()

        def set_selected(self, value: bool):
            self._selected = value
            if value:
                self.classes(add='selected')
            else:
                self.classes(remove='selected')
            self.update()

        @property
        def value(self) -> str:
            return self.text


    class ToggleGroup:

        def __init__(self, multi: bool = True, on_change=None):
            self.multi = multi
            self.chips: list[FilterChip] = []
            self._on_change = on_change

        def add(self, label: str) -> FilterChip:
            chip = FilterChip(label, group=self)
            self.chips.append(chip)
            return chip

        def _notify(self):
            if self._on_change:
                self._on_change(self.selected)

        @property
        def selected(self) -> list[str]:
            return [c.value for c in self.chips if c._selected]


    # ── get games and render dataframe on ui ───────────────────────────────────────────────────────────
    vertical_group  = ToggleGroup(multi=True)
    provider_group  = ToggleGroup(multi=True)

    def get_games():
        global df_tables

        main_area.clear()
        with main_area:
            ui.spinner(size='lg').classes('spinner')

        df_tables = get_casino_games(casino_id.value, casino_host.value, lobby_token.value, vertical_group.selected, 
                        provider_group.selected, currency.value)
        
        main_area.clear()
        with main_area:
            render_table(df_tables)  

    def render_table(df: pd.DataFrame):
        if df.empty:
            with ui.element('div').classes('main-wrapper'):
                with ui.element('div').classes('empty-state'):
                    ui.icon('inbox').classes('empty-search')
                    ui.label('No results found').classes('empty-title')
                    ui.label('try adjusting your filters').classes('empty-hint')
            return

        with ui.element('div').classes('main-wrapper'):
            # header
            with ui.element('div').classes('main-header'):
                ui.element('div').classes('main-title').classes('results-title') \
                    .text = 'Casino Assigned Games'
                ui.label('Casino Assigned Games').classes('results-title assigned-games-title')
                ui.label(f'{casino_id.value} · {casino_host.value}').classes('results-display')

            col_defs = [{'field': c, 'resizable': True, 'minWidth': 120} for c in df.columns]
            ui.aggrid({
                'columnDefs': col_defs,
                'rowData': df.fillna('').to_dict('records'),
                'defaultColDef': {'sortable': True, 'filter': True},
            }).classes('ag-theme-alpine-dark').style('height: calc(90vh - 180px); width:100%;')

            # footer
            with ui.row().classes('table-footer'):
                ui.label(f'Total rows: {len(df)}').classes('row-count')

                def download():
                    tmp = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
                    df.to_excel(tmp.name, index=False)
                    tmp.close()
                    ui.download(tmp.name, filename='casino_assigned_games.xlsx')

                ui.button('Download .xlsx', icon='download', on_click=download) \
                    .classes('download-btn').props('flat no-caps unelevated')

    # ── layout ───────────────────────────────────────────────────────────────────

    ui.query('.nicegui-content').classes('p-0') #override initial padding

    with ui.row().classes('w-full').style('gap:0; min-height:100vh;'):

        sidebar = ui.column().classes('sidebar').style('padding: 72px 0 24px; gap:0;')

        with sidebar:
            # ── dropdown and user input ───────────────────────────────────────────────────────────────────
            ui.label('CONNECTION').classes('section-label').style(
                "border-bottom: 2px solid #e0e020; display: inline-block;")

            with ui.element('div').classes('field-wrapper'):
                casino_id = ui.input('Casino ID', value='').props('filled dense')
            with ui.element('div').classes('field-wrapper'):
                lobby_token = ui.input('State API Token', value='').props('filled dense')
            with ui.element('div').classes('field-wrapper'):
                casino_host = ui.input('Hostname', value='').props('filled dense')

            # ── filter options ───────────────────────────────────────────────────────────────────

            ui.element('div').classes('divider')

            ui.label('Game Vertical').classes('section-label standard-label game-vertical-label')
            with ui.element('div').classes('filter-group'):
                for v in ['live', 'instant', 'rng', 'slots']:
                    vertical_group.add(v)

            ui.label('Game Provider').classes('section-label standard-label game-provider-label')
            with ui.element('div').classes('filter-group'):
                for p in ['evolution', 'redtiger', 'netent', 'btg', 'nlc',
                        'extendednetent', 'ezugi', 'taparoo', 'sneakyslots', 'spinningwhale']:
                    provider_group.add(p)

            ui.label('Currency').classes('section-label standard-label currency-label')
            with ui.element('div').classes('currency-wrapper'):
                currency = ui.select(
                    options=['USD', 'EUR', 'BRL'],
                    value='USD',
                    label='Currency',
                ).props('filled dense options-dark')

            ui.element('div').classes('divider')
            with ui.element('div').classes('env-section'):
                ui.button('Get Games', on_click=get_games).classes('env-btn-common')

        # ──main area ───────────────────────────────────────────────────────────────────
        main_area = ui.element('div').classes('flex-1 main-area-background')
        with main_area:
            render_table(df_tables)
            
    # ── sidebar toggle ───────────────────────────────────────────────────────────
    icon_state = {'open': True}

    toggle_icon = ui.icon('menu').classes('toggle-icon')

    def toggle_sidebar():
        icon_state['open'] = not icon_state['open']
        if icon_state['open']:
            sidebar.classes(remove='collapsed')
        else:
            sidebar.classes(add='collapsed')

    toggle_icon.on('click', toggle_sidebar)
