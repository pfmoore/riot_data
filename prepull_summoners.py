from cassiopeia.core import Summoner
from pathlib import Path
import json


def get_data(path):
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    return data["summoners"]["seen"], data["summoners"]["processed"]


if __name__ == "__main__":
    import cassiopeia
    cassiopeia.apply_settings("settings.json")
    seen, processed = get_data(Path("progress.json"))
    for id in seen:
        summoner = Summoner(id=id)
        print(summoner.name)
