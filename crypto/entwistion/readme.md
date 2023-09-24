# entwistion

*I'm so sure you can't break this, I'll even give you the source code and some plaintext.*

This challenge uses Python's `random` module to "encrypt" an image, taking each byte and using it to XOR two images. The plaintext of the first image is given, as well as the ciphertext of the first image and the second image.

`random` implements MT19937 and can be broken with 624 outputs. The challenge, then, becomes determining the inputs that were used to actually XOR the image, then synchronizing the state.

The following should be provided:
- The first plaintext image
- The first ciphertext image (allows the user to XOR the pair of images to determine the outputs of `random.randbytes()` and feed it to a Mersenne Twister solver)
- The second ciphertext image (contains the flag)
- The source code with comments removed (`entwistion.py`)

The picture of a dorgi is from this article about Queen Elizabeth's dogs: https://www.chinookobserver.com/opinion/columns/coast-chronicles-long-live-the-values-of-a-long-lived-queen/article_a06ba83e-3296-11ed-97cd-7727cd4828b1.html

The picture of a corgi *might* be from https://iheartdogs.com/7-strategies-to-stop-your-corgis-resource-guarding/ (that's where I found it on Google Images), but there's a lot of similar pictures, too.

