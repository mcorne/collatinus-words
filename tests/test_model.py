from src.collatinus_words.model import Model
import pytest


@pytest.fixture
def model():
    return Model()


def test_convert_string_to_ascii(model: Model):
    assert model.convert_string_to_ascii("àbc ÀBC_123,;:") == "abc ABC_123,;:"


def test_convert_string_to_number(model: Model):
    assert model.convert_string_to_number("123") == 123
    with pytest.raises(ValueError):
        model.convert_string_to_number("abc")
    with pytest.raises(ValueError):
        model.convert_string_to_number("1.23")


def test_error(model: Model):
    assert model.error("abc") == "abc (line #0)"


def test_parse_constant(model: Model):
    model.constants = {}
    model.parse_constant("$abc=a;b;c")
    assert model.constants["$abc"] == [["a"], ["b"], ["c"]]

    model.parse_constant("$def=d;e;f")
    assert model.constants["$def"] == [["d"], ["e"], ["f"]]


def test_parse_endings(model: Model):
    assert model.parse_endings("a;b;c") == [["a"], ["b"], ["c"]]
    assert model.parse_endings("a;b,c") == [["a"], ["b", "c"]]


def test_parse_line(model: Model):
    model.current_model["unused_inflections"] = []
    model.parse_line("abs:1,2,3")
    assert model.current_model["unused_inflections"] == [1, 2, 3]

    model.parse_line("modele:abc")
    assert "abc" in model.models

    model.current_model["roots"] = {}
    model.parse_line("R:0:-")
    assert model.current_model["roots"][0]["nb_chars_to_remove"] == "-"


def test_parse_lines(model: Model):
    model.constants = {}
    model.parse_lines(["$abc=a;b;c"])
    assert model.constants["$abc"] == [["a"], ["b"], ["c"]]

    model.parse_lines(["modele:abc"])
    assert "abc" in model.models


def test_parse_model(model: Model):
    model.parse_model("abc")
    assert model.current_model["endings"] == {}
    assert model.current_model["mandatory_suffixes"] == {}
    assert model.current_model["optional_suffixes"] == {}
    assert model.current_model["pos"] == {}
    assert model.current_model["roots"] == {}
    assert model.current_model["unused_inflections"] == []
    assert "abc" in model.models


def test_parse_numbers(model: Model):
    assert model.parse_numbers("1,2,3") == [1, 2, 3]
    assert model.parse_numbers("1,2-4, 5") == [1, 2, 3, 4, 5]
    with pytest.raises(AssertionError, match="2--3"):
        model.parse_numbers("1,2--3")


def test_parse_root(model: Model):
    model.current_model["roots"] = {}
    model.parse_root("0", "-")  # R:0:-
    assert model.current_model["roots"][0]["nb_chars_to_remove"] == "-"
    assert model.current_model["roots"][0]["string_to_add"] is None

    model.parse_root("1", "0")  # R:1:0
    assert model.current_model["roots"][1]["nb_chars_to_remove"] == 0
    assert model.current_model["roots"][1]["string_to_add"] is None

    model.parse_root("2", "1,0")  # R:2:0,0
    assert model.current_model["roots"][2]["nb_chars_to_remove"] == 1
    assert model.current_model["roots"][2]["string_to_add"] == "0"

    model.parse_root("3", "2,abc")  # R:3:0,abc
    assert model.current_model["roots"][3]["nb_chars_to_remove"] == 2
    assert model.current_model["roots"][3]["string_to_add"] == "abc"

    model.parse_root("4", "K")  # R:4:K
    assert model.current_model["roots"][4]["nb_chars_to_remove"] == "K"
    assert model.current_model["roots"][4]["string_to_add"] is None


def test_parse_unused_inflections(model: Model):
    model.current_model["unused_inflections"] = []
    model.parse_unused_inflections("1,2,3")
    assert model.current_model["unused_inflections"] == [1, 2, 3]

    model.parse_unused_inflections("4-5")
    assert model.current_model["unused_inflections"] == [1, 2, 3, 4, 5]


def test_read_model(model: Model):
    pytest.skip


def test_split_string(model: Model):
    assert model.split_string("a;b;c", ";") == ["a", "b", "c"]
    assert model.split_string("a;b;c", ";", 3) == ["a", "b", "c"]
    with pytest.raises(AssertionError, match="a;;c"):
        model.split_string("a;;c", ";")


def test_validate_nb_of_pieces(model: Model):
    with pytest.raises(AssertionError, match="abc"):
        model.validate_nb_of_pieces("abc", [1, 2, 3], 999)
