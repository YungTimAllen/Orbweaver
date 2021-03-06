"""gRPC tools and definitions"""
# Standard Imports
from json import loads, dumps
import yaml
from google.protobuf.json_format import MessageToDict

# RPC & GoBGP imports
import grpc
from . import gobgp_pb2 as gobgp
from . import gobgp_pb2_grpc
from . import attribute_pb2


class GoBGPQueryWrapper:
    """Class to add abstraction for RPC calls to a GoBGP Instance"""

    def __init__(
        self,
        target_ipv4_address: str = "",
        target_rpc_port: int = "",
        connect: bool = True,
    ):
        """Constructor initialises RPC session

        Args:
            target_ipv4_address: Management IPv4 Address of GoBGP instance
            target_rpc_port: Management Port of GoBGP Instance
            connect: When set false, will not build grpc channel or api stub objects

        Todo: Default parameters need some sanitation
        """
        if connect:
            channel = grpc.insecure_channel(f"{target_ipv4_address}:{target_rpc_port}")
            self.stub = gobgp_pb2_grpc.GobgpApiStub(channel)

    @staticmethod
    def __build_rpc_request() -> gobgp.ListPathRequest:
        """Builds a structured message for RPC query to get BGP-LS table

        Returns:
            gobgp.ListPathRequest: Structured message for RPC query
        """
        request = gobgp.ListPathRequest(
            table_type=gobgp.LOCAL,
            name="",
            family=gobgp.Family(afi=gobgp.Family.AFI_LS, safi=gobgp.Family.SAFI_LS),
            prefixes=None,
            sort_type=True,
        )
        return request

    def __get_bgp_ls_table(self) -> list:
        """Submits RPC query (structured message) for BGP-LS table

        Sends gobgp.ListPathRequest object over RPC session to get BGP-LS NLRI objects

        Returns:
            List of NLRI objects for the BGP-LS AFI/SAFI

        Notes:
            To build required structured message, calls __build_rpc_request() first
        """
        request = self.__build_rpc_request()
        response = self.stub.ListPath(request)
        rtn = [MessageToDict(nlri) for nlri in response]
        return rtn

    def debug(self) -> list:
        """Dumps the raw BGP-LS table received from GoBGP"""
        return self.__get_bgp_ls_table()

    def get_lsdb(self, best_only: bool = True, filename: str = None) -> list:
        """Gets the LSDB from the BGP-LS, including a gRPC call to GoBGP. LSDB can also be loaded from a file."""
        # Get the whole brib for ls
        gobgp_ls_table = (
            self.__get_bgp_ls_table()
            if not filename
            else yaml.load(open(filename, "r"), Loader=yaml.Loader)
        )

        # Filter for only best-paths
        b_rib = []
        for route in gobgp_ls_table:
            destination = route["destination"]
            for path in destination["paths"]:
                if best_only:
                    if path["best"]:
                        b_rib.append(path)
                else:
                    b_rib.append(path)

        # Find and replace dict for ugly grpc naming convention
        gapi_type_replace_lookup = {
            "type.googleapis.com/gobgpapi.OriginAttribute": "OriginAttribute",
            "type.googleapis.com/gobgpapi.AsPathAttribute": "AsPathAttribute",
            "type.googleapis.com/gobgpapi.MultiExitDiscAttribute": "MultiExitDiscAttribute",
            "type.googleapis.com/gobgpapi.LocalPrefAttribute": "LocalPrefAttribute",
            "type.googleapis.com/gobgpapi.LsAttribute": "LsAttribute",
            "type.googleapis.com/gobgpapi.MpReachNLRIAttribute": "MpReachNLRIAttribute",
            "type.googleapis.com/gobgpapi.LsPrefixV4NLRI": "LsPrefixV4NLRI",
            "type.googleapis.com/gobgpapi.LsLinkNLRI": "LsLinkNLRI",
            "type.googleapis.com/gobgpapi.LsNodeNLRI": "LsNodeNLRI",
        }

        # If you load a nest of different types, some of which are collections.OrderedDict,
        # you can recurse and cast these as dict ... or dump -> load it as Json to just
        # cast them all
        def remove_ordered_dicts(input_ordered_dict):
            return loads(dumps(input_ordered_dict))

        # If you want to replace keys and values in nested dicts, but dont want to recurse,
        # json.dump then find/replace on the string, then load back to a dict
        def replace_kv_in_dict(t_dict, item_to_be_replaced, replaced_with):
            return loads(dumps(t_dict).replace(f'"{item_to_be_replaced}"', f'"{replaced_with}"'))

        new_table = remove_ordered_dicts(b_rib)
        new_table = replace_kv_in_dict(new_table, "@type", "type")
        # Rename all keys using lookup dict gapi_type_replace_lookup
        for old_key, new_key in gapi_type_replace_lookup.items():
            new_table = replace_kv_in_dict(new_table, old_key, new_key)

        # A list of single-item non-duplicate dicts is no-good, so flatten it
        # Single item dicts have a key of 'type:', which is what we flatten on
        for path in new_table:
            pattrs_flat = {}
            for pattr in path["pattrs"]:
                pattrs_flat[pattr["type"]] = {}
                for key, value in pattr.items():
                    if key != "type":
                        pattrs_flat[pattr["type"]][key] = value
            path["pattrs"] = pattrs_flat

        # Finally, we bring some values to the root to assist in various tasks (qol)
        for path in new_table:
            # IGP metric, for spf pathcalc
            if path["nlri"]["nlri"]["type"] == "LsLinkNLRI":
                path["igpMetric"] = path["pattrs"]["LsAttribute"]["link"]["igpMetric"]
            # set key 'name' value to t137 value if it exits,
            # else, set it to regular router-id (thats an nsap for isis)
            # (note that the networkx node in the graph object is named by igpRouterId regardless)
            if path["nlri"]["nlri"]["type"] == "LsNodeNLRI":
                path["name"] = path["pattrs"]["LsAttribute"]["node"].get(
                    "name", path["nlri"]["nlri"]["localNode"]["igpRouterId"]
                )

        print(yaml.dump(new_table))

        return new_table
