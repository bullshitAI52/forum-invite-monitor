#!/usr/bin/env python3
"""Generate bounded candidates from 1024RegisterTool-style placeholders."""
from itertools import product

DIGITS = "0123456789"
HEX = "abcdef"


def candidates(template: str, *, max_count: int = 256):
    symbols = {"{i}": DIGITS, "{c}": HEX, "{a}": DIGITS + HEX}
    parts, choices, pos = [], [], 0
    while pos < len(template):
        matches = [(template.find(token, pos), token) for token in symbols]
        matches = [(at, token) for at, token in matches if at >= 0]
        if not matches:
            parts.append(template[pos:])
            break
        at, token = min(matches)
        parts.append(template[pos:at])
        parts.append(None)
        choices.append(symbols[token])
        pos = at + len(token)
    count = 1
    for choice in choices:
        count *= len(choice)
    if count > max_count:
        raise ValueError(f"candidate count {count} exceeds limit {max_count}")
    for values in product(*choices):
        it = iter(values)
        yield "".join(next(it) if part is None else part for part in parts)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("template")
    args = parser.parse_args()
    print("\n".join(candidates(args.template)))
