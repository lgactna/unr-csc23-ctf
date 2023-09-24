"""
This is the "developer's" version of entwistion, with comments attached.

Distribute this file with comments and the seed removed.
"""

import random
from pathlib import Path

import numpy as np

INPUT_FILE_1 = Path("corgi.jpg")
INPUT_FILE_2 = Path("flag.png")

OUTPUT_PATH_1 = Path("corgi.jpg.twist")
OUTPUT_PATH_2 = Path("flag.png.twist")

SEED = "{$(R4'c&Mn}V[~QL=zXm(qeW@'D-SXv."


def entwist(input_file: Path) -> bytes:
    """
    Encrypt a file.

    Assumes that `random` has already been initialized appropriately.
    """

    with open(input_file, "rb") as fp:
        # Each "output" of the Mersenne Twister is 32 bits. But to avoid having
        # to manually pad out the last few bytes, we will read it in as a series
        # of uint8s instead. Accordingly, we'll need to generate a key that's
        # a series of uint8s, but to recover the state later, we'll need to
        # turn it back into 32-bit sequences.
        pt = np.frombuffer(fp.read(), dtype=np.uint8)

    # We need at least 2,496 bytes of data (624 32-bit sequences) to recover the
    # state in full. It's possible to make a guess with less, but we shouldn't
    # need to deal with this. The second file can be whatever; it's just that the
    # user needs to know 624 outputs from `random` as-is.
    #
    # REMOVE THIS when distributing the source code.
    if len(pt) < 2496:
        print("Plaintext is shorter than 2,496 bytes")

    # Pull a number of 8-bit outputs equal in length to the file itself
    key = np.frombuffer(random.randbytes(len(pt)), dtype=np.uint8)

    # XOR the two together, effectively "encrypting" it - but since we can predict
    # the output of the Mersenne Twister given enough information, this isn't
    # cryptographically secure.
    #
    # Even if we didn't give the user a plaintext and ciphertext to get them to
    # the correct state, it would still very much be possible to analyze the ciphertext
    # in other ways to deduce *enough* of the state to break it.
    #
    # Also, we're using numpy because it's probably a little faster, and the syntax
    # is a little nicer.
    ct = pt ^ key

    # XOR'ing the ciphertext with the key better yield the plaintext again. If it
    # doesn't, something's wrong lol
    assert np.array_equiv(pt, ct ^ key)

    # Return as a regular `bytes` object
    return ct.tobytes()


if __name__ == "__main__":
    # If seed is None, the current time is used.
    r = random.seed(SEED)

    # The state *should* be shared between these two.
    with open(OUTPUT_PATH_1, "wb") as fp:
        fp.write(entwist(INPUT_FILE_1))

    with open(OUTPUT_PATH_2, "wb") as fp:
        fp.write(entwist(INPUT_FILE_2))
