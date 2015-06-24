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
portmap = {}

class VideoSlice (EventMixin):

    def __init__(self):
        self.listenTo(core.openflow)
        core.openflow_discovery.addListeners(self)

        # Adjacency map.  [sw1][sw2] -> port from sw1 to sw2
        self.adjacency = defaultdict(lambda:defaultdict(lambda:None))

        '''
        The structure of self.portmap is a four-tuple key and a string value.
        The type is:
        (dpid string, src MAC addr, dst MAC addr, port (int)) -> dpid of next switch
        '''

        self.portmap = {
                        #switch 1, video
                        ('00-00-00-00-00-01', EthAddr('00:00:00:00:00:01'),
                         EthAddr('00:00:00:00:00:03'), 80): '00-00-00-00-00-03',


                        ('00-00-00-00-00-01', EthAddr('00:00:00:00:00:01'),
                         EthAddr('00:00:00:00:00:04'), 80): '00-00-00-00-00-03',

                        ('00-00-00-00-00-01', EthAddr('00:00:00:00:00:02'),
                         EthAddr('00:00:00:00:00:03'), 80): '00-00-00-00-00-03',

                        ('00-00-00-00-00-01', EthAddr('00:00:00:00:00:02'),
                         EthAddr('00:00:00:00:00:04'), 80): '00-00-00-00-00-03',



                        #switch 1 non video (port80), marked as tcp port 0:
                        ('00-00-00-00-00-01', EthAddr('00:00:00:00:00:01'),
                         EthAddr('00:00:00:00:00:03'), 0): '00-00-00-00-00-02',

                        ('00-00-00-00-00-01', EthAddr('00:00:00:00:00:01'),
                         EthAddr('00:00:00:00:00:04'), 0): '00-00-00-00-00-02',

                        ('00-00-00-00-00-01', EthAddr('00:00:00:00:00:02'),
                         EthAddr('00:00:00:00:00:03'), 0): '00-00-00-00-00-02',

                        ('00-00-00-00-00-01', EthAddr('00:00:00:00:00:02'),
                         EthAddr('00:00:00:00:00:04'), 0): '00-00-00-00-00-02',

                        #switch 4, video
                        ('00-00-00-00-00-04', EthAddr('00:00:00:00:00:03'),
                         EthAddr('00:00:00:00:00:01'), 80): '00-00-00-00-00-03',

                        ('00-00-00-00-00-04', EthAddr('00:00:00:00:00:03'),
                         EthAddr('00:00:00:00:00:02'), 80): '00-00-00-00-00-03',

                        ('00-00-00-00-00-04', EthAddr('00:00:00:00:00:04'),
                         EthAddr('00:00:00:00:00:01'), 80): '00-00-00-00-00-03',

                        ('00-00-00-00-00-04', EthAddr('00:00:00:00:00:04'),
                         EthAddr('00:00:00:00:00:02'), 80): '00-00-00-00-00-03',

                        #switch 4 non video (port80), marked as tcp port 0:
                        ('00-00-00-00-00-04', EthAddr('00:00:00:00:00:03'),
                         EthAddr('00:00:00:00:00:01'), 0): '00-00-00-00-00-02',

                        ('00-00-00-00-00-04', EthAddr('00:00:00:00:00:03'),
                         EthAddr('00:00:00:00:00:02'), 0): '00-00-00-00-00-02',

                        ('00-00-00-00-00-04', EthAddr('00:00:00:00:00:04'),
                         EthAddr('00:00:00:00:00:01'), 0): '00-00-00-00-00-02',

                        ('00-00-00-00-00-04', EthAddr('00:00:00:00:00:04'),
                         EthAddr('00:00:00:00:00:02'), 0): '00-00-00-00-00-02',

                        }


    def _handle_LinkEvent (self, event):
        l = event.link
        sw1 = dpid_to_str(l.dpid1)
        sw2 = dpid_to_str(l.dpid2)

        log.debug ("~~~ link %s[%d] <-> %s[%d]",
                   sw1, l.port1,
                   sw2, l.port2)

        self.adjacency[sw1][sw2] = l.port1
        self.adjacency[sw2][sw1] = l.port2
        log.debug("~~~ adjacency from %s to %s is %d", sw1, sw2, self.adjacency[sw1][sw2])



    def _handle_PacketIn (self, event):
        """
        Handle packet in messages from the switch to implement above algorithm.
        """
        packet = event.parsed
        self.tcpp = event.parsed.find('tcp')
        self.event = event
        self.nextHop = ''




        def install_fwdrule(event,packet,outport):
            msg = of.ofp_flow_mod()
            msg.idle_timeout = 10
            msg.hard_timeout = 30
            msg.match = of.ofp_match.from_packet(packet, event.port)
            msg.actions.append(of.ofp_action_output(port = outport))
            msg.data = event.ofp
            msg.in_port = event.port
            event.connection.send(msg)
        def forward (message = None):
            this_dpid = dpid_to_str(event.dpid)


            if packet.dst.is_multicast:
                flood()
                return
            else:
                #log.debug("~~~~ Got unicast packet for DEST %s at switch %s (input port %s):",
                #          str(packet.dst), dpid_to_str(event.dpid), str(event.port))

                try:
                # check for dest port there may not be one since its a BPDU:
                    if not (packet.find('tcp').dstport):
                        log.debug("~~~ received packet not a tcp packet")
                        return
                    else:
                        tcpDestPort = event.parsed.find('tcp').dstport

                        """ Add your logic here"""
                        theTuple = (this_dpid, packet.src, packet.dst, tcpDestPort)
                        log.debug("~~~ Switch ID: %s, src: %s, dest: %s, dport: %s", this_dpid, packet.src, packet.dst ,tcpDestPort)
                        #log.debug("~~~ complete portmap: %s", self.portmap)

                        #log.debug("~~~ the variable self globalPortMap theTuple %s", self.globalPortmap[theTuple])
                        if (tcpDestPort != 80):
                            log.debug("~~~ dest port isn't 80")
                            theTuple = (this_dpid, packet.src, packet.dst, 0)
                            log.debug("~~~ theTuple: %s", theTuple)
                        if (self.portmap[theTuple]):
                            nextHop = self.portmap[theTuple]
                            log.debug("~~~ TUPLE MATCHED! next hop is %s", nextHop)
                            #log.debug("~~~ first swtich is %s", self.portmap[theTuple][0])
                            switch1 = this_dpid
                            switch2 = nextHop
                            nextPort = self.adjacency[switch1][switch2]
                            log.debug("~~~ switch1: %s going to switch: %s via nextPort: %s", switch1, switch2, nextPort)
                            #log.debug("~~~~ sw: %s: explicit match found, sending packet src %s, dst %s, port %s, to next-hop %s", dpid, packet.src, packet.dst, tcpp.dstport, nextHop)
                            install_fwdrule(event,packet,nextPort)

                            #check if this matches with portmap key, and if so,
                            #get the next hop dpid , and
                            #install that as a rule in install_fwdrule

                except AttributeError:
                        log.debug("packet type has no transport ports, flooding")
                        log.debug("~~~ error message: %s", AttributeError.message)
                        # flood and install the flow table entry for the flood
                        install_fwdrule(event,packet,of.OFPP_FLOOD)

        # flood, but don't install the rule
        def flood (message = None):
            """ Floods the packet """
            msg = of.ofp_packet_out()
            msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
            msg.data = event.ofp
            msg.in_port = event.port
            event.connection.send(msg)

        forward()


    def _handle_ConnectionUp(self, event):
        dpid = dpidToStr(event.dpid)
        log.debug("~~~ Switch %s has come up.", dpid)

        if dpid == "00-00-00-00-00-01":
            log.debug("~~~ switch %s : Programming forwarding logic", dpid)
            msg = of.ofp_flow_mod()
            msg.priority =20
            match = of.ofp_match()
            msg.match = match
            msg.match.dl_dst = EthAddr("00-00-00-00-00-01")
            msg.actions.append(of.ofp_action_output(port=3))
            log.debug("~~~ switch %s : programmed traffic going to 00-00-00-00-00-01 out port 3", dpid)
            event.connection.send(msg)

            msg.match.dl_dst = EthAddr("00-00-00-00-00-02")
            msg.actions.append(of.ofp_action_output(port=4))
            log.debug("~~~ switch %s : programmed traffic going to 00-00-00-00-00-02 out port 4", dpid)
            event.connection.send(msg)


        if dpid == "00-00-00-00-00-02":
            log.debug("~~~ switch %s : Programming PORT forwarding logic", dpid)
            msg = of.ofp_flow_mod()
            msg.priority =20
            match = of.ofp_match()
            msg.match = match
            msg.match.in_port = 1
            msg.actions.append(of.ofp_action_output(port=2))
            log.debug("~~~ switch %s : programmed Rx pkt on port 1, Tx pkt on port 2", dpid)
            event.connection.send(msg)

            msg.match.in_port = 2
            msg.actions.append(of.ofp_action_output(port=1))
            log.debug("~~~ switch %s : programmed Rx pkt on port 2, Tx pkt on port 1", dpid)
            event.connection.send(msg)

        if dpid == "00-00-00-00-00-04":
            log.debug("~~~ switch %s : Programming forwarding logic", dpid)
            msg = of.ofp_flow_mod()
            msg.priority =20
            match = of.ofp_match()
            msg.match = match
            msg.match.dl_dst = EthAddr("00-00-00-00-00-03")
            msg.actions.append(of.ofp_action_output(port=3))
            log.debug("~~~ switch %s : programmed traffic going to 00-00-00-00-00-03 out port 3", dpid)
            event.connection.send(msg)

            msg.match.dl_dst = EthAddr("00-00-00-00-00-04")
            msg.actions.append(of.ofp_action_output(port=4))
            log.debug("~~~ switch %s : programmed traffic going to 00-00-00-00-00-04 out port 4", dpid)
            event.connection.send(msg)


        if dpid == "00-00-00-00-00-03":
            log.debug("~~~ switch %s : Programming PORT forwarding logic", dpid)
            msg = of.ofp_flow_mod()
            msg.priority =20
            match = of.ofp_match()
            msg.match = match
            msg.match.in_port = 1
            msg.actions.append(of.ofp_action_output(port=2))
            log.debug("~~~ switch %s : programmed Rx pkt on port 1, Tx pkt on port 2", dpid)
            event.connection.send(msg)

            msg.match.in_port = 2
            msg.actions.append(of.ofp_action_output(port=1))
            log.debug("~~~ switch %s : programmed Rx pkt on port 2, Tx pkt on port 1", dpid)
            event.connection.send(msg)



def launch():
    # Run spanning tree so that we can deal with topologies with loops
    pox.openflow.discovery.launch()
    pox.openflow.spanning_tree.launch()

    '''
    Starting the Video Slicing module
    '''
    core.registerNew(VideoSlice)
