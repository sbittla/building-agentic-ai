import re


def citations(text: str) -> list[tuple[str, int]]:
    """Every "(file:line)" citation as (file, line_number) pairs. The file part may
    contain folders, dots and dashes: "(work/2026-06-02-incident.md:3)".
    Ignore things like "(see page 12)" or "(12:30)"."""
    # TODO: a capture group for the path and one for the digits
    raise NotImplementedError


if __name__ == "__main__":
    print(citations("Lag spiked (work/incident-kafka.md:3) but not (see page 12)."))
