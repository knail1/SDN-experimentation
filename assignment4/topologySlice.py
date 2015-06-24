'''
Coursera:
- Software Defined Networking (SDN) course
-- Network Virtualization

Professor: Nick Feamster
Teaching Assistant: Arpit Gupta

Student: Omer Ansari , 6/21/15, assignment 4
'''

from pox.core import core
from collections import defaultdict

import pox.openflow.libopenflow_01 as of
import pox.openflow.discovery
import pox.openflow.spanning_tree

from pox.lib.revent import *
from pox.lib.util import dpid_to_str
from pox.lib.util import dpidToStr
from pox.lib.addresses import IPAddr, EthAddr
from collections import namedtuple
import os

log = core.getLogger()


class TopologySlice (EventMixin):

    def __init__(self):
        self.listenTo(core.openflow)
        log.debug("Enabling Slicing Module")


    """This event will be raised each time a switch will connect to the controller"""
    def _handle_ConnectionUp(self, event):

        # Use dpid to differentiate between switches (datapath-id)
        # Each switch has its own flow table. As we'll see in this
        # example we need to write different rules in different tables.
        dpid = dpidToStr(event.dpid)
        log.debug("~~~ Switch %s has come up.", dpid)

        """ Add your logic here """
        if dpid == "00-00-00-00-00-01":
            log.debug("~~~ switch %s : Programming forwarding logic", dpid)
            msg = of.ofp_flow_mod()
            msg.priority =20
            match = of.ofp_match()
            msg.match = match
            msg.match.in_port = 3
            msg.actions.append(of.ofp_action_output(port=1))
            log.debug("~~~ switch %s : programmed Rx pkt on port 3, Tx pkt on port 1", dpid)
            event.connection.send(msg)

            msg.match.in_port = 1
            msg.actions.append(of.ofp_action_output(port=3))
            log.debug("~~~ switch %s : programmed Rx pkt on port 1, Tx pkt on port 3", dpid)
            event.connection.send(msg)

            msg.match.in_port = 4
            msg.actions.append(of.ofp_action_output(port=2))
            log.debug("~~~ switch %s : programmed Rx pkt on port 1, Tx pkt on port 3", dpid)
            event.connection.send(msg)

            msg.match.in_port = 2
            msg.actions.append(of.ofp_action_output(port=4))
            log.debug("~~~ switch %s : programmed Rx pkt on port 1, Tx pkt on port 3", dpid)
            event.connection.send(msg)


        if dpid == "00-00-00-00-00-02":
            log.debug("~~~ switch %s : Programming forwarding logic", dpid)
            msg = of.ofp_flow_mod()
            msg.priority =20
            match = of.ofp_match()
            msg.match = match
            msg.match.in_port = 1
            msg.actions.append(of.ofp_action_output(port=2))
            log.debug("~~~ switch %s : programmed Rx pkt on port 3, Tx pkt on port 1", dpid)
            event.connection.send(msg)

            msg.match.in_port = 2
            msg.actions.append(of.ofp_action_output(port=1))
            log.debug("~~~ switch %s : programmed Rx pkt on port 1, Tx pkt on port 3", dpid)
            event.connection.send(msg)

        if dpid == "00-00-00-00-00-03":
            log.debug("~~~ switch %s : Programming forwarding logic", dpid)
            msg = of.ofp_flow_mod()
            msg.priority =20
            match = of.ofp_match()
            msg.match = match
            msg.match.in_port = 1
            msg.actions.append(of.ofp_action_output(port=2))
            log.debug("~~~ switch %s : programmed Rx pkt on port 3, Tx pkt on port 1", dpid)
            event.connection.send(msg)

            msg.match.in_port = 2
            msg.actions.append(of.ofp_action_output(port=1))
            log.debug("~~~ switch %s : programmed Rx pkt on port 1, Tx pkt on port 3", dpid)
            event.connection.send(msg)

        if dpid == "00-00-00-00-00-04":
            log.debug("~~~ switch %s : Programming forwarding logic", dpid)
            msg = of.ofp_flow_mod()
            msg.priority =20
            match = of.ofp_match()
            msg.match = match
            msg.match.in_port = 1
            msg.actions.append(of.ofp_action_output(port=3))
            log.debug("~~~ switch %s : programmed Rx pkt on port 3, Tx pkt on port 1", dpid)
            event.connection.send(msg)

            msg.match.in_port = 3
            msg.actions.append(of.ofp_action_output(port=1))
            log.debug("~~~ switch %s : programmed Rx pkt on port 1, Tx pkt on port 3", dpid)
            event.connection.send(msg)

            msg.match.in_port = 2
            msg.actions.append(of.ofp_action_output(port=4))
            log.debug("~~~ switch %s : programmed Rx pkt on port 1, Tx pkt on port 3", dpid)
            event.connection.send(msg)

            msg.match.in_port = 4
            msg.actions.append(of.ofp_action_output(port=2))
            log.debug("~~~ switch %s : programmed Rx pkt on port 1, Tx pkt on port 3", dpid)
            event.connection.send(msg)


def launch():
    # Run spanning tree so that we can deal with topologies with loops
    pox.openflow.discovery.launch()
    pox.openflow.spanning_tree.launch()

    '''
    Starting the Topology Slicing module
    '''
    core.registerNew(TopologySlice)


