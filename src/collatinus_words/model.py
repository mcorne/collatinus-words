import unicodedata
from pathlib import Path


class Model:
    constants = {}
    current_model = {}
    line_number = 0
    models = {}

    def convert_string_to_ascii(self, string):
        decomposed = unicodedata.normalize("NFKD", string)
        ascii = decomposed.encode("ASCII", "ignore").decode()
        return ascii

    def convert_string_to_number(self, string):
        try:
            return int(string)
        except ValueError:
            raise ValueError(self.error(f"Invalid number {string}"))

    def error(self, error_message):
        error_message += f" (line #{self.line_number})"
        return error_message

    def parse_constants(self, line):
        constant, endings = self.split_string(line, "=", 2)
        self.constants[constant] = self.parse_endings(endings)

    def parse_endings(self, string):
        endings = self.split_string(string, ";")
        endings = [self.split_string(ending, ",") for ending in endings]
        # TODO: check endings contain only letters with str.isalpha(), including a possible digit at the very end for "des"
        return endings

    def parse_line(self, line):
        pieces = self.split_string(line, ":")
        line_type = pieces[0]
        del pieces[0]

        if line_type == "abs":
            self.validate_nb_of_pieces(line, pieces, 1)
            self.parse_unused_inflections(unused_inflections=pieces[0])
        elif line_type == "modele":
            self.validate_nb_of_pieces(line, pieces, 1)
            self.parse_model(model=pieces[0])
        elif line_type == "R":
            self.validate_nb_of_pieces(line, pieces, 2)
            self.parse_root(root=pieces[0], fix=pieces[1])
        else:
            pass
            # TODO: throw exception

    def parse_lines(self, lines):
        for line in lines:
            self.line_number += 1
            line = line.replace(" ", "").strip()  # remove spaces
            if line == "" or line[0] == "!":
                pass  # ignore empty lines and comments
            elif line[0] == "$":
                self.parse_constants(line)
            else:
                self.parse_line(line)

    def parse_model(self, model):
        self.current_model = {
            "endings": {},  # des (désinences)
            "mandatory_suffixes": {},  # sufd (suffixes désinences), eg quī+dăm, quēm+dăm etc.
            "optional_suffixes": {},  # suf (suffixes), eg 	hīc+ĕ, hīc+ĭnĕ or hīc
            "pos": {},  # part of speech
            "roots": {},  # R (radicaux)
            "unused_inflections": [],  # abs (désinences absentes)
        }
        self.models[model] = self.current_model

    def parse_numbers(self, string):
        numbers = []
        ranges = [
            self.split_string(range, "-") for range in self.split_string(string, ",")
        ]
        for myrange in ranges:
            assert len(myrange) <= 2, self.error(f"Invalid number range in {string}")
            start = self.convert_string_to_number(myrange[0])
            if len(myrange) == 1:
                numbers.append(start)  # single number
            else:
                stop = self.convert_string_to_number(myrange[1])  # number range
                numbers += [*range(start, stop + 1)]
        # TODO: check numbers correspond to an entry in morphos.la
        return numbers

    def parse_root(self, root, fix):
        root = self.convert_string_to_number(root)
        fix = self.split_string(fix, ",")
        nb_chars_to_remove = fix[0]
        if nb_chars_to_remove != "-" and nb_chars_to_remove != "K":
            nb_chars_to_remove = self.convert_string_to_number(nb_chars_to_remove)
        string_to_add = None if len(fix) == 1 else fix[1]
        self.current_model["roots"][root] = {
            "nb_chars_to_remove": nb_chars_to_remove,
            "string_to_add": string_to_add,  # TODO: validate letters
        }

    def parse_unused_inflections(self, unused_inflections):
        numbers = self.parse_numbers(unused_inflections)
        self.current_model["unused_inflections"] += numbers

    def read_model(self):
        path = Path(__file__).parent.joinpath("data/modeles.la")
        with path.open(encoding="utf-8") as f:
            lines = unicodedata.normalize("NFC", f.read()).split("\n")
            self.parse_lines(lines)

    def split_string(self, string, separator, expected_nb_pieces=None):
        pieces = [piece.strip() for piece in string.split(separator)]
        if expected_nb_pieces:
            self.validate_nb_of_pieces(string, pieces, expected_nb_pieces)
        for piece in pieces:
            assert piece != "", self.error(f"Empty substring in split string {string}")
        return pieces

    def validate_nb_of_pieces(self, string, pieces, expected_nb_pieces):
        assert len(pieces) == expected_nb_pieces, self.error(
            f"Unexpected number of substrings in string split by : (colon) {string}"
        )
