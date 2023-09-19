"""
Introducing the linked object list (.lol) format.

A .lol file consists of three sections:
- The length of the reconstructed file, as an 8-byte BE unsigned integer.
- The MD5 hash of the reconstructed file, as a checksum.
- A sequence of variable-length chunks, described below.

A "chunk" itself consists of three sections:
- The length of the data part of the chunk, as a 4-byte BE unsigned integer
(that is, it excludes the length and the pointer at the end of the chunk).
- The data contained in the chunk.
- A pointer to the next chunk to read, expressed as an 8-byte BE unsigned integer
of the absolute starting offset of the next chunk. If set to all null bytes,
this indicates the "end" of the file (at which point the reconstructed file's hash
and length should be checked).

The first chunk must always be the first sequential chunk (which will hopefully
make things more obvious?). The last chunk may appear anywhere in the file.

Of course, you could just do this where each chunk is sequential and equal-size,
but where's the fun in that?
"""

import argparse
import hashlib
import logging
import random
from pathlib import Path
from typing import Optional, List

DEFAULT_INPUT_FILE = "flag.png"

# Anywhere from 1 to 10 kiB
DEFAULT_MIN_RANDOM_CHUNK_SIZE = 1024
DEFAULT_MAX_RANDOM_CHUNK_SIZE = DEFAULT_MIN_RANDOM_CHUNK_SIZE * 10


FORMAT = "[%(levelname)s] %(filename)s:%(lineno)s - %(funcName)s(): %(message)s"
logging.basicConfig(format=FORMAT)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class Chunk:
    """
    Format:
    - length of data (4 bytes, BE unsigned int)
    - data
    - absolute offset to next chunk (8 bytes, BE unsigned int)
    """

    # Constants, in bytes
    SIZE_CHUNK_LENGTH = 4
    SIZE_CHUNK_OFFSET = 8

    def __init__(self, data: bytes, idx: int):
        """
        Create a "raw" uninitialized chunk.

        :param data: The raw binary data of the chunk.
        :param idx: The index of this chunk in a larger (correct) sequence of
            chunks.
        """
        self.data: bytes = data
        self.idx: int = idx
        self.next: Optional[int] = None

        self.is_final_chunk: bool = False

        if not self._check_len():
            raise RuntimeError(
                "Chunk length exceeds UINT32_MAX, the maximum size of a chunk"
            )

    @classmethod
    def get_next_chunk_data(cls, data: bytes, cur_offset: int) -> "bytes, int":
        """
        Return a tuple containing the data of the chunk starting at `cur_offset`
        and the offset of the next chunk.
        """
        start_offset = cur_offset
        data_offset = start_offset + cls.SIZE_CHUNK_LENGTH

        chunk_length = int.from_bytes(data[cur_offset:data_offset], "big")
        next_offset = data_offset + chunk_length

        chunk_data = data[data_offset:next_offset]
        next_pointer = int.from_bytes(
            data[next_offset : next_offset + cls.SIZE_CHUNK_OFFSET], "big"
        )

        return chunk_data, next_pointer

    def _check_len(self) -> bool:
        """
        Assert that the length of the data is not greater than UINT32_MAX.

        Return True if it is within the allowed range, False otherwise.
        """
        return len(self.data) <= (2 ** (8 * self.SIZE_CHUNK_LENGTH)) - 1

    def as_bytes(self) -> bytes:
        """
        Get the full contents of this chunk as bytes.

        If the object is uninitialized, as indicated by `next` being
        None, this raises RuntimeError.
        """
        if self.next is None:
            raise RuntimeError("Attempted to get the bytes of an uninitialized chunk")

        return (
            len(self.data).to_bytes(self.SIZE_CHUNK_LENGTH, "big")
            + self.data
            + self.next.to_bytes(self.SIZE_CHUNK_OFFSET, "big")
        )

    def get_full_length(self) -> bytes:
        """
        Get the full length of this chunk.
        """
        return len(self.data) + self.SIZE_CHUNK_LENGTH + self.SIZE_CHUNK_OFFSET


class LOLFile:
    """
    Format:
    - length of reconstructed file (8 bytes, BE unsigned int)
    - md5 hash of reconstructed file (16 bytes)
    - list of chunks (first chunk is always start of reconstructed file)
    """

    # Constants, in bytes
    SIZE_FILE_LENGTH = 8
    SIZE_MD5_LENGTH = 16

    @staticmethod
    def get_raw_chunks_from_file(
        file_path: Path, min_chunk_size: int, max_chunk_size: int, seed=None
    ) -> List[Chunk]:
        """
        Create a list of randomly-sized chunks from a file.

        The raw chunks are returned in sequential order, such that concatenating
        the `data` attribute of the resulting list of chunks would produce the
        original file.

        If `min_chunk_size` is greater than `max_chunk_size`, this raises
        ValueError.

        :param file_path: The path to the file to break into chunks.
        :param min_chunk_size: The minimum size of the `data` field of a chunk.
        :param max_chunk_size: The maximum size of the `data` field of a chunk.
        :param seed: The seed to use when generating chunk sizes.
        :returns: A list of Chunk objects corresponding to the contents of the input
            file.
        """
        if max_chunk_size < min_chunk_size:
            raise ValueError("Max raw chunk size is smaller than min raw chunk size")

        # The same seed will always lead to the same random outputs.
        randomizer = random.Random(seed)

        # List of chunks.
        raw_chunks: List[Chunk] = []

        # Read in a random amount of the file. So long as we get bytes back,
        # continue attempting to read.
        with open(args.input_file, "rb") as fp:
            idx = 0
            while data := fp.read(randomizer.randint(min_chunk_size, max_chunk_size)):
                raw_chunks.append(Chunk(data, idx))
                idx += 1

        # Indicate that the final chunk should have its `next` pointer set to null
        raw_chunks[-1].is_final_chunk = True

        logger.debug(f"Created {len(raw_chunks)} chunks")
        logger.debug(f"Chunk data lengths: {[len(chunk.data) for chunk in raw_chunks]}")

        return raw_chunks

    @classmethod
    def from_chunks(cls, raw_chunks: List[Chunk], seed=None) -> bytes:
        """
        Construct a LOLFile.

        :param raw_chunks: A sequence of chunks with data in the correct order.
            That is, if the data were concatenated as-is from the list of chunks,
            the original file would pop out.
        :param seed: A valid seed for `random.Random`. If None, the seed is random
            based on the implementation of the `random` library.
        """
        # The same seed will always lead to the same random outputs.
        randomizer = random.Random(seed)

        # Create a dictionary from the raw chunks, so that we know the original
        # order of the chunks.
        chunk_indexes = {idx: chunk for idx, chunk in enumerate(raw_chunks)}

        # Randomize the order of the chunks (note that shuffle() is in-place,
        # which we don't want since we need the original chunks). Always
        # keep the first "true" chunk first.
        random_chunks: list[Chunk] = [raw_chunks[0]]
        random_chunks += randomizer.sample(raw_chunks[1:], len(raw_chunks) - 1)

        # Calculate the offset of each ordered chunk into the resulting file.
        random_offsets = {}
        cur_offset = cls.SIZE_FILE_LENGTH + cls.SIZE_MD5_LENGTH
        for chunk in random_chunks:
            random_offsets[chunk.idx] = cur_offset
            cur_offset += chunk.get_full_length()

        # With the offsets of each correctly-ordered chunk known, now link up
        # each chunk's "next" pointer
        for chunk in random_chunks:
            if chunk.idx + 1 not in random_offsets:
                logger.debug(f"Assuming chunk ending in {chunk.data[-20:]} is the end")
                chunk.next = 0
            else:
                chunk.next = random_offsets[chunk.idx + 1]

        # Get the information we need for the header
        raw_bytes = b"".join([chunk.data for chunk in raw_chunks])
        original_len = len(raw_bytes)
        md5_hash = hashlib.md5(raw_bytes).digest()

        # Return full sequence of bytes
        return (
            original_len.to_bytes(cls.SIZE_FILE_LENGTH, "big")
            + md5_hash
            + b"".join([chunk.as_bytes() for chunk in random_chunks])
        )

    @classmethod
    def undo_lol_file(cls, lol_file: bytes) -> bytes:
        """
        Undo and verify a .lol file.

        If the file fails the length and hash check, this raises RuntimeError.
        """
        len_bytes = int.from_bytes(lol_file[0:8], "big")
        md5_bytes = lol_file[8:24]

        reconstructed_data = b""
        cur_offset = 24
        while True:
            chunk_data, cur_offset = Chunk.get_next_chunk_data(lol_file, cur_offset)
            reconstructed_data += chunk_data
            # If pointer is "null"
            if cur_offset == 0:
                break

        # Do verification step
        reconstructed_hash = hashlib.md5(reconstructed_data).digest()
        reconstructed_len = len(reconstructed_data)

        if reconstructed_hash == md5_bytes:
            logger.debug(
                f"Hash check ok (got {reconstructed_hash.hex()}, expected"
                f" {md5_bytes.hex()})"
            )
        else:
            raise RuntimeError(
                f"Hash check failed (got {reconstructed_hash.hex()}, but expected"
                f" {md5_bytes.hex()})"
            )

        # well, i'd be real impressed if it passes hash but not the length lol
        if reconstructed_len == len_bytes:
            logger.debug(
                f"Length check ok (got {reconstructed_len} bytes, exepcted"
                f" {len_bytes} bytes)"
            )
        else:
            raise RuntimeError(
                f"Length check failed (got {reconstructed_len} bytes, but exepcted"
                f" {len_bytes} bytes)"
            )

        return reconstructed_data


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Creates and verifies .lol files.")
    parser.add_argument(
        "--input-file",
        default=DEFAULT_INPUT_FILE,
        type=Path,
        help="The file to convert into a .lol file.",
        required=True,
    )
    parser.add_argument(
        "--output-file",
        type=Path,
        default=None,
        help=(
            "The output path for the created .lol file. Defaults to the input file's"
            " stem with .lol instead of the original extension, if one existed."
        ),
    )
    parser.add_argument(
        "--seed",
        default=None,
        help=(
            "The random seed used to generate chunks. By default, a random seed"
            " is selected each time; you can pass a seed to make .lol generation"
            " deterministic."
        ),
    )
    parser.add_argument(
        "--min-chunk-size",
        "-l",
        type=int,
        default=DEFAULT_MIN_RANDOM_CHUNK_SIZE,
        help=(
            "The minimum length (in bytes) of the `data` field in an individual chunk,"
            " inclusive."
        ),
    )
    parser.add_argument(
        "--max-chunk-size",
        "-u",
        type=int,
        default=DEFAULT_MAX_RANDOM_CHUNK_SIZE,
        help=(
            "The maximum length (in bytes) of the `data` field in an individual chunk,"
            " exclusive."
        ),
    )

    return parser.parse_args()


def main(args: argparse.Namespace) -> None:
    if args.seed is not None:
        logger.debug(f"Using seed {args.seed}")
    else:
        logger.debug(f"No seed specified, using random seed")

    # Parse file into chunks, then pass them into LOLFile's method to convert it
    # to the "random" format
    raw_chunks = LOLFile.get_raw_chunks_from_file(
        args.input_file, args.min_chunk_size, args.max_chunk_size, args.seed
    )
    lol_file = LOLFile.from_chunks(raw_chunks, args.seed)

    # If no output file has been defined, just use the input filepath but with
    # .lol instead
    if not args.output_file:
        args.output_file = args.input_file.with_suffix(".lol")

    logger.info(f"Writing resulting file to {args.output_file}")

    # Write back out to file
    with open(args.output_file, "wb") as fp:
        fp.write(lol_file)

    # Reconstruct the file as a sanity check
    with open(args.output_file, "rb") as fp:
        try:
            reconstructed_data = LOLFile.undo_lol_file(fp.read())
        except:
            logger.exception("File-internal verify step failed")
            raise

    # Throw out the reconstructed file, just to verify. The default path is just
    # the input path with "-reconstructed" added onto its stem. Note that I use
    # with_name instead of with_stem for compatibility reasons.
    reconstructed_path = args.input_file.with_name(
        args.input_file.stem + "-reconstructed" + args.input_file.suffix
    )
    with open(reconstructed_path, "wb") as fp2:
        fp2.write(reconstructed_data)

    # Check if the file is still the same way going out as it was coming in
    with open(Path(args.input_file), "rb") as fp:
        old_hash = hashlib.md5(fp.read()).digest()

    new_hash = hashlib.md5(reconstructed_data).digest()
    if new_hash == old_hash:
        logger.info("OK")
    else:
        logger.error("Hash verify step failed")
        exit(1)


if __name__ == "__main__":
    # Parse arguments
    args = get_args()

    main(args)
