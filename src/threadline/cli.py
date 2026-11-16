import argparse


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="threadline")
    parser.parse_args(argv)
    return 0
