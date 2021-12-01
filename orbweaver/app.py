#!/usr/bin/env python3
"""Orbweaver, Flask RESTful frontend for GoBGP"""
from flask import Flask, render_template, jsonify
import yaml
from bgp_ls_vis.lsm import LinkStateManager


app = Flask(__name__)
LSM = LinkStateManager(target_ipv4_address="127.0.0.1")


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
    print("Sleep to let GoBGP come up...")
    app.run(debug=False, host="0.0.0.0", port=80)


if __name__ == "__main__":
    main()
