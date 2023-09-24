import random
from pathlib import Path

import numpy as np

INPUT_FILE_1 = Path("corgi.jpg")
INPUT_FILE_2 = Path("flag.png")

OUTPUT_PATH_1 = Path("corgi.jpg.twist")
OUTPUT_PATH_2 = Path("flag.png.twist")

def entwist(input_file: Path) -> bytes:
    with open(input_file, "rb") as fp:
        pt = np.frombuffer(fp.read(), dtype=np.uint8)

    key = np.frombuffer(random.randbytes(len(pt)), dtype=np.uint8)
    ct = pt ^ key

    assert np.array_equiv(pt, ct ^ key)

    return ct.tobytes()


if __name__ == "__main__":
    # Seed omitted for security
    r = random.seed(SEED)

    with open(OUTPUT_PATH_1, "wb") as fp:
        fp.write(entwist(INPUT_FILE_1))

    with open(OUTPUT_PATH_2, "wb") as fp:
        fp.write(entwist(INPUT_FILE_2))
