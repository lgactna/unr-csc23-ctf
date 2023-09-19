(author: Lloyd Gonzales, RE)

This was originally designed by me for the USCG Season II Pipeline Program, where it was used in the Season III Cyber Open.

Long story short, to make a file containing the flag:
```sh
python3 lol.py --input-file flag.png -l 100 -u 200 --output-file flag.lol
```

## Description
**The challenge itself**: given a compiled binary from `lol.c` and a `.lol` file, can you figure out the file format and get the flag that's been broken up inside `flag.lol`?

At a high level, I've created a challenge that breaks up an input file into randomly-sized chunks and rearranges them in a random order. Each chunk contains some data from the original file as well as the position of the next chunk. If you follow these chunks around and keep appending the data of each chunk, you'll eventually get the original file.

The file format (`.lol`) containing these chunks has a few additional properties, most of which are also described in `lol.py`:
- The first 8 bytes of the generated file is the length of the *original* file. This makes it possible for a parser to allocate space ahead of time, and also allows the parser to check if it's gotten the entire file or not while following the chunks around.
- The next 16 bytes of the generated file is the MD5 of the *original* file.
- The first chunk in the resulting file is always the first chunk of the original file. The hope is that this makes more obvious what the file is supposed to contain, since many file formats have an easily recognizable header signature. 
    - For example, in the included sample `flag.lol`, the PNG signature can be found close to the start of the file because of this property. Then, somebody might try and binwalk `flag.lol` to no avail, or discover that the `IEND` marker that signifies the end of the PNG is somewhere in the middle of the file instead. This (hopefully?) makes it a little clearer that the file's been jumbled around.

`lol.py` is the Python script containing both a "writer" and "parser" for this file format. When run, it breaks up the input file, scrambles the chunks, and then forms the resulting file. It then attempts to parse the result to make sure it can reconstruct the original file that was passed in, serving as a self-test of sorts.

`lol.c` is the source code for just a "parser" for the file format. It simply reconstructs the file in memory and then checks if the MD5 hash is the same as what the file claims it should be. It doesn't spit out the reconstructed file, which is the challenge here.

## Local challenge creation
`lol.py` is the main script used to generate `.lol` files. It takes in five arguments:
- `--input-file`: The file to break up and turn into a `.lol` file.
- `--output-file`: The output path for the `.lol` file. If not specified, defaults to `--input-file` with the extension `.lol` instead of whatever its original extension was.
- `--seed`: The seed used to randomize chunk sizes and chunk positions. If not set, Python will usually use the current time as the seed, thus creating a different file each time. The same seed always creates the same `.lol` file, no matter what. Takes in any string.
- `--min-chunk-size` or `-l`: The minimum length of a chunk (inclusive). 
- `--max-chunk-size` or `-u`: The maximum length of a chunk (exclusive).

For example, if you wanted to make a new `flag.lol` from the included sample `flag.png`, you could run

```sh
python3 lol.py --input-file flag.png -l 100 -u 200
```

which will generate `flag.lol` with chunks that are between 100-199 bytes in length each (except possibly the last chunk). The script can handle really small chunk sizes, but it inflates the size of the resulting file by quite a bit.

Then, to verify that the generated file matches the MD5 of the original file, we can use `lol.c` (of course, Linux only):
```sh
make
./lol flag.lol

# or with gcc: strip symbols, include necessary libraries for MD5
gcc -s -Wall -Wextra -Wpedantic -o lol lol.c -lssl -lcrypto
./lol flag.lol
```

Although the intent is that the `.lol` file represents an image (because they're not too big but not too small while also being a good format to "hide" a flag in), you can pass whatever you want into `lol.py`:

```sh
python3 lol.py --input-file lol.py -l 5 -u 10 --output-file lol.lol
```

## Deployment
No part of this challenge requires any dependencies outside of the Python standard library and will definitely work on Python 3.9+. I don't believe I use any features that aren't in Python 3.8 or Python 3.7, but it definitely won't work on Python 3.6 or below.

I'm not entirely sure what features CTFd provides, but I designed this with the idea that the flag could either be dynamically generated for each person or statically shared across every person who accesses the challenge. Additionally, the file containing the flag itself can also be different across each person, even if it contains the same static flag; a valid solution should still have the same result.

I think the simplest way to deploy the challenge with a static flag is to: 
- Create `flag.png` with the text of the static flag.
- Pass `flag.png` into `lol.py` to create `flag.lol`.
- Compile `lol.c` without symbols as shown above.
- Provide competitors with `flag.lol` and the resulting binary by simply uploading those two files and serving them.

## A note on whether or not the challenge functions correctly
I've tried my best to make `lol.c` portable, namely with respect to endianness. I'm certain that it works on little-endian machines, which should cover most architectures (x86/ARM), but I haven't been able to test it on a big-endian machine. To the best of my knowledge, it should work because of the little-endian check in `lol.c`, but I don't have any environments to test this in.