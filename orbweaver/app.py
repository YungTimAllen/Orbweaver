#!/usr/bin/env python3
"""Orbweaver, Flask RESTful frontend for GoBGP"""
import sys
from os.path import isfile
from flask import Flask, render_template, jsonify
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
    return render_template(
        "home.html",
        title="LSDB Report",
        hosts_list=str(LSM.get_hosts()),
        lsdb=yaml.dump(LSM.get_lsdb()),
    )


@app.route("/hosts")
def rest_get_hosts():
    """Flask endpoint to return all nodes in the LSDB graph"""
    return jsonify(LSM.get_hosts())


@app.route("/lsdb")
def rest_get_lsdb():
    """Flask endpoint to return the LSDB as gleaned from GoBGP's BGP-LS table"""
    return jsonify(LSM.get_lsdb())


@app.route("/nx")
def rest_get_networkx_graph():
    """Flask endpoint to return the LSDB as a NetworkX BiDirGraph object in JSON format"""
    return jsonify(LSM.get_graph())


def main():
    """Entrypoint when ran as a script"""

    app.run(debug=False, host=CONF["flask_bind_ip"], port=CONF["flask_bind_port"])


if __name__ == "__main__":
    main()
