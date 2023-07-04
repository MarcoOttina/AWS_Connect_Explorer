from typing import Callable
from vdn_graph_types import GraphVDN, GraphVDNNode

def __main():
    g = GraphVDN("start")
    has_path:bool = True
    nodes = [
        ("start", ["a", "b", "c"]),
        ("end", []),
        ("a", ["d"]),
        ("b", []), # dead end
        ("c", ["start"]), #cycle
        ("d", ["e", "f", "g", "q"]),
        ("e", ["e"]), # dead end and self-link
        ("f", ["end"] if has_path else []),
        ("g", ["h"]), # towards a longer path
        ("h", ["i"]),
        ("i", ["j"]),
        ("j", ["end", "k"] if has_path else ["k"]), #longer cycle
        ("k", ["l"]),
        ("l", ["m"]),
        ("m", ["n"]),
        ("n", ["o"]),
        ("o", ["p"]),
        ("p", ["j"]), # end of cycle
        ("q", ["r"]), # start mini cycle with long node inside
        ("r", ["roar"]),
        ("roar", ["r", "s"]),
        ("s", ["q"]) # end of cycle
    ]
    print("filling graph")
    print("--graph ->", g.to_json())
    for n in nodes:
        g.add_node_block(n, n[0], len(n[1])==0, None)
    print("\nafter adding nodes")
    print("--graph ->", g.to_json())

    for n in nodes:
        for adj in n[1]:
            g.add_link_id(n[0], adj, True)

    print("\nafter adding LINKS")
    print("--graph ->", g.to_json())
    
    print("\n\npath")
    p = g.shortest_path("start", "end")
    print("path:")
    print(p)
    print("has path start->end ?", g.has_path("start", "end"))

    print("\n\n testing with check_trivial_start_self_link = TRUE")
    path_self_extremities=[
        "start",
        "e",
        "j",
        "q"
    ]
    filter_node: (Callable[[GraphVDNNode, GraphVDNNode],bool]|None)= lambda node_start, node_end : \
        len( (node_end if node_end is not None else node_start) .id) == 1
    uses_filter = False
    for p_s_e in path_self_extremities:
        print("\ndisabling check_trivial_start_self_link for node: ", p_s_e)
        p = g.shortest_path(\
            p_s_e, \
            p_s_e, \
            check_trivial_start_self_link= False, \
            node_filter= filter_node if uses_filter else None
        )
        print("path:")
        print(p)
    
    print("\n\n\nall ends:")
    for p in map(lambda p: p.to_json(), g.get_all_ends()):
        print("-\t:", p)
        
    print("\n\n\n recalculating ends")
    g.recalculate_ends(
        is_selfLoop_marking_end=True, \
        block_types_of_ends=['Loop', 'DisconnectParticipant'], \
        node_end_check=None
    )
    print("new graph:\n")
    print(g.to_json())
    
if __name__ == "__main__":
    __main()