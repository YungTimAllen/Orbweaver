"""Discrete graphing tools for bgp_ls_vis"""
import networkx as nx


def build_nx_from_lsdb(lsdb: list) -> nx.MultiDiGraph:
    """Given an LSDB gleaned from BGP-LS table in GoBGP, constructs a NetworkX graph object
    and returns it"""
    graph = nx.MultiDiGraph()

    # init Node LSAs to NetworkX Graph object
    for lsa in lsdb:
        if lsa["nlri"]["nlri"]["type"] == "LsNodeNLRI":
            graph.add_node(
                lsa["nlri"]["nlri"]["localNode"]["igpRouterId"],
                data=lsa,
            )

    # init Link and Prefix LSAs to NetworkX Graph object
    for lsa in lsdb:
        if lsa["nlri"]["nlri"]["type"] == "LsLinkNLRI":
            graph.add_edge(
                lsa["nlri"]["nlri"]["localNode"]["igpRouterId"],
                lsa["nlri"]["nlri"]["remoteNode"]["igpRouterId"],
                data=lsa,
            )

        if lsa["nlri"]["nlri"]["type"] == "LsPrefixV4NLRI":
            graph.nodes[lsa["nlri"]["nlri"]["localNode"]["igpRouterId"]]["data"] = lsa

    return graph
