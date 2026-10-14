"""Run the default Python PRACH Zadoff-Chu baseline example."""

from python.prach_reference import generate_preambles


def main() -> None:
    preambles = generate_preambles()
    print(f"Generated {len(preambles)} preambles")
    print(
        f"First preamble: root={preambles[0].root_index}, "
        f"shift={preambles[0].cyclic_shift}"
    )
    print(
        f"Last preamble: root={preambles[-1].root_index}, "
        f"shift={preambles[-1].cyclic_shift}"
    )


if __name__ == "__main__":
    main()
