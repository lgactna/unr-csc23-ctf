# entwistion

This challenge uses Python's `random` module to "encrypt" an image, taking each byte and using it to XOR two images. The plaintext of the first image is given, as well as the ciphertext of the first image and the second image.

`random` implements MT19937 and can be broken with 624 outputs. The challenge, then, becomes determining the inputs that were used to actually XOR the image, then synchronizing the state.

The following should be provided:
- The first plaintext image
- The first ciphertext image (allows the user to XOR the pair of images to determine the outputs of `random.randbytes()` and feed it to a Mersenne Twister solver)
- The second ciphertext image
- The source code (`entwistion.py`)

