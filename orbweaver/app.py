#!/usr/bin/env python3
"""Orbweaver, Flask RESTful frontend for GoBGP"""
import sys
from os.path import isfile
from flask import Flask, render_template, jsonify, make_response
import yaml
from bgp_ls_vis.lsm import LinkStateManager

CONF = (
    yaml.safe_load(open("config.yaml", "r"))
    if isfile("config.yaml")
    else sys.exit("Config.yaml not found. Exiting.")
)


app = Flask(__name__)
LSM = LinkStateManager(
    target_ipv4_address=CONF["gobgp_grpc_ip"],
    target_port=CONF["gobgp_grpc_port"],
    polling_period=CONF["update_interval"],
)


@app.route("/")
def home():
    """Flask root endpoint"""
    return make_response(
        render_template(
            "home.html",
            title="LSDB Report",
            hosts_list=str(LSM.get_hosts()),
            lsdb=yaml.dump(LSM.get_lsdb()),
        ),
        200,
    )


@app.route("/hosts")
def rest_get_hosts():
    """Flask endpoint to return all nodes in the LSDB graph"""
    return make_response(jsonify(LSM.get_hosts()), 200)


@app.route("/lsdb")
def rest_get_lsdb():
    """Flask endpoint to return the LSDB as gleaned from GoBGP's BGP-LS table"""
    return make_response(jsonify(LSM.get_lsdb()), 200)


@app.route("/nx")
def rest_get_networkx_graph():
    """Flask endpoint to return the LSDB as a NetworkX BiDirGraph object in JSON format"""
    return make_response(jsonify(LSM.get_graph()), 200)


@app.route("/shortest_path/<source_node>/<target_node>/hosts", methods=["POST"])
def rest_shortest_path_hosts(source_node: str, target_node: str):
    """alculates the shortest path and returns an ordered list of node names.

    Examples:
        $ curl -X POST http://127.0.0.1/shortest_path/0000.0000.0001/0000.0000.0009
        ["0000.0000.0001","0000.0000.0005","0000.0000.0009"]

    Args:
        source_node:
        target_node:

    Returns:

    """
    return make_response(
        jsonify(
            LSM.get_shortest_path(
                source_node=source_node,
                target_node=target_node,
            )
        ),
        200,
    )


@app.route("/shortest_path/<source_node>/<target_node>", methods=["POST"])
def rest_shortest_path(source_node: str, target_node: str):
    """Calculates the shortest path and returns a sub-graph of those nodes concerned.
    What is returned is a networkx graph object in JSON format. Note that edges in the subgraph
    which are not used in the shortest path calculated will NOT be pruned.

    Examples:
        curl -X POST http://127.0.0.1/shortest_path/0000.0000.0001/0000.0000.0009
        {"directed":true,"graph":{},"links":[{"data":{ ...

    Args:
        source_node:
        target_node:

    Returns:

    """
    return make_response(
        jsonify(
            LSM.get_shortest_path_subgraph(
                source_node=source_node,
                target_node=target_node,
            )
        ),
        200,
    )


def main():
    """Entrypoint when ran as a script"""
    app.run(debug=False, host=CONF["flask_bind_ip"], port=CONF["flask_bind_port"])


if __name__ == "__main__":
    main()
