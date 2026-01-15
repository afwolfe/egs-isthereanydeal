import json
from pathlib import Path

import requests

def get_itad_ids(game_titles: list[str]):
    if not game_titles:
        return {}
    
    url = 'https://api.isthereanydeal.com/lookup/id/title/v1'

    response = requests.post(url,json=game_titles)

    response.raise_for_status()
    return response.json()

def transform_library(legendary_path, output_file):
    # Build ITAD skeleton
    itad_format = {
        "version": "03",
        "data": [
            {
                "group": "epicmanualimport",
                "public": False,
                "games": []
            }
        ]
    }
    
    # Load JSONs
    metadata_path = Path(legendary_path) / "metadata"
    if not metadata_path.is_dir():
        raise Exception("Invalid path")
    
    library_files = list(metadata_path.glob("*.json"))
    
    # Get each game's title
    game_titles = []
    for input_file in library_files:
        
        with open(input_file, 'r') as f:
            game = json.load(f)
            
            title = (
                game.get('app_title')
                or game.get('metadata', {}).get('title', '')
                or game.get('metadata', {}).get('description', '')
            )
            game_titles.append(title)
    
    # Lookup ITAD metadata
    title_to_itad_id = get_itad_ids(game_titles)
    for title in title_to_itad_id:
            itad_format['data'][0]['games'].append({
                "id": title_to_itad_id[title],
                "title": title,
                "platforms": 0,
                "playtime": 0
            })

    with open(output_file, 'w') as f:
        json.dump(itad_format, f, indent=2)


if __name__ == '__main__':
    legendary_config_path = Path("~/.config/heroic/legendaryConfig/legendary")
    output_file = 'transformed_legendary_library.json'
    transform_library(legendary_config_path, output_file)
