"""Link-State Manager Class - Handles periodic updates and Flask endpoint logic"""
import threading
import time
import networkx
from networkx.readwrite.json_graph import node_link_data
from . import proto
from . import graphing


class LinkStateManager:
    """Link-State Manager object, wrapper for GoBGP calls"""

    def __init__(
        self,
        target_ipv4_address,
        target_port: int = 50051,
        task: bool = True,
        polling_period: int = 3,  # seconds
    ):
        """Constructor"""
        self.rpc = proto.GoBGPQueryWrapper(
            target_ipv4_address=target_ipv4_address,
            target_rpc_port=target_port,
        )
        self.polling_period = polling_period
        self.__update()
        if task:
            threading.Thread(target=self.task).start()

    def __update(self) -> networkx.Graph:
        """Updates the cached nx topology by calling gRPC methods that query GoBGP for it's LSDB
        then loading the content into a networkx graph object"""
        self.lsdb = self.rpc.get_lsdb()
        self.graph: networkx.Graph = graphing.build_nx_from_lsdb(self.lsdb)
        return self.graph

    def task(self):
        """Blocking task to be threaded, periodically updates the cached networkx graph object"""
        while True:
            time.sleep(self.polling_period)
            self.__update()

    def get_hosts(self) -> list:
        """Returns all nodes in the networkx graph, aka all link-state routers in the LSDB"""
        return list(self.graph.nodes)

    def get_lsdb(self) -> list:
        """Returns the full LSDB as gleaned from the BGP-LS table in GoBGP"""
        return self.lsdb

    def get_graph(self) -> dict:
        """Returns the cached NetworkX graph object as JSON"""
        return node_link_data(self.graph)

    def get_shortest_path(self, source_node: str, target_node: str) -> dict:
        """Shortest path between two node names"""
        return networkx.shortest_path(
            G=self.graph,
            source=source_node,
            target=target_node,
            method="dijkstra",
            weight="igpMetric",
        )

    def get_shortest_path_subgraph(self, source_node: str, target_node: str) -> dict:
        nodes_in_spf = networkx.shortest_path(
            G=self.graph,
            source=source_node,
            target=target_node,
            method="dijkstra",
            weight="igpMetric",
        )
        return node_link_data(self.graph.subgraph(nodes=nodes_in_spf))
