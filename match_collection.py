from cassiopeia.core import Summoner, MatchHistory, Match
from cassiopeia.data import Queue, Patch
from pathlib import Path
import json


class ARAMScanner:
    def __init__(self, patch):
        self.seen_summoners = set()
        self.processed_summoners = set()
        self.seen_matches = set()
        self.processed_matches = set()
        self.patch = patch
        self.match_history = {}


    def load(self, path):
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        self.seen_summoners = set(data["summoners"]["seen"])
        self.processed_summoners = set(data["summoners"]["processed"])
        self.seen_matches = set(data["matches"]["seen"])
        self.processed_matches = set(data["matches"]["processed"])
        self.match_history = data["match_history"]


    def save(self, path):
        data = {
            "summoners": {
                "seen": list(self.seen_summoners),
                "processed": list(self.processed_summoners),
            },
            "matches": {
                "seen": list(self.seen_matches),
                "processed": list(self.processed_matches),
            },
            "match_history": self.match_history,
        }
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f)


    def queue_summoner(self, summoner):
        self.seen_summoners.add(summoner.id)


    def get_match_history(self, id):
        # Try to get the match history from our cache
        # Avoids re-querying the Riot API, as Cass doesn't cache
        # match history because it's volatile - but we don't really
        # care if we're a bit out of date.
        if id in self.match_history:
            return self.match_history[id]

        summoner = Summoner(id=id)
        matches = MatchHistory(summoner=summoner,
                               # begin_time=self.patch.start, end_time=self.patch.end,
                               queues={Queue.aram})
        if matches:
            matches = [m.id for m in matches]
            self.match_history[id] = matches
            return matches


    def process_summoner(self, id=None):
        if id is None:
            id = next(iter(self.seen_summoners))

        new_matches = self.get_match_history(id)
        if new_matches:
            self.seen_matches.update(set(new_matches) - self.processed_matches)
        self.processed_summoners.add(id)
        self.seen_summoners.remove(id)


    def process_match(self, id=None):
        if id is None:
            id = next(iter(self.seen_matches))
        match = Match(id=id)
        participants = {p.summoner.id for p in match.participants}
        self.seen_summoners.update(participants - self.processed_summoners)
        self.processed_matches.add(id)
        self.seen_matches.remove(id)


def crawl_matches(patch):
    scanner = ARAMScanner(patch)
    progress = Path("progress.json")
    if progress.exists():
        scanner.load(progress)
    else:
        scanner.queue_summoner(Summoner(name="GustavEnk"))
        scanner.queue_summoner(Summoner(name="TerrorSlash"))

    while len(scanner.processed_matches) < 1000:
        scanner.process_summoner()
        scanner.process_match()
        scanner.save(progress)


if __name__ == "__main__":
    import cassiopeia
    cassiopeia.apply_settings("settings.json")
    patch_720 = Patch.from_str("7.20")
    crawl_matches(patch_720)
