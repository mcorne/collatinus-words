import unicodedata
from pathlib import Path


class Model:
    constants = {}
    current_model = {}
    models = {}

    def convert_string_to_ascii(self, string):
        decomposed = unicodedata.normalize("NFKD", string)
        ascii = decomposed.encode("ASCII", "ignore").decode()
        return ascii

    def normalize_string(self, string):
        normalized = unicodedata.normalize("NFC", string)
        return normalized

    def parse_constants(self, line):
        constant, endings = line.split("=")
        endings = endings.split(";")
        endings = [ending.split(",") for ending in endings]
        self.constants[constant] = endings

    def parse_line(self, line):
        pieces = line.split(":")
        line_type = pieces[0]
        del pieces[-1]

        if line_type == "modele":
            self.current_model = {
                "abs": {},
                "des": {},
                "pos": {},
                "R": {},
                "suf": {},
                "sufd": {},
            }
            self.models[line_type] = self.current_model
        elif line_type == "R":
            self.parse_R(pieces)

    def parse_lines(self, lines):
        for line in lines:
            line = line.replace(" ", "")  # remove spaces
            if line == "" or line[0] == "!":  # comment
                continue
            if line[0] == "$":
                self.parse_constants(line)
                continue
            self.parse_line(line)

    def parse_R(self, pieces):
        root = pieces[0]
        parts = pieces[1].split(",")
        self.current_model["R"][root] = {
            "nb_chars_to_remove": parts[0],
            "string_to_add": None if len(parts) == 1 else parts[1],
        }

    def read_model(self):
        path = Path(__file__).parent.joinpath("data/modeles.la")
        with path.open(encoding="utf-8") as f:
            lines = self.normalize_string(f.read()).split("\n")
            self.parse_lines(lines)


model = Model()
model.read_model()
