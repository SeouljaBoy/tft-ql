from typing import Any


def splay(m: Any, layer: int = 0, depth: int | None =None) -> None:
    tab = "  "
    if depth is not None and layer > depth:
        return
    if isinstance(m, dict):
        for key in m.keys():
            print(tab * layer + str(key))
            splay(m[key], layer + 1, depth)
    elif isinstance(m, list):
        print(tab * layer + f"[{len(m)}]")
        if len(m) > 0:
            splay(m[0], layer + 1, depth)
    else:
        print(tab * layer + str(m))


# Meta TFT specific.
def avg_place(places: Any) -> Any:
    """Given a list of placement counts, computes average placement.
    [4, 6, 8, 10, 8, 6, 4, 10] => 4.714285714285714"""
    tot = sum(places)
    return sum((i+1) * x / tot for i, x in enumerate(places))

def pad_traits(traits: list[str]) -> list[str]:
    """Pads traits list with blank strings."""
    new_traits = [trait for trait in traits]
    while len(new_traits) < 3:
        new_traits.append('')
    return new_traits
