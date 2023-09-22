To-Do
=====

### Test in-game:

- Mackerel range
- Tuna / Anglerfish symbiosis (+X for every Y in neighbouring fish)
    - Only Y _produced_ by the neighbouring fish, or _all_ Y there from any source?
    - The latter interpretation will currently lead to infinite recursion.

### Others

- Symbiosis declaration:

```python
class Somefish(Fish):
    class SOME_SYMB:
        bonus = Yield(food=1)
    class SomeSymb(Symbiosis):
        def yields(self):
            return self.SOME_SYMB.bonus if self.x else Yields()

```

- Source `@require_world` decorator

- Solve Circular dependencies (Tuna, Anglerfish)

- Rename Tile -> Patch

- Resources are **NOT** integers!!! They are _float_!

### UI:

- Patch has Source
- Source has Aspects:
    - Class description, no indication of actual yield
    - "**Potent Herd Aspect** - +X **Food**. If at least Y **Natura**, +Z **Food**"
- Source resources, provided by it and given to it
    - Might include symbiosis given from other sources to this _Source_, counted in Symbiosis
        - Papayas affected by Bank's Frutas Inc
        -
    - Do not include resources from ranged animals, these are given to the _Patch_
    - Food: "Base: X, Aspects: Y, Symbiosis: Z, **Total: T**
        - Base listed even if 0, Aspects and Symbiosis not
    - Technology: ...
    - Wealth
    - Awe
    - Danger
    - Natura
    - Range
- Symbiosis list: for each, Description and resulted Resources (not discriminated why)
- Transmutations: Some require 2 aspects of each (not in Wiki)
- For Projects:
    - the Specialization is counted as Symbiosis, not Base
    - Specialization that depends on resources from other patches
      are NOT counted in the Source at all, only in the Patch as "On-Patch Symbiosis"
    - Bank: Local Investment 185, "Frutas" Inc 100, Source 100 (as Symbiosis),
      Patch 285 (Base 100, On-Patch Symbiosis 185)
- Patch:
    - For each Resource (Food, Technology, ...):
        - Base: T (from source on this patch, same T in the above Source Total)
            - Except Animals, where patch source is listed with other sources
            - Except Natura, counted as Base even if produced by another source
            - So source total natura may be 5, but its patch base natura might be 10
            - Base not listed if 0 (animal patches)
        - Source A Name: a (from ranged animal in another patch)
        - Source B Name: b
        - Source C Name: c
        - ...
        - "On-Patch Symbiosis": resources that depend on other resources?
        - **Total: x**
    - Range is not included

Conclusions:

- Minerals and Plants provide resources to their own Patch as "Base"
- Animals provide resources to Patches, _including their own_, as "Animal Name"
- Patches with Animals have no Base, only "Animal Name"
- Projects have Source Base=0, bonus goes to Source Symbiosis (or Patch On-Patch).
- Symbiosis affecting other sources, are added to those sources Symbiosis (Frutas->Papaya)
- Symbiosis affected by resources from other _sources_ are added to the Source Symbiosis as usual
    - Most Symbiosis affected by resources are of this kind.
- Symbiosis affected by resources from other _patches_ are added to "On-Patch Symbiosis"
    - Very little symbiosis fall in this case.
- Natura in a Source only listed if it produces any. Natura in Patch shows highest from nearby sources

Examples:

- Superior Iron
    - Source:
        - Technology:
            - Base: 25
            - Aspects: 65
            - Symbiosis: 120
            - Total: 210
    - War Metal:
        - Technology: 120
    - Patch:
        - Technology: Base: 120, Superior Parrotfish: 9, Total: 129
        - Danger: Superior Clownfish: 6, Superior Clownfish: 6, Total: 12

- Great Gila Monster (Wealth, "... for each _patch_ with at least 25 Natura"):
    - Source: Base 20, Aspects 12, Symbiosis: 10 (from "Adaptation" only), Total: 42
    - Slow Potentials: 20 (not counted above)
    - Adaptation: 10 (only counted as On-Patch Symbiosis)
    - Patch: Great Gila Monster: 42 (source total), On-Patch Symbiosis: 20, Total: 62

- Multinational
    - Frutas Inc: +X Wealth goes to (self) Source Symbiosis
    - All Papayas get +Y Food in their Source Symbiosis

- Silver. "80% from neighbouring Gold, ..." goes to Source Symbiosis as usual
    - Maybe because it's from other _sources_, not _patches_
    - Does **not** include other Wealth in the Gold's _patch_ (from Animals), only
      Wealth from the Gold _source_
- Hospital. "1.5 Food from Plants in 2 range" also to Source Symbiosis
    - Maybe because it gets "from _Plants_" and not "from _patches_"

Challenging:

- Orange Tree 3 25 Food, 5 Natura +3 Food for each Natura on this Patch.
  +27 Food for each different Source Type within Natura Range, excluding itself.
- Cardon Cactus 3 15 Food, 4 Natura +25 Food for each Mineral within Natura Range.
  Gains 50% of the Wealth of all Minerals within Natura Range.
- Barrel Cactus 1 2 Technology, 2 Natura +8 Technology if at least 5 Wealth on this patch.
- Goat 1 1 Food, 2 Range +6 Food on each patch within Animal-Range that has a Plant.
- Bighorn 3 6 Food, 2 Range +5 Food for each Mineral in Animal-Range.
  All Goats and Deer on the planet gain +3 Food.
- Bull 3 5 Food, 5 Wealth, 1 Danger, 2 Range +30 Food and +30 Wealth on each patch in Animal-Range that has a Plant.
  +1 Wealth for each 1 Awe from Plants within Animal-Range.
- Cacao Tree 3 15 Food, 12 Natura +25 Awe if next to a Plant. +25 Natura if next to a Mineral. +50 Food if next to an
  Animal.
  +80 Food if there is at least 150 Technology in Natura Range.
- Hemp 2 8 Technology, 4 Natura +1 Technology for each Awe within Natura Range.
  +15 Technology and +10 Awe for each Iron, Phosphorus, Salt or Aluminium next to it.
- Buffalo 2 4 Food, 2 Range Each patch within Animal Range with a Plant receives a 50% bonus of that Plant's Food.
  +5 Food for each Hemp, Tomato or Marsh Mallow next to this Buffalo.
    - Only the _patch_ gets the bonus, as "On-Patch Symbiosis", based on the Plant's _Total_
- Multinational -> Papaya -> Buffalo effect
- Orangutan 3 8 Food, 2 Range +12 Technology for each Rubber Tree, Coffea, White Willow, Papaya and Cacao Tree within
  Animal-Range. Stacks up to 3 times. +1 Range if at least two such trees are within Animal-Range.
  White Willow or Coffea gain 75% extra Technology. This is an on-patch symbiosis.
    - So it's actually the _patch_ that gets the bonus, not the plants
- Dragonfruit 1 4 Food, 10 Technology, 1 Natura +1 Food and +0.5 Awe for each Natura.
- Lychee 2 10 Food, 4 Natura +18 Food for each Animal Nest next to it.
  Animals within Natura Range gain +2 Food.
- Cinnamomum 2 15 Food, 15 Wealth, 1 Natura Gains 60% of the Wealth of neighboring Minerals.
  +5 Food for each Plant within Natura Range. Also gains +20 Food if next to a Plant.
- Tea Plant 2 10 Food, 7 Natura, 5 Awe +12 Awe for each Tea Plant within Natura Range.
  +1 Natura Range and +35 Technology if this patch has at least 15 Natura.
- Musk Deer 	1 	2 Food, 1 Wealth, 2 Range 	+1 Wealth for each patch within Animal Range with at least 10 Technology.
+1 Range if at least 2 Danger on this patch.
- Diamond 	Forest,Desert,Swamp, Mountain 	3 	500 Wealth in Use and 250 Food in Use. 	25 Wealth 	+100 Wealth if next to 2 Plants, and +100 Wealth if there are 2 Minerals within 2 range.
+2.5 Wealth for each 1 Wealth from neighboring Animals.
- Oil 	+100 Wealth gain 100% of the Food from neighboring Plants as Technology.
+5 Technology for each Plant on the planet. +5 Wealth for each Mineral on the planet. +5 Food for each Animal on the planet.
  (Wiki has _very_ inconsistent data on Oil. See its Symbiosis Activation, transmutation from Platinum, etc.)

### Evaluation Order:

- Resources: reverse presentation order, Natura must be first, then Range
- Natura before everything, for Aspects. See Tea Plant
- Danger before Range. See Musk Deer - **How?**
- Danger before Wealth . See White Shark
- Awe before Technology. See Hemp
- Technology before Awe. See Anglerfish. **Damn!**
- Awe before Wealth. See Panda, Coal
- Awe before Tech. See Coal
- Wealth before Technology. See Barrel Cactus, Musk Deer
- Wealth before Food. See Tuna
- Technology before Food. See Cacao Tree
- Aspects depend on Natura
- Natural Sources: Minerals before Plants. See Cardon Cactus, Cinnamomum
- Plants before Animals. See Buffalo, Lychee
- Animals before Minerals. See Diamond **Impossible**
