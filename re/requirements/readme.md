# requirements

*OIT's getting real creative with their username requirements these days... can you get me one that passes this one?*

```re
(?:[?^_!#+\/{|}=$%&'*~-]{8,12}(?:\.[0-2]{2,4})*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z]{4,7}(?:[0-9]{4,7}unr)+\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])
```

A valid match is `________.00@11111unr.edu` - *approximately*, this regex requires:
- 8 to 12 characters of the first matching set `[?^_!#+\/{|}=$%&'*~-]`
- 2 to 4 characters of the second matching set `[0-2]`
- An `@`
- 4-7 alphabetic characters
- 4-7 numeric characters
- `unr`
- `.`, and then anything else