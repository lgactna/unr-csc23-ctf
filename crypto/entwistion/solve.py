import numpy as np

# From https://github.com/icemonster/symbolic_mersenne_cracker/blob/main/main.py
from stt import Untwister

PT_FILE_1 = "corgi.jpg"
CT_FILE_1 = "corgi.jpg.twist"

CT_FILE_2 = "flag.png.twist"

FLAG_PATH = "flag_solved.png"

def main() -> None:
    with open(PT_FILE_1, "rb") as fp:
        pt_1 = np.frombuffer(fp.read(), dtype=np.uint8)

    with open(CT_FILE_1, "rb") as fp:
        ct_1 = np.frombuffer(fp.read(), dtype=np.uint8)

    with open(CT_FILE_2, "rb") as fp:
        ct_2 = np.frombuffer(fp.read(), dtype=np.uint8)

    # Start off by deriving the key by simply XOR'ing the ciphertext against
    # the plaintext - get it back as `bytes`
    key_1 = (pt_1 ^ ct_1).tobytes()

    # Submit the first 624 instances of 32-bit results to the Z3 solver as strings
    # of 1s and 0s
    ut = Untwister()
    for i in range(624):
        # This should be little endian
        observation = int.from_bytes(key_1[(i*4):(i*4)+4], "little")
        ut.submit(bin(observation)[2:])

    # Solve and clone state (hopefully - if this raises an error we've done
    # something wrong)
    r = ut.get_random()
    print("done solving")

    # For the remainder of the file, make sure that we're getting the same
    # outputs as the random number generator
    for i in range(624*4, len(key_1)):
        assert r.randbytes(1) == key_1[i]


if __name__ == "__main__":
    main()