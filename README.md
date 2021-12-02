# Orbweaver

## Containerized GoBGP and Flask for RESTful access to GoBGP BGP-LS Tables as NetworkX Graph objects

*Yung Tim Allen#1918 @ https://disnog.org/*


![PyLint](https://raster.shields.io/badge/Linting-PyLint-yellow.png)
![Style](https://raster.shields.io/badge/Style-Black-black.png)
 

---

> *"Wherever a topology exists, it should be as a NetworkX Graph."* 
> 
> Wise man, China, c. 700 BC

### What is it?

* 2 component container solution with a docker-compose file
  * GoBGP as a container, with a config file
  * Flask App for providing RESTful endpoints that return BGP-LS LSDB contents in various formats

### What isn't it?

* A tool for manipulating LSDBs
* A tool for advertising anything - it only listens

### Why?

* Intended usecase is for web frontends to get access to topology information easier than gRPC, and to expose topology 
  information as NetworkX objects

### Development Guide

* Black, with line-width 100
* PyLint

### Configuration Files

#### GoBGP

* `gobgp/gobgp.conf.yml` is ADD'd to the container during build. This is where you define neighbors.

#### Orbweaver

* `orbweaver/config.yaml` is used to specify bindings and other settings for the container.

### Usage

1. Pull it
2. Tinker with the GoBGP config
3. `docker-compose -f docker-compose up --build -d`
4. Curl or similar at the exposed endpoints

#### Endpoints

Currently, there are four endpoints defined, with more to come. See: `tests/example.txt` for some Curls.

* `/hosts`
    * list of link-state routers (nodes in the nx object)
* `/lsdb`
    * Contents of cached GoBGP BGP-LS table (updated every `update_interval` seconds (Default: 1))
* `/nx`
    * Above lsdb endpoint but as a NetworkX BiDirGraph object, in JSON format.
    * See: https://networkx.org/documentation/stable/reference/readwrite/json_graph.html

* `/`
    * Renders a page containing the LSDB and a list of link-state routers (nodes in the nx object) 