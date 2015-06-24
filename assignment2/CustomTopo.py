#!/usr/bin/python

'''Coursera:
- Software Defined Networking (SDN) course
-- Programming Assignment 2

Professor: Nick Feamster
Teaching Assistant: Arpit Gupta, Muhammad Shahbaz

Code updated by : Omer Ansari (oansari@gmail.com) 6/7/15
'''

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import setLogLevel
from mininet.util import irange,dumpNodeConnections
from mininet.link import TCLink

class CustomTopo(Topo):
    "Simple Data Center Topology"

    "linkopts - (1:core, 2:aggregation, 3: edge) parameters"
    "fanout - number of child switch per parent switch"
    def __init__(self, linkopts1, linkopts2, linkopts3, fanout=2, **opts):
        # Initialize topology and default options
        Topo.__init__(self, **opts)
        
        # Add your logic here ...

        # changed LinearTopo to TreeTopo, not sure what difference this makes)
        super(CustomTopo, self).__init__(**opts)

        self.fanout = fanout
        switchFanOut = fanout
        edgeSwitchFanOut = fanout
        hostFanOut = fanout



        #lastSwitch = None
        # create core switch
        coreSwitch = self.addSwitch('c1')

        #now start logic of creating tree under the root (i.e. core switch)
        for asfo in irange(1, switchFanOut):
            aggSwitch = self.addSwitch('a%s' % asfo)
            for esfo in irange(1+fanout*(asfo-1), edgeSwitchFanOut+fanout*(asfo-1)):
                edgeSwitch = self.addSwitch('e%s' % esfo)
                for hfo in irange(1+fanout*(esfo-1), hostFanOut+fanout*(esfo-1)):
                    host = self.addHost('h%s' % hfo)
                    self.addLink(host, edgeSwitch, **linkopts3)
                self.addLink(edgeSwitch, aggSwitch, **linkopts2)
            self.addLink(coreSwitch, aggSwitch, **linkopts1)


           ## self.addLink(node1, node2, **linkopts)
           #if lastSwitch:
           #    self.addLink(switch, lastSwitch, bw=10, delay='5ms', loss=1, max_queue_size=1000, use_htb=True)
           #lastSwitch = switch


            #host = self.addHost('h%s' % i, cpu=.5/k)
            # 10 Mbps, 5ms delay, 1% loss, 1000 packet queue
            #self.addLink( host, switch, bw=10, delay='5ms', loss=1, max_queue_size=1000, use_htb=True)


def dcFabric():
    " Create network and run simple performance test"
    print "a. Setting link parameters"
    "--- core to aggregation switches"
    linkopts1 = {'bw':50, 'delay':'5ms'}
    "--- aggregation to edge switches"
    linkopts2 = {'bw':30, 'delay':'10ms'}
    "--- edge switches to hosts"
    linkopts3 = {'bw':10, 'delay':'15ms'}

    topo = CustomTopo(linkopts1, linkopts2, linkopts3, fanout=3)
    #net = Mininet(topo=topo,
    #              host=CPULimitedHost, link=TCLink)
    net = Mininet(topo=topo, link=TCLink)
    net.start()
    print "Dumping host connections"
    dumpNodeConnections(net.hosts)
    print "Testing network connectivity"
    net.pingAll()
    print "Testing bandwidth between h1 and h4"
    #h1, h4 = net.get('h1', 'h4')
    #net.iperf((h1, h4))
    net.stop()


topos = { 'custom': ( lambda: CustomTopo() ) }


if __name__ == '__main__':
   setLogLevel('info')
   dcFabric()
