import argparse
from pathlib import Path

import bitstring

bits = bitstring.BitStream()

def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Creates and verifies .lol files.")
    
    # Access as args.input_file
    parser.add_argument(
        "input_file",
        type=Path,
        help="The file to convert into a .tire file."
    )

    return parser.parse_args()

def main(args: argparse.Namespace) -> None:
    input_file: Path = args.input_file

    with open(input_file, "rb") as fp:
        bits = bitstring.BitStream(fp.read())
    
    print("Before adding zero:")
    bits[:40].pp(width=80)
    
    bits.prepend('0b0')

    print("After adding zero:")
    bits[:40].pp(width=80)

    with open(input_file.with_suffix(input_file.suffix + ".tire"), "wb") as fp:
        # bits.tobytes() converts it to the built-in `bytes` type. It also automatically
        # adds leading zeros, as necessary.
        #
        # bits.tofile() does this, too, against an existing file pointer.
        bits.tofile(fp)

if __name__ == "__main__":
    # Parse arguments
    args = get_args()

    main(args)