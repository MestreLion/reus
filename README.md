# Reus Game Tools

Tools and assorted scripts for [Reus game][1]

---
Installing
----------

To install the project and its dependencies, preferably in a virtual environment:

    pip3 install -e .

> _**Note**: Fully tested on Python 3.8, should work fine on all later python versions._

Usage
-----

For basic usage, just run:

    reus-fish-calculator @ Seabass Clown Parrot Tuna Parrot Seabass ] Mack Tuna Mack

And voilá!

```console
Ocean Layout:
[<Seabass(food= 5)>,
 <Clownfish(gold= 4)>,
 <Parrotfish(gold= 6, tech= 4)>,
 <Tuna(food=13)>,
 <Parrotfish(gold= 6, tech= 4)>,
 <Seabass(food= 5)>,
 <Mackerel(food= 2, range=3)>,
 <Tuna(food= 7)>,
 <Mackerel(food= 2, range=3)>]

Village Sources, range = 6:
{0: <Yields(food= 5, gold=10, tech= 4)>,
 1: <Yields(food=18, gold=10, tech= 4)>,
 2: <Yields(food=18, gold=16, tech= 8)>,
 3: <Yields(food=20, gold=16, tech= 8)>,
 4: <Yields(food=20, gold=12, tech= 8)>,
 5: <Yields(food=29, gold= 6, tech= 4)>}

Total: food=110, gold=70, tech=36
Prosperity: 216
```

How powerful can you make your oceans?

---
Contributing
------------

Patches are welcome! Fork, hack, request pull!

If you find a bug or have any enhancement request, please do open a [new issue][11]


Author
------

Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>

License and Copyright
---------------------
```
Copyright (C) 2023 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>.
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>.
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
```

[1]: https://wiki.reusgame.com/
[10]: https://github.com/MestreLion/reus/blob/main/TODO.md
[11]: https://github.com/MestreLion/reus/issues
