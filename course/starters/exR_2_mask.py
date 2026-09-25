import re


def mask(text: str) -> str:
    """Replace anything that looks like an API key ("sk-" then at least 10 letters,
    digits or dashes) with "sk-***". Leave a lone "sk-" or "sk-short" alone."""
    # TODO: re.sub(pattern, "sk-***", text)
    raise NotImplementedError


if __name__ == "__main__":
    print(mask("my key is sk-ant-api03-AbC123xyz789 ok?"))   # my key is sk-*** ok?
    print(mask("sk- on its own stays"))
