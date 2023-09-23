# spare-tire

*My friend tells me he's invented a new form of encryption - can you get the original image back?*

Add a single leading zero to the the bits of the input file.

Original image from https://www.amazon.com/Eastern-Jungle-Gym-Heavy-Duty-Adjustable/dp/B007FB69EI.

To create a new flag, simply run

```sh
python3 create-flag.py input_file.png
```

which will create a new file called `input_file.png.tire`. To solve, run:

```sh
python3 solve.py input_file.png.tire
```

which will drop the leading zero and (over)write to `input_file_solved.png`.

