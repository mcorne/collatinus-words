from model import Model

if __name__ == "__main__":
    """python collatinus_words/cli.py"""
    try:
        model = Model()
        model.read_model()
    except Exception as e:
        if hasattr(e, "message"):
            print(e.message)
        else:
            print(e)
