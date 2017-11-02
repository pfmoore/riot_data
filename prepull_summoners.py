from cassiopeia.core import Summoner
from pathlib import Path
import json
from tqdm import tqdm


def get_data(path):
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    return data["summoners"]["seen"], data["summoners"]["processed"]


def cached_ids():
    cache = Path('cache/cass')
    summoners = set(int(s.name.split('.')[2]) for s in cache.glob('Sum*'))
    return summoners


if __name__ == "__main__":
    import cassiopeia
    cassiopeia.apply_settings("settings.json")
    seen, processed = get_data(Path("progress.json"))
    cached = cached_ids()
    to_load = list((set(seen) | set(processed)) - cached)
    for id in tqdm(to_load, ascii=True):
        summoner = Summoner(id=id)
        try:
            # Don't worry about exceptions
            x = summoner.name
        except Exception:
            pass
