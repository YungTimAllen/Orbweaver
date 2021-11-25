#!/usr/bin/env python3
import threading
import time
from io import BytesIO
import matplotlib.pyplot as plt

from flask import Flask, render_template, jsonify
import networkx
from networkx.readwrite import json_graph
import yaml
import bgp_ls_vis.proto
import bgp_ls_vis.graphing


class LinkStateManager:
    graph: networkx.Graph = None

    def __init__(
        self, target_ipv4_address, target_port: int = 50051, task: bool = True, debug: bool = False
    ):

        # rpc = bgp_ls_vis.proto.GoBGPQueryWrapper(
        #     target_ipv4_address=target_ipv4_address,
        #     target_rpc_port=target_port,
        # )
        self.rpc = bgp_ls_vis.proto.GoBGPQueryWrapper(connect=False)
        if not debug:
            self.__update()
            if task:
                threading.Thread(target=self.task).start()
        else:
            self.lsdb = self.rpc.get_lsdb_2(filename="18-node-isis-w-bcast-segment.yaml")

    def __update(self) -> networkx.Graph:
        # self.lsdb = self.rpc.get_lsdb()
        self.lsdb = self.rpc.get_lsdb(filename="18-node-isis-w-bcast-segment.yaml")
        self.graph: networkx.Graph = bgp_ls_vis.graphing.build_nx_from_lsdb(self.lsdb)
        return self.graph

    def task(self):
        i = 0
        while True:
            time.sleep(10)

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


app = Flask(__name__)


@app.route("/")
def home():
    # return str(lsm.get_hosts())
    return render_template(
        "home.html",
        title="LSDB Report",
        hosts_list=str([h for h in lsm.get_graph().nodes]),
        lsdb=yaml.dump(lsm.get_lsdb()),
    )


@app.route("/hosts")
def rest_get_hosts():
    return jsonify(lsm.get_hosts())


@app.route("/lsdb")
def rest_get_lsdb():
    return jsonify(lsm.get_lsdb())


@app.route("/nx")
def rest_get_networkx_graph():
    return jsonify(json_graph.node_link_data(lsm.get_graph()))


def main():
    global lsm
    lsm = LinkStateManager(target_ipv4_address="10.0.0.1")

    app.run(debug=False)


if __name__ == "__main__":
    # main()
    LinkStateManager(target_ipv4_address="10.0.0.1", task=False, debug=True)
