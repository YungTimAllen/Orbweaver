import threading
import time
import networkx
import bgp_ls_vis
import bgp_ls_vis.proto as proto
import bgp_ls_vis.graphing as graphing


class LinkStateManager:
    polling_period: int = 30  # seconds

    def __init__(
        self,
        target_ipv4_address,
        target_port: int = 50051,
        task: bool = True,
    ):

        # rpc = proto.GoBGPQueryWrapper(
        #     target_ipv4_address=target_ipv4_address,
        #     target_rpc_port=target_port,
        # )
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
        i = 0
        while True:

            time.sleep(self.polling_period)

            # Debugging locally
            print(f"Added new host newhost{i}")
            self.__update().add_edge("P9", f"newhost{i}")
            i += 1

    def get_hosts(self):
        return [h for h in self.graph.nodes]

    def get_lsdb(self):
        return self.lsdb

    def get_graph(self) -> networkx.Graph:
        return self.graph

    def draw_graph(self):
        networkx.draw(self.graph)
