import unicodedata
from pathlib import Path


class Common:
    def read_model(self, file):
        path = Path(__file__).parent.joinpath(file)
        with path.open(encoding="utf-8") as f:
            lines = unicodedata.normalize("NFC", f.read()).split("\n")
            return lines
