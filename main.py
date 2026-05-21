from nicegui import ui
from helper import get_casino_games
import pandas as pd
import tempfile
import json
from pathlib import Path
import os

LOCAL_MODE = os.environ.get('LOCAL_MODE', 'fale').lower() == 'true'

env_option = False
sidebar_open = True
df_tables = pd.DataFrame()

CASINOS_FILE = Path('casinos.json')

ui.add_head_html('''
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
  body { background: #0f1117; font-family: "DM Sans", sans-serif; }

  .sidebar {
    width: 260px;
    min-height: 100vh;
    background: #16181f;
    border-right: 1px solid #2a2d3a;
    transition: width 0.25s ease, opacity 0.25s ease;
    overflow: hidden;
    flex-shrink: 0;
  }
  .sidebar.collapsed { width: 0; opacity: 0; pointer-events: none; }

  .section-label {
    font-family: "DM Mono", monospace;
    font-size: 12px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #ffffff;
    padding: 0 20px;
    margin-bottom: 8px;
  }
  .sidebar-title {
    font-size: 13px;
    font-weight: 500;
    color: #e2e4f0;
    padding: 0 20px;
    margin-bottom: 24px;
    letter-spacing: 0.02em;
  }
  .field-wrapper {
    padding: 0 20px;
    margin-bottom: 20px;
  }
  .field-wrapper .q-field__label {
    font-family: "DM Mono", monospace !important;
    font-size: 10px !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: #4a4f6a !important;
  }
  .field-wrapper .q-field__native {
    font-family: "DM Mono", monospace !important;
    font-size: 13px !important;
    color: #c8cbdf !important;
  }
  .field-wrapper .q-field__bottom { display: none; }
  .field-wrapper .q-field--filled .q-field__control {
    background: #0f1117 !important;
    border-radius: 8px !important;
    border: 1px solid #2a2d3a !important;
  }
  .field-wrapper .q-field--filled.q-field--focused .q-field__control {
    border-color: #5c6bc0 !important;
    background: #0f1117 !important;
  }
  .field-wrapper .q-field__control:before { border: none !important; }
  .field-wrapper .q-field__control:after  { border: none !important; }

  .env-section { padding: 0 20px; margin-bottom: 28px; }
  .env-btn-live   { background: #1a3a2e !important; border: 1px solid #2e7d52 !important; color: #5dcc8a !important; }
  .env-btn-uat    { background: #3a1a1a !important; border: 1px solid #7d2e2e !important; color: #cc5d5d !important; }
  .env-btn-common {
    border-radius: 8px !important;
    font-family: "DM Mono", monospace !important;
    font-size: 12px !important;
    letter-spacing: 0.08em !important;
    font-weight: 500 !important;
    padding: 6px 16px !important;
    box-shadow: none !important;
    transition: filter 0.15s !important;
  }
  .env-btn-common:hover { filter: brightness(1.15); }

  .divider { height: 1px; background: #2a2d3a; margin: 12px 20px 0px; }

  /* ── filter toggle buttons ── */
  .filter-group {
    padding: 0 20px;
    margin-bottom: 20px;
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }

  .filter-chip {
    font-family: "DM Mono", monospace !important;
    font-size: 11px !important;
    letter-spacing: 0.06em !important;
    font-weight: 400 !important;
    padding: 4px 10px !important;
    border-radius: 6px !important;
    box-shadow: none !important;
    transition: all 0.15s ease !important;
    /* default: unselected */
    background: #1e2130 !important;
    border: 1px solid #2a2d3a !important;
    color: #6b7194 !important;
  }
  .filter-chip:hover {
    border-color: #4a4f6a !important;
    color: #9ba3c8 !important;
  }
  .filter-chip.selected {
    background: #1e2545 !important;
    border: 1px solid #4a5fc4 !important;
    color: #8fa4f3 !important;
  }
  .filter-chip.selected:hover {
    filter: brightness(1.1);
  }

  /* ── currency select ── */
  .currency-wrapper {
    padding: 0 20px;
    margin-bottom: 20px;
  }
  .currency-wrapper .q-field__label {
    font-family: "DM Mono", monospace !important;
    font-size: 10px !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: #4a4f6a !important;
  }
  .currency-wrapper .q-field__native,
  .currency-wrapper .q-field__input {
    font-family: "DM Mono", monospace !important;
    font-size: 13px !important;
    color: #c8cbdf !important;
  }
  .currency-wrapper .q-field__bottom { display: none; }
  .currency-wrapper .q-field--filled .q-field__control {
    background: #0f1117 !important;
    border-radius: 8px !important;
    border: 1px solid #2a2d3a !important;
  }
  .currency-wrapper .q-field--filled.q-field--focused .q-field__control {
    border-color: #5c6bc0 !important;
  }
  .currency-wrapper .q-field__control:before { border: none !important; }
  .currency-wrapper .q-field__control:after  { border: none !important; }
  .currency-wrapper .q-select__dropdown-icon { color: #4a4f6a !important; }

  /* ── dataframe download btn ── */            
  .download-btn {
    font-family: "DM Mono", monospace !important;
    font-size: 11px !important;
    background: #1e2130 !important;
    border: 1px solid #2a2d3a !important;
    color: #8890b0 !important;
    border-radius: 7px !important;
    box-shadow: none !important;
    }

  download-btn:hover {
    border-color: #4a5fc4 !important;
    color: #8fa4f3 !important;
    }

    /* ── main area ── */
    .main-wrapper {
        max-width: 1450px;
        margin: 0 auto;
        padding: 48px 40px 40px;
        width: 100%;
        box-sizing: border-box;
    }
    .main-header {
        margin-bottom: 20px;
    }
    .main-title {
        font-size: 20px;
        font-weight: 500;
        color: #e2e4f0;
        letter-spacing: 0.01em;
        margin: 0 0 4px 0;
    }
    .main-subtitle {
        font-family: "DM Mono", monospace;
        font-size: 11px;
        color: #4a4f6a;
        letter-spacing: 0.06em;
    }
    .table-footer {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-top: 12px;
    }
    .row-count {
        font-family: "DM Mono", monospace;
        font-size: 11px;
        color: #34b926;
        letter-spacing: 0.06em;
    }
    .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 16px;
        padding: 80px 0;
    }
    .empty-title {
        font-size: 18px;
        font-weight: 500;
        color: #6a6f85;
        letter-spacing: 0.01em;
    }
    .empty-hint {
        font-family: "DM Mono", monospace;
        font-size: 11px;
        color: #6a6f85;
        letter-spacing: 0.06em;
    }

</style>
''')

# ── env button ───────────────────────────────────────────────────────────────
# class BetterEnvButton(ui.button):
#     def __init__(self, *args, **kwargs):
#         self._state = False
#         super().__init__(*args, **kwargs)
#         self.classes('env-btn-common env-btn-uat')
#         self.props('flat no-caps unelevated')
#         self.on('click', self.toggle)

#     def toggle(self):
#         self._state = not self._state
#         self.update()

#     def update(self):
#         global env_option
#         env_option = self._state
#         self.set_text('LIVE 1' if self._state else 'UAT 1')
#         if self._state:
#             self.classes(remove='env-btn-uat', add='env-btn-live')
#         else:
#             self.classes(remove='env-btn-live', add='env-btn-uat')
#         super().update()


# ── saved casino settings ───────────────────────────────────────────────────────────────

def load_casinos() -> list[dict]:
    if not CASINOS_FILE.exists():
        return []
    return json.loads(CASINOS_FILE.read_text())

def save_casino(label: str, cid: str, token: str, host: str):
    casinos = load_casinos()
    for c in casinos:
        if c['label'] == label:
            c.update({'casino_id': cid, 'token': token, 'hostname': host})
            break
    else:
        casinos.append({'label': label, 'casino_id': cid, 'token': token, 'hostname': host})
    CASINOS_FILE.write_text(json.dumps(casinos, indent=2))


# ── filter toggle chip ───────────────────────────────────────────────────────
class FilterChip(ui.button):
    """
    Toggle button for filter selection.

    Args:
        label:      display text
        group:      ToggleGroup this chip belongs to
    """
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
    """
    Manages a set of FilterChips.

    Args:
        multi:      True  → multiple chips can be selected (e.g. providers)
                    False → only one chip active at a time (e.g. vertical)
        on_change:  optional callback(selected: list[str])
    """
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
        ui.spinner(size='lg').style('margin: 40px auto; display:block;')

    df_tables = get_casino_games(casino_id.value, casino_host.value, lobby_token.value, vertical_group.selected, 
                     provider_group.selected, currency.value)
    
    main_area.clear()
    with main_area:
        render_table(df_tables)  

def render_empty():
    with ui.element('div').classes('main-wrapper'):
        with ui.element('div').classes('empty-state'):
            ui.icon('manage_search').style('font-size:52px; color:#6a6f85;')
            ui.label('Search for Games').classes('empty-title')
            ui.label('configure filters and hit get games').classes('empty-hint')

def render_table(df: pd.DataFrame):
    if df.empty:
        with ui.element('div').classes('main-wrapper'):
            with ui.element('div').classes('empty-state'):
                ui.icon('inbox').style('font-size:52px; color:#6a6f85;')
                ui.label('No results found').classes('empty-title')
                ui.label('try adjusting your filters').classes('empty-hint')
        return

    with ui.element('div').classes('main-wrapper'):
        # header
        with ui.element('div').classes('main-header'):
            ui.element('div').classes('main-title').style('font-size:20px; font-weight:500; color:#e2e4f0;') \
                .text = 'Casino Assigned Games'
            ui.label('Casino Assigned Games').style(
                'font-size:20px; font-weight:500; color:#e2e4f0; margin-bottom:4px; display:block;')
            ui.label(f'{casino_id.value}  ·  {casino_host.value}').style(
                'font-family:"DM Mono",monospace; font-size:11px; color:#757eb1; letter-spacing:0.06em;')

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
        # ui.label('CONFIGURATION').classes('section-label').style(
        #     "border-bottom: 2px solid #ff5722; display: inline-block;")
        # ui.label('Casino Settings').classes('sidebar-title')

        # ui.label('ENVIRONMENT').classes('section-label')
        # with ui.element('div').classes('env-section'):
        #     BetterEnvButton('UAT 1')

        # ── dropdown and user input ───────────────────────────────────────────────────────────────────
        ui.label('CONNECTION').classes('section-label').style(
            "border-bottom: 2px solid #e0e020; display: inline-block;")
        
        casinos = load_casinos()
        preset_options = [c['label'] for c in casinos]

        def on_preset_select(e):
            selected = next((c for c in load_casinos() if c['label'] == e.value), None)
            if selected:
                casino_id.set_value(selected['casino_id'])
                lobby_token.set_value(selected['token'])
                casino_host.set_value(selected['hostname'])

        if LOCAL_MODE:
            with ui.element('div').classes('currency-wrapper'):
                preset_select = ui.select(
                    options=preset_options,
                    label='Load saved casino',
                    on_change=on_preset_select,
                ).props('filled dense options-dark clearable')

            with ui.element('div').classes('field-wrapper'):
                casino_name_input = ui.input('Save as...', value='').props('filled dense')

        with ui.element('div').classes('field-wrapper'):
            casino_id = ui.input('Casino ID', value='').props('filled dense')
        with ui.element('div').classes('field-wrapper'):
            lobby_token = ui.input('State API Token', value='').props('filled dense')
        with ui.element('div').classes('field-wrapper'):
            casino_host = ui.input('Hostname', value='').props('filled dense')

        if LOCAL_MODE:
            def on_save():
                label = casino_name_input.value.strip()
                if not label:
                    ui.notify('Fill in "Save as..." first.', color='negative')
                    return
                try:
                    save_casino(label, casino_id.value, lobby_token.value, casino_host.value)

                    new_options = [c['label'] for c in load_casinos()]
                    preset_select.options = new_options
                    preset_select.update()
                    ui.notify(f'"{label}" saved.', color='positive')
                except Exception as e:
                    ui.notify(f'Error saving: {e}', color='negative')

            with ui.element('div').classes('env-section'):
                ui.button('Save', icon='save', on_click=on_save) \
                    .classes('env-btn-common') \
                    .props('flat no-caps unelevated')

        # ── filter options ───────────────────────────────────────────────────────────────────

        ui.element('div').classes('divider')

        ui.label('Game Vertical').classes('section-label').style('margin-top:8px; margin-bottom:6px; border-bottom: 2px solid #22ff51; display: inline-block;')
        with ui.element('div').classes('filter-group'):
            for v in ['live', 'instant', 'rng', 'slots']:
                vertical_group.add(v)

        ui.label('Game Provider').classes('section-label').style('margin-top:4px; margin-bottom:6px; border-bottom: 2px solid #226eff; display: inline-block;')
        with ui.element('div').classes('filter-group'):
            for p in ['evolution', 'redtiger', 'netent', 'btg', 'nlc',
                      'extendednetent', 'ezugi', 'taparoo', 'sneakyslots', 'spinningwhale']:
                provider_group.add(p)

        ui.label('Currency').classes('section-label').style('margin-top:4px; margin-bottom:6px; border-bottom: 2px solid #7f13c2; display: inline-block;')
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
    main_area = ui.element('div').classes('flex-1').style('background:#0f1117;')
    with main_area:
        render_empty()
        
# ── sidebar toggle ───────────────────────────────────────────────────────────
icon_state = {'open': True}

toggle_icon = ui.icon('menu').style(
    'position:absolute; top:18px; left:18px; z-index:100; '
    'color:#8890b0; cursor:pointer; font-size:20px; '
    'background:#1e2130; border:1px solid #2a2d3a; '
    'border-radius:8px; padding:8px; transition:background 0.15s;'
)

def toggle_sidebar():
    icon_state['open'] = not icon_state['open']
    if icon_state['open']:
        sidebar.classes(remove='collapsed')
    else:
        sidebar.classes(add='collapsed')

toggle_icon.on('click', toggle_sidebar)

ui.run(
    host='0.0.0.0',
    port=int(os.environ.get('PORT', 8080)),
    dark=True,
    title='Casino Config'
)