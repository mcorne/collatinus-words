from model import Model

if __name__ == "__main__":
    """python collatinus_words/cli.py"""
    try:
        model = Model()
        lines = model.read_model("data/modeles.la")
        model.parse_lines(lines)
    except Exception as e:
        if hasattr(e, "message"):
            print(e.message)
        else:
            print(e)
