import json
from itertools import chain
from typing import Callable, Self, Any
from queue import SimpleQueue


class Jsonable:
    def to_json(self):
        return self


# just added as documentation, since it's NOT serializable automatically; call "to_json()" for that purpose
class GraphVDNNode(Jsonable):
    __is_end:bool
    id:str # it is a UUID
    block_type: str
    original_data: dict
    links_out_ids_correct: list[str]
    links_out_ids_error: list[str]
    links_causing_loops: set[str] | dict[str, bool]
    
    def __init__(self, id:str, is_end: bool = True):
        self.id = id
        self.__is_end = is_end
        self.block_type = "UNKNOWN"
        self.original_data = {}
        self.links_out_ids_correct = []
        self.links_out_ids_error = []
        self.links_causing_loops = {}
        
    def to_json(self):
        data = self.original_data
        try:
            data = json.dumps(data)
        except:
            pass
        return {
            "id": self.id,
            "is_end": self.__is_end,
            "block_type": self.block_type,
            "links_out_ids_correct": self.links_out_ids_correct,
            "links_out_ids_error": self.links_out_ids_error,
            "original_data": self.original_data,
            "links_causing_loops": [id for id in map( lambda t : t[0] , self.links_causing_loops.items()) ]
        }
    def short_description(self):
        return {
            "type": self.block_type,
            "is_end": self.__is_end,
            "id": self.id,
            "links_out": {
                "correct": len(self.links_out_ids_correct),
                "errors": len(self.links_out_ids_error)
            },
            "links_causing_loops": [id for id in map( lambda t : t[0] , self.links_causing_loops.items()) ]
        }
        
    def iterator_all_links(self) -> chain[str] :
        return chain([self.links_out_ids_correct, self.links_out_ids_error])
        
    def is_end(self):
        return self.__is_end or \
            (len(self.links_out_ids_correct)==0 and len(self.links_out_ids_error)==0)
            
    def set_is_end(self, is_end):
        self.__is_end = is_end
    
    def amount_links_out(self):
        return len(self.links_out_ids_correct) + len(self.links_out_ids_error)
        
    def has_link_out(self, node_id):
        return node_id in self.links_out_ids_correct or node_id in self.links_out_ids_error 
        
    def add_node_id_to_link_out(self, node_id:str, is_correct_link:bool):
        if is_correct_link:
            if node_id in self.links_out_ids_correct:
                print("@@@@ ERROR : add_node_id_to_link_out on adding", node_id, "into node", self.id, " in correct list")
                return False
            self.links_out_ids_correct.append(node_id)
        else:
            if node_id in self.links_out_ids_error:
                print("@@@@ ERROR : add_node_id_to_link_out on adding", node_id, "into node", self.id, " in correct list")
                return False
            self.links_out_ids_error.append(node_id)
        return True
    
    '''
    TODO: aggiungere il parametro "metadata" che permetta di specificare il tipo di errore, se "is_correct_link" fosse falso, o che valore
    e' stato controllato ed e' stato determinante nel definire questa specifica diramazione.
    Quindi, riunire ambo i link sotto una unica collezione, che e' lista di una sovraclasse astratta, le cui due sottoclassi rappresentano
    i link "normali/corretti" ed i link di errore. Es: { 'id_next': str, 'is_correct': bool, 'metadata': dict|object }
    Modificare infine i for_each tali che effettuino dei filtri su quale link invocare la "azione".
    '''
    def add_node_to_link_out(self, node: object | dict, is_correct_link: bool):
        if not isinstance(node, GraphVDNNode):
            print(" [[[[[[[[[[[[[[[[[ node is NOT A GraphNode INSTANCE]]]]]]]]]]]]]]]]]")
            return False
        return self.add_node_id_to_link_out(node.id, is_correct_link)
    
    def for_each_link_out_correct(self, action: Callable[[str], None] ):
        for l_o in self.links_out_ids_correct:
            action(l_o)
    def for_each_link_out_error(self, action: Callable[[str], None] ):
        for l_o in self.links_out_ids_error:
            action(l_o)
    def for_each_link_out(self, action: Callable[[str], None] ):
        self.for_each_link_out_correct(action)
        self.for_each_link_out_error(action)
    def mark_link_as_loop(self, adjacent_node_id:str):
        if adjacent_node_id is None or adjacent_node_id == "":
            return
        self.links_causing_loops[adjacent_node_id] = True
    def unmark_link_as_loop(self, adjacent_node_id:str):
        if (adjacent_node_id is None) or (adjacent_node_id == "") \
            or ( adjacent_node_id not in self.links_causing_loops):
            return
        del self.links_causing_loops[adjacent_node_id]
        
class forwardLink:
    never_cloned:bool
    path_length:int
    source_node:GraphVDNNode|None # works as "current node" as well
    dest_node:GraphVDNNode|None
    source_link: Self|None
    dest_link: Self|None
    def __init__(self, source_node:GraphVDNNode|None, dest_node:GraphVDNNode|None = None, prev_link:(Self|None)=None) -> None:
        self.path_length = 1
        self.never_cloned = True
        self.source_node = source_node
        self.dest_node = dest_node
        self.dest_link = None
        if prev_link is None:
            self.source_link = None
        else:
            prev_link.dest_link = self
            self.source_link = prev_link
            self.path_length = prev_link.path_length + 1
    def is_end(self):
        return self.dest_node == None #self.dest_link == None
    def is_start(self):
        return self.source_node == None #self.source_link == None
    def is_middle(self):
        return not( self.is_end() or self.is_start() )
    def is_source_end(self):
        return False if self.source_node is None else self.source_node.is_end
    def clone_after_first(self):
        if self.never_cloned:
            self.never_cloned = False
            return self
        c = forwardLink(self.source_node, self.dest_node)
        c.source_link = self.source_link
        c.path_length = self.path_length
        return c

class NodeInfoPathfinding(Jsonable):
    key:str #id
    block:GraphVDNNode
    previous:Self|None = None
    distance:int = 0
    #color: int = 0 #0 = white=="never seen", 1 = grey=="in frontier", 2 = black=="visited"
    def __init__(self, id, block, prev:Self|None = None):
        self.key = id
        self.block = block
        self.previous = prev
        self.distance = 0 if prev is None else prev.distance + 1
        #self.color = 0
    def to_json(self):
        return {
            "id": self.key,
            "previous": 'null' if self.previous is None else self.previous.key,
            "distance": self.distance
        }


class VDNPath(Jsonable):
    id_start:str|None
    id_end:str|None
    steps_ids:list[str]
    end_type:str|None
    def __init__(self, id_start:str|None=None, id_end:str|None=None, end_type:str|None=None, length:int = 0):
        self.id_start = id_start
        self.id_end = id_end
        self.steps_ids = None if length <= 0 else ([""] * length)
        self.end_type = "unknown" if end_type is None else end_type
    def to_json(self):
        return {
            "start_id": self.id_start,
            "end_id": self.id_end,
            "end_type": self.end_type,
            "length_path": len(self.steps_ids),
            "steps_ids": self.steps_ids
        }

class GraphVDN(Jsonable):
    startID:str #UUID formatted
    nodes_by_ID: dict[str, GraphVDNNode]
    ends_IDs: list[str]
    
    def __init__(self, startID):
        self.startID = startID
        self.nodes_by_ID = {}
        self.ends_IDs = []
        
    def to_json(self):
        nodes = {}
        for n_id, n in self.nodes_by_ID.items():
            nodes[n_id] = n.to_json()
        return {
            "startID": self.startID,
            "nodes_by_ID": nodes,
            "ends": self.ends_IDs #[e_id for e_id, _ in nodes]
        }

    def add_node_block(self, original_data, id: str, is_end:bool = False, \
        field_from_original_data_setter: Callable[[GraphVDNNode, object|dict],None] = None):
        if id in self.nodes_by_ID:
            print("-------- ID gia' presente:", id)
            return
        gNode = GraphVDNNode(id, is_end)
        gNode.original_data = original_data
        if field_from_original_data_setter is not None:
            field_from_original_data_setter(gNode, original_data)
        #print("added new node: <id:", id, ", is_end:", is_end, "> -->", gNode.short_description())
        self.nodes_by_ID[id] = gNode
        if is_end:
            #self.ends.append(gNode)
            self.ends_IDs.append(id)
            
    def has_node(self, id_node):
        return id_node in self.nodes_by_ID

    '''
    TODO: aggiungere il parametro "metadata" che permetta di specificare il tipo di errore, se "is_correct_link" fosse vero, o che valore
    e' stato controllato ed e' stato determinante nel definire questa specifica diramazione
    '''
    def add_link_id(self, id_node_source, id_node_destination, is_correct_link: bool):
        if id_node_source not in self.nodes_by_ID:
            print("___ERROR Graph.add_link_id #1 add link id: ID source (", id_node_source, ") not found:", id_node_source)
            return False
        if id_node_destination not in self.nodes_by_ID:
            print("___ERROR Graph.add_link_id #2 add link id: ID dest (", id_node_destination, ") not found:", False)
            return False
        return self.nodes_by_ID[id_node_source].add_node_id_to_link_out(id_node_destination, is_correct_link)

        
    def __dfs(self, action:Callable[[GraphVDNNode,GraphVDNNode], None], visited_nodes: dict[str, bool], current_node: GraphVDNNode, father_node: GraphVDNNode):
        if current_node.id in visited_nodes:
            return
        visited_nodes[current_node.id] = True
        action(current_node, father_node)
        
        def dfs_iteration(id_out: str):
            if id_out in visited_nodes:
                return
            self.__dfs(action, visited_nodes, self.nodes_by_ID[id_out], current_node)
        current_node.for_each_link_out(dfs_iteration)

    # Depth-First Search
    # scan the whole network, touching each nodes just once, performing an action on each node.
    # The action accepts two parameters: the current node and its father from the root
    # (the father of the root is None).
    def depth_first_search(self, action:Callable[[GraphVDNNode,GraphVDNNode], None]):
        starting_node = self.nodes_by_ID[self.startID]
        visited_nodes: dict[str, bool] = {}
        self.__dfs(action, visited_nodes, starting_node, None)
        
    # the path collector is a function accepting the list of already collected paths, the current "end node" and its relative incoming link
    def __gae(self, paths_to_vdns: list[VDNPath], path_collector: Callable[[list[VDNPath], GraphVDNNode, forwardLink], VDNPath] , current_node: GraphVDNNode, incoming_link: forwardLink) -> None:
        print("---exploring:", current_node.short_description(), " ----> from", ('SUPER-ROOT' if incoming_link.source_node is None else incoming_link.source_node.id), "node ")
        if current_node.is_end():
            print("----- end found!")
            path_collector(paths_to_vdns, current_node, incoming_link)
            return
        
        # avoid infinite recursion by detecting a cycle
        already_explored_nodes: dict[str, bool] = {}
        already_explored_nodes[current_node.id] = True
        backward_iter_link = incoming_link.source_link
        no_cycle = True
        while (backward_iter_link is not None) \
            and (backward_iter_link.source_node is not None) \
            and no_cycle:
                no_cycle = (backward_iter_link.source_node.id not in already_explored_nodes) # is the previous node alreadi seen
                if no_cycle:
                    already_explored_nodes[backward_iter_link.source_node.id] = True
                    backward_iter_link = backward_iter_link.source_link
        already_explored_nodes.clear()
        already_explored_nodes = None
        if not no_cycle:
            print("##### CYCLE detected in", current_node.id)
            return
        
        #recursion
        def gae_on_out_links(id_out_node):
            out_node = self.nodes_by_ID[id_out_node]
            next_link = forwardLink(current_node, out_node, incoming_link.clone_after_first())
            self.__gae(paths_to_vdns, path_collector, out_node, next_link)
            
        print(" recursion on neighbours")
        current_node.for_each_link_out(gae_on_out_links)
        print("returned onto", current_node.id)
    
    def get_all_ends(self) -> list[VDNPath]:
        #self.depth_first_search(lambda current_node, father_node: print(('ENTRY POINT' if father_node is None else father_node.id), "->", current_node.id))
        
        starting_node = self.nodes_by_ID[self.startID]
        
        #forward_links : dict[str, str] = {} # keep track of
        super_root: forwardLink = forwardLink(None, dest_node=starting_node)
        
        paths_to_vdns: list[VDNPath] = []
        
        def path_collector(already_collected_paths: list[VDNPath], end_node:GraphVDNNode, incoming_link:forwardLink):
            new_VDN_path:VDNPath = VDNPath( \
                id_start = None, \
                id_end = end_node.id, \
                end_type = end_node.block_type, \
                length = incoming_link.path_length)
            new_VDN_path.steps_ids[incoming_link.path_length-1] = end_node.id
            
            # collect all IDs, in a backward manner
            i = incoming_link.path_length - 1
            backward_link_iter = incoming_link
            while i >= 0 and (backward_link_iter is not None): # and (backward_link_iter.dest_node is not None):
                # the last node, the "end", is already collected (hence, the "-1" below): already jump backward
                backward_link_iter = backward_link_iter.source_link
                i -= 1
                if (backward_link_iter is not None and backward_link_iter.dest_node is not None): # a jump is done, the current "link" might be the "super_node"
                    new_VDN_path.steps_ids[i] = backward_link_iter.dest_node.id
            new_VDN_path.id_start = new_VDN_path.steps_ids[0]
            
            already_collected_paths.append(new_VDN_path)
            return new_VDN_path
            
        print("------------------------------------starting GAE")
        self.__gae(paths_to_vdns, path_collector, starting_node, super_root)
        return paths_to_vdns
    
    def recalculate_ends(self, \
        is_selfLoop_marking_end:bool = True, \
        block_types_of_ends:(list[str]|set[str]|dict[str,Any]|None) = None, \
        node_end_check:(Callable[[GraphVDNNode],bool]|None)=None \
        ):
        '''
        block_types_of_ends: a set of Block Types forcing each block of one of those types to be marked
        as "end" automatically
        '''
        has_bte = (block_types_of_ends is not None) and len(block_types_of_ends) > 0
        has_nec = node_end_check is not None
        
        for id_node, node in self.nodes_by_ID.items():
            is_end = False
            print("NODE:", id_node)
            
            if has_bte and node.block_type in block_types_of_ends:
                is_end = True
            elif (node.amount_links_out() == 0) or \
                (all(map( lambda id_adj: id_adj == id_node, node.iterator_all_links()))):
                is_end = True
            elif has_nec and node_end_check(node):
                is_end = True
            else:
                links_list = [node.links_out_ids_correct, node.links_out_ids_error]
                amount_links_ount = node.amount_links_out()
                links_counter_causing_selfLoop = 0
                self_loop_found = False
                #i_list = 0
                #while i_list < len(links_list) and ( not(is_selfLoop_marking_end and self_loop_found) ):
                for links in links_list:
                    for adjacent_id in links:
                        if (adjacent_id == id_node) :
                            print("id_node:", id_node, "-> adjacent_id:", adjacent_id)
                        if (adjacent_id == id_node) or self.has_path(adjacent_id, id_node):
                            links_counter_causing_selfLoop += 1
                            self_loop_found = True
                            node.mark_link_as_loop(adjacent_id)
                if (is_selfLoop_marking_end and self_loop_found) or (links_counter_causing_selfLoop == amount_links_ount):
                    print("#1 node \'", id_node, "\' has", links_counter_causing_selfLoop, "over", amount_links_ount, "links ... found loops?", self_loop_found)
                    is_end = True
                else:
                    print("#2 node \'", id_node, "\' has", links_counter_causing_selfLoop, "over", amount_links_ount, "links ... found loops?", self_loop_found)
            node.set_is_end(is_end)
    
    def add_edges(self, \
        edges:(list[tuple[str]]), \
        is_selfLoop_marking_end:bool = True, \
        block_types_of_ends:(list[str]|set[str]|dict[str,Any]|None) = None, \
        node_end_check:(Callable[[GraphVDNNode],bool]|None)=None \
        ):
        for e in edges:
            source = e[0]
            dest = e[1]
            is_correct_link = e[2]
            if source in self.nodes_by_ID:
                self.nodes_by_ID[source].add_node_id_to_link_out(dest, is_correct_link)
        self.recalculate_ends(is_selfLoop_marking_end, block_types_of_ends, node_end_check)
            

    def shortest_path( \
        self, \
        id_start, \
        id_dest, \
        check_trivial_start_self_link:bool = True, \
        node_filter: (Callable[[GraphVDNNode|None, GraphVDNNode|None],bool]|None) = None \
        ) -> list[str]|None :
        '''
        The optional predicate can be used to filter in the edges, if specified. It is a
        filter function accepting 2 optional nodes: the source and the destination links
        of an edge. In particular, the starting node is provided as the first parameter,
        while the ending node is provided as the second parameter. 
        '''
        
        if (id_start is None) or (id_dest is None) \
            or (id_start not in self.nodes_by_ID) or (id_dest not in self.nodes_by_ID):
            return None
        if check_trivial_start_self_link and id_start == id_dest:
            return [id_start]
        
        frontier:SimpleQueue = SimpleQueue()
        nodes_info: dict[str, NodeInfoPathfinding] = {}
        include_all_nodes = node_filter is None
        
        block_start = self.nodes_by_ID[id_start]
        block_dest = self.nodes_by_ID[id_dest]
        if (not include_all_nodes) and \
            ((not node_filter(block_start, None)) or (not node_filter(None, block_dest))):
                return None # if some of the starting or ending node is filtered out, then no such path can exists
            
        node_start:NodeInfoPathfinding = NodeInfoPathfinding(id_start, block_start)
        nodes_info[id_start] = node_start
        node_start.previous = node_start # useful marker to retrieve the path
        node_dest:NodeInfoPathfinding = NodeInfoPathfinding(id_dest, block_dest)
        nodes_info[id_dest] = node_dest
        
        current_node:NodeInfoPathfinding = node_start
        frontier.put_nowait(node_start)
        
        # BFS graph traversal (breadth-first search)
        # since all links are "equal", i.e. they all have the same weight,
        # then the BFS is the most efficient path finding algorithm
                
        while node_dest.previous is None and (not frontier.empty()):
            current_node = frontier.get_nowait()
            # current_node is not the destination
            # for each adjacent ...
            #current_node.block.for_each_link_out( for_each_adjacent )
            for blocks_adj in (current_node.block.links_out_ids_correct, current_node.block.links_out_ids_error):
                i = 0
                l = len(blocks_adj)
                while node_dest.previous is None and i < l:
                    id_adj = blocks_adj[i]
                    i += 1
                    if id_adj == id_dest:
                        node_dest.previous = current_node # found
                        node_dest.distance = current_node.distance + 1
                    else:
                        adj_block = self.nodes_by_ID[id_adj]
                        if (id_adj not in nodes_info) and \
                            (include_all_nodes or node_filter(current_node, adj_block)):
                            adj_node:NodeInfoPathfinding = NodeInfoPathfinding(id_adj, adj_block, current_node)
                            nodes_info[id_adj] = adj_node
                            frontier.put_nowait(adj_node)
                        #else: cycle detected
                        
 
        if node_dest.previous is None:
            return None
        '''
        cycle_detected = id_start == id_dest
        i = 0
        if cycle_detected: #discard the end, since it's equal to the starting point
            i = (node_dest.distance -1)
            current_node = node_dest.previous
        else:
            current_node = node_dest
            i = node_dest.distance
        path:list[str] = [""] * (i + 1)
        '''
        current_node = node_dest
        i = node_dest.distance
        path:list[str] = [""] * (i + 1)
        
        print("path length: ", len(path), ": but i:", i)
        while current_node.previous != current_node \
            and i > 0: # check added as a bug-guard
            print("PATH includes:", current_node.key)
            path[i] = current_node.key
            i -= 1
            current_node = current_node.previous
        #if not cycle_detected:
        #    path[0] = id_start
        path[0] = id_start
        return path
    
    def has_path (self, \
        id_start, \
        id_dest, \
        check_trivial_start_self_link:bool = True, \
        node_filter: (Callable[[GraphVDNNode|None, GraphVDNNode|None],bool]|None) = None \
        ) -> list[str]|None :
        path = self.shortest_path(id_start, id_dest, check_trivial_start_self_link, node_filter)
        return path is not None and (len(path) > (0 if check_trivial_start_self_link else 1))
                        

