import threading
import time
import networkx
from networkx.readwrite.json_graph import node_link_data
from . import proto
from . import graphing


class LinkStateManager:
    def __init__(
        self,
        target_ipv4_address,
        target_port: int = 50051,
        task: bool = True,
        polling_period: int = 30,
    ):

        # rpc = proto.GoBGPQueryWrapper(
        #     target_ipv4_address=target_ipv4_address,
        #     target_rpc_port=target_port,
        # )
        self.polling_period = polling_period
        self.rpc = proto.GoBGPQueryWrapper(connect=False)
        self.__update()
        if task:
            threading.Thread(target=self.task).start()

    def __update(self) -> networkx.Graph:
        # self.lsdb = self.rpc.get_lsdb()
        self.lsdb = self.rpc.get_lsdb(filename="18-node-isis-w-bcast-segment.yaml")
        self.graph: networkx.Graph = graphing.build_nx_from_lsdb(self.lsdb)
        return self.graph

    def task(self):
        while True:
            time.sleep(self.polling_period)
            self.__update()

    def get_hosts(self) -> list:
        return [h for h in self.graph.nodes]

    def get_lsdb(self) -> list:
        return self.lsdb

    def get_graph(self) -> dict:
        return node_link_data(self.graph)
