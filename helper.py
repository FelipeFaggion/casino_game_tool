import requests
import pandas as pd
import json
import base64

def get_casino_games(casino_id, casino_host, lobby_token, vertical_group, provider_group, currency):

    base64_message = base64_encode(f"{casino_id}:{lobby_token}")
    vertical_filter = ",".join(vertical_group)
    provider_filter = ",".join(provider_group)

    URL = f"https://{casino_host}/api/lobby/v1/{casino_id}/state"

    HEADERS = {
    "authorization": f"Basic {base64_message}"
    }

    PARAMS = {
    "gameVertical": vertical_filter,
    "currency": currency,
    "gameProvider": provider_filter,
    "exclude": "operationSchedules,dealer,language,videoSnapshot,players,descriptions,gameType,gameVertical,display,results"
    }

    print(HEADERS)
    print(PARAMS)

    OUTPUT_FILE = f"{casino_id}_assigned_games.xlsx"
    RAW_DATA_FILE = "raw_api_data.json"

    # ─── Fetch Data  ───────────────────────────────────────────────────────────────────
    try:
        r = requests.get(URL, params=PARAMS, headers=HEADERS, timeout=30)
        r.raise_for_status()
        raw_json = r.json()
    
        # with open(RAW_DATA_FILE, 'w', encoding='utf-8') as f:
        #         json.dump(raw_json, f, indent=4, ensure_ascii=False)
        # print(f"Raw data for analysis saved in: {RAW_DATA_FILE}")

        fetched_data = r.json()

    except Exception as e:
        print(f"Error in data search: {e}")
        return {}
    
    # ─── Process Data  ───────────────────────────────────────────────────────────────────
    rows = []
    tables = fetched_data.get('tables', {})

    for internal_key, info in tables.items():
        if not isinstance(info, dict):
            continue

        bet_limits = info.get('betLimits', {})
        
        currency_found = ""
        min_bet = None
        max_bet = None
        
        if 'BRL' in bet_limits:
            currency_found = 'BRL'
            min_bet = bet_limits['BRL'].get('min')
            max_bet = bet_limits['BRL'].get('max')
        elif bet_limits:
            currency_found = list(bet_limits.keys())[0]
            limit_data = bet_limits[currency_found]
            if isinstance(limit_data, dict):
                min_bet = limit_data.get('min')
                max_bet = limit_data.get('max')

        sites_list = info.get('sitesAssigned', [])
        sites_str = ", ".join(map(str, sites_list)) if isinstance(sites_list, list) else ""

        row = {
            "Table Name": str(info.get('name', '')).replace('\n', ' ').strip(),
            "Table Id": info.get('tableId'),
            "Virtual Table Id": info.get('virtualTableId') or internal_key,
            "Provider": info.get('gameProvider'),
            "Site Assigned": sites_str,
            "Min Bet": min_bet,
            "Max Bet": max_bet,
            "Currency": currency_found
        }
        rows.append(row)

    processed_rows = rows

    if processed_rows:
        df = pd.DataFrame(processed_rows)
        cols = ["Table Name", "Table Id", "Virtual Table Id", "Provider", "Site Assigned", "Min Bet", "Max Bet", "Currency"]
        df = df[cols]        
        # df.to_excel(OUTPUT_FILE, index=False)
        # print(f"Success! File '{OUTPUT_FILE}' generated with {len(df)} rows.")
        return df
    else:
        print("No data found to process.")

def base64_encode(message):
    message_bytes = message.encode('utf-8')

    base64_bytes = base64.b64encode(message_bytes)

    base64_message = base64_bytes.decode('utf-8')

    return base64_message
