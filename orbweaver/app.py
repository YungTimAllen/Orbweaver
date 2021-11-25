#!/usr/bin/env python3
from flask import Flask, render_template, jsonify
from networkx.readwrite import json_graph
import yaml
from bgp_ls_vis.lsm import LinkStateManager


app = Flask(__name__)
global LSM
LSM = LinkStateManager(target_ipv4_address="10.0.0.1")


@app.route("/")
def home():
    return render_template(
        "home.html",
        title="LSDB Report",
        hosts_list=str([h for h in LSM.get_graph().nodes]),
        lsdb=yaml.dump(LSM.get_lsdb()),
    )


@app.route("/hosts")
def rest_get_hosts():
    return jsonify(LSM.get_hosts())


@app.route("/lsdb")
def rest_get_lsdb():
    return jsonify(LSM.get_lsdb())


@app.route("/nx")
def rest_get_networkx_graph():
    return jsonify(json_graph.node_link_data(LSM.get_graph()))


def main():
    app.run(debug=False, host='0.0.0.0', port=80)


if __name__ == "__main__":
    main()
