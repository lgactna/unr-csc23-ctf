# annual-netid-reset

*I'm tired of figuring out new passwords every time, so I've decided to make my passwords from the most random source there is - the UNR homepage!*

*The password is two 4+ letter words followed by a number scraped from the homepage, all lowercase. Oh, and there's an exclamation point at the end.*

This challenge scrapes two words and a number from a target webpage, then tacks on a punctuation mark at random. Users should write a script to scrape the target webpage, and will most likely want to generate a wordlist that can be fed into a high-speed cracker.

While both the solve of this challenge and its generation could be done manually (e.g. through manual parsing with something like Python's Beautiful Soup library), `cewl` and `hashcat` are sufficient:

```sh
# Use Kali's cewl to grab all 4+character words and numbers from the homepage,
# then make them all lowercase and put them in wordlist.txt
cewl https://www.unr.edu/ -d 1 -m 4  --with-numbers --lowercase > wordlist.txt

# Randomly pick two words and mash them together - you should verify that the two 
# words are actually visible on the homepage and are unlikely to change
shuf -n 2 wordlist.txt | tr -d '\n'

# You *can* also randomly pick a number, but I recommend making sure it's one
# that's actually visible on the page and not just in the source code somewhere
pcregrep "^[0-9]+$" wordlist.txt | shuf -n 1

# This is what you'll want to provide to competitors
echo "nevadaexcellence1874" -n | md5sum | awk '{ print $1 }' > hash.txt

# To make a valid wordlist, we can use a combinator attack. Since the password
# format is word - word - number, we can start off by making the right side of
# the wordlist:
pcregrep "^[0-9]+$" wordlist.txt > numbers.txt
hashcat -m 0 -a 1 --stdout hash.txt wordlist.txt numbers.txt > right-side.txt
cat right-side.txt | while read line; do echo ${line}!; done > right-side.txt

# At this point, it's sufficient to actually run hashcat:
hashcat -m 0 -a 1 --stdout hash.txt wordlist.txt right-side.txt
```