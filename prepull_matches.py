from cassiopeia.core import Match
from pathlib import Path
import json
from tqdm import tqdm


def get_data(path):
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    return data["matches"]["seen"], data["matches"]["processed"]


def cached_ids():
    cache = Path('cache/cass')
    matches = set(int(s.name.split('.')[2]) for s in cache.glob('Mat*'))
    return matches


if __name__ == "__main__":
    import cassiopeia
    cassiopeia.apply_settings("settings.json")
    seen, processed = get_data(Path("progress.json"))
    cached = cached_ids()
    to_load = list((set(seen) | set(processed)) - cached)
    for id in tqdm(to_load, ascii=True):
        match = Match(id=id)
        try:
            # Don't worry about exceptions
            x = match.participants
        except Exception:
            pass
