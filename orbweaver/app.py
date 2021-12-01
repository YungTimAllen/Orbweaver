#!/usr/bin/env python3
""""""
from flask import Flask, render_template, jsonify
from time import sleep
import yaml
from bgp_ls_vis.lsm import LinkStateManager


app = Flask(__name__)
LSM = LinkStateManager(target_ipv4_address="127.0.0.1")


@app.route("/")
def home():
    return render_template(
        "home.html",
        title="LSDB Report",
        hosts_list=str(LSM.get_hosts()),
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
    return jsonify(LSM.get_graph())


def main():
    print("Sleep to let GoBGP come up...")
    sleep(5)
    app.run(debug=False, host="0.0.0.0", port=80)


if __name__ == "__main__":
    main()
