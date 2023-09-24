# symbols

A bit of JS obfuscation, inspired by [http://aem1k.com/aurebesh.js/](http://aem1k.com/aurebesh.js/) and WE01 in the National Cyber Scholarship Competition.

Here's the unmodified source:

```js
A = ''              // empty string
B = !A + A          // "true"
C = !B + A          // "false"
D = A + {}          // "[object Object]"
E = B[A++]          // "t" = "true"[0]
G = ''
F = B[G = A]        // "r" = "true"[1]
H = ++G + A         // 2, 3
I = D[G + H]        // "c"

B[
  I +=              // "c"
    D[A] +          // "o" = "object"[0]
    (B.C+D)[A] +    // "n" = "undefined"[1]
    C[H] +          // "s" = "false"[3]
    E +             // "t"
    F +             // "r"
    B[G] +          // "u" = "true"[2]
    I +             // "c" = "[object]"[5]
    E +             // "t"
    D[A] +          // "o" = "[object]"[1]
    F               // "r"
][
  I                 // "constructor"
](
  C[A] +            //  "a"
  C[G] +            //  "l"
  B[H] +            //  "e"
  F +               //  "r"
  E +               //  "t"
  "(\"" +           //  "(""
  B[G] +            //  "u"
  (B.C+D)[A] +      //  "n"
  F +               //  "r"
  D[G + H] +        //  "c"
  E +               //  "t"
  C[--A] +          //  "f"
  "{" +             //  "{"
  C[G] +            //  "l"
  D[++A] +          //  "o"
  C[H] +            //  "s"
  E +               //  "t"
  "+" +             //  "+"
  C[G] +            //  "l"
  C[A] +            //  "a"
  (B.C+D)[A] +      //  "n"
  "g" +             //  "g"
  "+" +             //  "+"
  D[A++] +          //  "o"
  D[G] +            //  "b"
  D[++A] +          //  "j"
  "}\")"            //  "}")"
)()
```

And minified with [https://codebeautify.org/minify-js](https://codebeautify.org/minify-js):

```js
A="",B=!A+A,C=!B+A,D=A+{},E=B[A++],G="",F=B[G=A],H=++G+A,I=D[G+H],B[I+=D[A]+(B.C+D)[A]+C[H]+E+F+B[G]+I+E+D[A]+F][I](C[A]+C[G]+B[H]+F+E+'("'+B[G]+(B.C+D)[A]+F+D[G+H]+E+C[--A]+"{"+C[G]+D[++A]+C[H]+E+"+"+C[G]+C[A]+(B.C+D)[A]+"g+"+D[A++]+D[G]+D[++A]+'}")')();
```

Replacing with the selection of Greek letters:
```python
x = (
    """
    A="",B=!A+A,C=!B+A,D=A+{},E=B[A++],G="",F=B[G=A],H=++G+A,I=D[G+H],B[I+=D[A]+(B.C+D)[A]+C[H]+E+F+B[G]+I+E+D[A]+F][I](C[A]+C[G]+B[H]+F+E+'("'+B[G]+(B.C+D)[A]+F+D[G+H]+E+C[--A]+"{"+C[G]+D[++A]+C[H]+E+"+"+C[G]+C[A]+(B.C+D)[A]+"g+"+D[A++]+D[G]+D[++A]+'}")')();
    """
)

lang = "ABCDEFGHI"
out = "πβεγμτφθλ"

t = {x: y for x, y in zip(lang, out)}

result = ""
for char in x:
    if char in t:
        result += t[char]
    else:
        result += char

print(result)
```

which yields

```js
π="",β=!π+π,ε=!β+π,γ=π+{},μ=β[π++],φ="",τ=β[φ=π],θ=++φ+π,λ=γ[φ+θ],β[λ+=γ[π]+(β.ε+γ)[π]+ε[θ]+μ+τ+β[φ]+λ+μ+γ[π]+τ][λ](ε[π]+ε[φ]+β[θ]+τ+μ+'("'+β[φ]+(β.ε+γ)[π]+τ+γ[φ+θ]+μ+ε[--π]+"{"+ε[φ]+γ[++π]+ε[θ]+μ+"+"+ε[φ]+ε[π]+(β.ε+γ)[π]+"g+"+γ[π++]+γ[φ]+γ[++π]+'}")')();
```

It's not great, but I'm chalking that up to my lack of random JavaScript error strings.