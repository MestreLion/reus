from reus.model import Yields

# Instancing
ref = Yields(food=1, gold=2, tech=3, awe=4, danger=5)  # keyword args
twin = Yields(1, 2, 3, 4, 5)  # positional args
assert (zero := Yields()) == Yields(0, 0, 0, 0, 0)  # all args optional, all default to 0

# dict and tuple conversion, iterability
assert not isinstance(ref, tuple)  # not a tuple subclass
assert not isinstance(ref, dict)  # not a dict subclass
assert (dic := dict(food=1, gold=2, tech=3, awe=4, danger=5)) == vars(ref)
assert (tup := (1, 2, 3, 4, 5)) == tuple(twin)  # iterability
assert (length := 5) == len(tup)  # Yield itself has no len

# Identity, Equality and Truthiness
assert ref is ref
assert ref is not twin
assert ref == ref == twin == Yields(**dic) == Yields(*tup)
assert not ref == (other := Yields(*reversed(tup)))
assert ref != other
assert ref
assert Yields()

# Arithmetics
assert ref + zero == ref
assert ref + other == (const := Yields(*(length * (length + 1,))))
assert (double := 2 * ref) == ref * 2 == ref + ref == Yields(*(range(2, length * 2 + 2, 2)))
assert double == 2.0 * ref == ref * 2.0  # accept float
assert double / 2 == double // 2 == double / 2.0 == double // 2.0 == ref
assert 2 * zero == zero
assert zero / 2 == zero

# Truncation
assert 1.1 * ref == ref
assert 1.5 * ref == Yields(*(int(1.5 * _) for _ in ref)) != ref

# dataclass
# import dataclasses
# assert dic == dataclasses.asdict(ref)
# assert tup == dataclasses.astuple(ref)
# assert length == len(dataclasses.fields(ref))

print("Done!")
