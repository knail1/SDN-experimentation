# Network Virtualization Assignment
In this assignment, you will learn how to slice your OpenFlow network using the "Pox" OpenFlow controller. In the process, you will also learn more about the concept of flowspaces and how the centralized visibility and “layerless-ness” of OpenFlow enables flexible slicing.

The purpose of this exercise is to help motivate network virtualization and show you different ways in which network virtualization can be implemented. In the lessons, you learned about [FlowVisor](http://www.google.com/url?q=http%3A%2F%2Fflowvisor.org%2F&sa=D&sntz=1&usg=AFQjCNFJU6x1ptpARocpGc4OtC-HuBZadw), a mechanism for allowing multiple controllers to operate on distinct portions of network flowspace. Flowvisor is implemented in Java, which would require you to install a completely new tool and operating environment. In lieu of doing so, we have created a simpler assignment that illustrates some of the concepts of slicing that Flowvisor uses. We encourage you to follow the</span> <span class="c29">[Flowvisor Tutorial](https://www.google.com/url?q=https%3A%2F%2Fgithub.com%2Fonstutorial%2Fonstutorial%2Fwiki%2FFlowvisor-Exercise&sa=D&sntz=1&usg=AFQjCNFRaHgFZASUPXLOoioC9XvPI5TzXg)</span><span class="c6"> if you are interested in playing specifically with FlowVisor.</span>

<span class="c6">The Flowvisor tutorial teaches you how to create multiple network slices and control different slices with different controllers. Here, because we are going to implement everything directly in Pox, your task is simpler: You will create a network application that creates multiple Layer 2 network slices for different portions of the flowspace.</span>

<span class="c6">Read further for instructions on creating and submitting your code. Make sure that you follow each step carefully.</span>

## <a name="h.l5apm79xi1jj"></a><span class="c6 c17">Setup</span>

<span></span>

![](https://docs.google.com/drawings/d/15Hq3NTUElJvEh5lHu1eeoXysUY3gjUb0IjHgZ-DiIJ8/pub?w=481&h=231 "https://docs.google.com/drawings/d/15Hq3NTUElJvEh5lHu1eeoXysUY3gjUb0IjHgZ-DiIJ8/pub?w=481&h=231")

<span class="c4">Figure 1: Network Topology</span>

## <a name="h.le3k34tab4o5"></a><span class="c16">Creating Topology</span>

<span class="c6">In this assignment we will slice a wide-area network (WAN). The WAN shown in the figure above connects two sites. For simplicity, we’ll have each site represented by a single OpenFlow switch, s1 and s4, respectively. The sites, s1 and s4, have two paths between them:</span></span>

*   <span class="c6">a low-bandwidth path via switch s2</span>
*   <span class="c6">a high-bandwidth path via switch s3</span>

<span class="c6">Switch s1 has two hosts attached: h1 and h2, and s4 has two hosts attached: h3 and h4.</span>

<span class="c6">As a quick refresher, remember to always ensure that there is no other controller running in the background. Check if any controller is running in the background.</span>

<span class="c10">$</span> <span class="c3">ps -A | grep controller  
</span>

<span class="c6">Kill the controller in case any of them is still running.</span>

<span class="c10">$</span> <span class="c3">sudo killall controller  
</span>

<span class="c6">Restart Mininet to make sure that everything is clean and using the faster kernel switch.</span>

<span class="c10">$</span> <span class="c3">sudo mn -c  
</span>

<span class="c6">We'll use a Mininet script,</span> <span class="c1">mininetSlice.py</span><span class="c6">, to create a network with the topology provided above. The topology we have provided should correspond to the one shown in the figure above, although for the second part of the assignment we have used Pox's link-layer discovery protocol (LLDP) features to ensure that you can complete the assignment without ever explicitly referring to port numbers.</span>

<span class="c41">self</span><span class="c3 c13">.</span><span class="c3">addLink(</span><span class="c15">'s1'</span><span class="c3">,</span> <span class="c15">'s2'</span><span class="c3">, port1</span> <span class="c3 c13">=</span><span class="c3"> </span><span class="c25">1</span><span class="c3">, port2</span> <span class="c3 c13">=</span><span class="c3"> </span><span class="c25">1</span><span class="c3">,</span> <span class="c3 c13">**</span><span class="c3">http_link_config)  
</span>

## <a name="h.f8z2bssocptb"></a><span class="c6 c17">Code Overview</span>

<span class="c6">The assignment has two parts, (1) simple topology-based slicing and (2) advanced flowspace slicing. To get started, download the zip file for the assignment([virtualization-assignment](https://d396qusza40orc.cloudfront.net/sdn/srcs/virtualization-assignment.zip)). It consists of four files:</span>

*   <span class="c1">mininetSlice.py</span><span class="c6">: Mininet script to create the topology used for this assignment.</span>
*   <span class="c1">topologySlice.py</span><span class="c6">: A skeleton class where you will implement simple topology-based slicing logic.</span>
*   <span class="c1">videoSlice.py</span><span class="c6">: A skeleton class where you will implement advanced flowspace slicing logic.</span>
*   <span class="c1">submit.py</span><span class="c6">: The submission script to submit your assignment's output to the Coursera servers.</span>

<span class="c6">We'll now see how you will use these files to run the exercise and submit your assignment.</span>

### Part 1: Topology-based Slicing

<span class="c6">The first part of the assignment should give you a basic understanding of how to "slice" a network using a SDN controller. The goal of this part is to divide the network into two separate slices: upper and lower, as shown below. Users in different slices should not be able to communicate with each other. In practice, a provider may want to subdivide the network in this fashion to support multi-tenancy (and, in fact, the first part of this assignment provides similar functionality as ordinary VLANs).</span>
<span></span>
![](https://docs.google.com/drawings/d/1mdFRYvi4QdjzYRpc5KNitDIwUToWjIVGwZNRD6vAejQ/pub?w=480&h=360 "https://docs.google.com/drawings/d/1mdFRYvi4QdjzYRpc5KNitDIwUToWjIVGwZNRD6vAejQ/pub?w=480&h=360")
<span class="c4">Figure 2: Sliced Topology</span>

To implement this isolation, we need to block communication between hosts in different slices. You will implement this functionality by judiciously inserting drop rules at certain network switches. For example, host h1 should not be able to communicate to host h2\. To implement this restriction, you should write OpenFlow rules that provide this isolation. (Unlike previous assignment, this topology has multiple switches; each switch has its own flow table; the controller uses each switch's datapath ID to write flow rules to the appropriate switch.)</span></span>

### Understanding the code

<span class="c6">The</span> <span class="c1">topologySlice.py</span><span class="c6"> file provides skeleton for this implementation. As in the previous assignment, we have implemented a</span> <span class="c1">launch()</span><span class="c6"> function, which registers a new component. The</span><span class="c1">_handle_ConnectionUp()</span><span class="c6"> callback is invoked whenever a switch connects to the controller.</span>

<span class="c6">We also launch the</span> <span class="c1">discovery</span><span class="c6"> and</span> <span class="c1">spanning tree</span><span class="c6"> modules, which compute a spanning tree on the topology, thus preventing any traffic that is flooded from looping (since the topology itself has a loop in it, computing a spanning tree is required). More information about these modules is available here:</span> <span class="c29">[Spanning Tree](https://www.google.com/url?q=https%3A%2F%2Fgithub.com%2Fnoxrepo%2Fpox%2Fblob%2Fcarp%2Fpox%2Fopenflow%2Fspanning_tree.py&sa=D&sntz=1&usg=AFQjCNGEXDxrx7W3wIS6LWzzQawmaiYYsQ)</span><span class="c6">,</span> <span class="c29">[Discovery](https://www.google.com/url?q=https%3A%2F%2Fgithub.com%2Fnoxrepo%2Fpox%2Fblob%2Fcarp%2Fpox%2Fopenflow%2Fdiscovery.py&sa=D&sntz=1&usg=AFQjCNH8OK0VcJLRAqLNDXFAHVa6y5kNSA)</span>

### <a name="h.as89dknr9eyb"></a><span class="c6 c23">Testing your code</span>

<span class="c6">Once you have implemented the logic for topology based-slicing, you can test it following these instructions:</span>

<span class="c6">Move your files to POX's directory,</span> <span class="c1">~/pox/pox/misc</span><span class="c6">. This should prevent any potential</span> <span class="c1">PYTHONPATH</span><span class="c6"> issues you might encounter.</span>

<span class="c10">$</span> <span class="c3">mv topologySlice.py ~/pox/pox/misc/  
</span><span class="c10">$</span> <span class="c3">mv mininetSlice.py ~/pox/pox/misc/  
</span>

<span class="c6">Launch the POX controller.</span>

<span class="c3">~/pox/pox/misc</span><span class="c10">$</span> <span class="c3">pox.py log.level --DEBUG misc.topologySlice &  
</span>

<span class="c6">In a separate terminal, launch your Mininet script.</span>

<span class="c3">~/pox/pox/misc</span><span class="c10">$</span> <span class="c3">sudo python mininetSlice.py  
</span>

<span class="c6">Wait until the application indicates that the OpenFlow switch has connected and that all spanning tree computation has finished. You should see some messages such as</span> <span class="c1">DEBUG:openflow.spanning_tree:Requested switch features for [00-00-00-00-00-03 4]</span><span class="c6"> after a while, possibly followed by some flooding.</span>

<span class="c6"></span>

<span class="c6">Now, verify that the hosts in different slices are not able to communicate with each other.</span>

<span class="c3">mininet> pingall  
</span>

<span class="c6">You should see the following output:</span>

<span class="c3">h1 -> X h3 X   
h2 -> X X h4   
h3 -> h1 X X   
h4 -> X h2 X   
*** Results: 66% dropped</span> <span class="c3 c13">(</span><span class="c3">8/12 lost</span><span class="c3 c13">)</span><span class="c3">  
</span>

## <a name="h.ccnt2mtmape2"></a><span class="c6 c17">Part 2: Flowspace Slicing</span>

<span class="c6">In the previous part of the assignment, you learned how to slice a network based on the network's physical topology. It is also possible to slice the network in more interesting ways, such as based on the application that is sending the traffic. SDN networks in principle can be sliced on any attributes of flowspace.</span>

<span class="c6">Recall that the topology has two paths connecting two sites: a high-bandwidth path and a low-bandwidth path. Suppose that you want to prioritize video traffic in our network by sending all the video traffic over the high bandwidth path, and sending all the other traffic over the default low bandwidth path. File transfers won't be affected by the video traffic, and vice versa. In this part of the assignment, you'll use network slicing to implement this isolation.</span>

<span class="c6">Let's assume for simplicity that all video traffic goes on TCP port 80\. In this assignment you are required to write the logic to create two slices, "video" and "non-video", as shown below.</span>

</span></p><h3 class=](https://docs.google.com/drawings/d/1LANqW077ndKlSEuRQDNBTaepq3Ts0fidn7Ev4n8Egeo/pub?w=518&h=453)<a name="h.6y914md5x0zl"></a>

<span></span>
![](https://docs.google.com/drawings/d/1LANqW077ndKlSEuRQDNBTaepq3Ts0fidn7Ev4n8Egeo/pub?w=518&h=453 "https://docs.google.com/drawings/d/1LANqW077ndKlSEuRQDNBTaepq3Ts0fidn7Ev4n8Egeo/pub?w=518&h=453")
<span class="c4">Figure 3: Video Slicing</span>


### Understanding your code

<span class="c6">In</span> <span class="c1">videoSlice.py</span><span class="c6">, you have a class called (</span><span class="c1">VideoSlice</span><span class="c6">). We have provided you with some of the logic to implement slicing. You should fill in the</span> <span class="c1">portmap</span><span class="c6"> data structure and the missing parts of the</span> <span class="c1">forward</span><span class="c6"> function. We have included a line of the portmap data structure as a hint: the data structure should map a switch and a portion of flowspace to the dpid of the next switch. You will need to figure out how to implement a wildcard, in addition to explicit flowspace directives for port 80.</span>

[](#)[](#)

<table cellpadding="0" cellspacing="0" class="c24">

<tbody>

<tr class="c33">

<td class="c40">

<span class="c2">       '''</span>

<span class="c2">       The structure of self.portmap is a four-tuple key and a string value.</span>

<span class="c2">       The type is:</span>

<span class="c2">       (dpid string, src MAC addr, dst MAC addr, port (int)) -> dpid of next switch</span>

<span class="c2">       '''</span>

<span class="c8 c6">       </span> <span class="c8 c34">self</span><span class="c8 c6 c13">.</span><span class="c8 c6">portmap</span> <span class="c8 c6 c13">=</span><span class="c8 c6 c9"> {</span>

<span class="c8 c6">                        (</span><span class="c8 c21">'00-00-00-00-00-01'</span><span class="c8 c6">, EthAddr(</span><span class="c8 c21">'00:00:00:00:00:01'</span><span class="c9 c8 c6">),</span>

<span class="c8 c6">                         EthAddr(</span><span class="c8 c21">'00:00:00:00:00:03'</span><span class="c8 c6">),</span> <span class="c8 c12">80</span><span class="c6 c8">):</span> <span class="c8 c21">'00-00-00-00-00-03'</span><span class="c9 c8 c6">,</span>

<span class="c9 c8 c6">                ...</span>

</td>

</tr>

</tbody>

</table>

<span class="c6"></span>

<span class="c6">The discovery module that we discussed above also passes information to the Pox controller about the topology, such as the switches that it knows about, and the ports of each switch that are connected to one another. This discovery protocol, link-layer discovery protocol (LLDP), is useful for part 2 of the assignment, but we've included the code to do that discovery for you. You can look at the skeleton code for an example of how LLDP is used (see the</span> <span class="c1">handleLinkEvent</span><span class="c6"> function). The</span> <span class="c8 c19">[l2_multi.py](https://www.google.com/url?q=https%3A%2F%2Fgithub.com%2Fnoxrepo%2Fpox%2Fblob%2Fcarp%2Fpox%2Fforwarding%2Fl2_multi.py&sa=D&sntz=1&usg=AFQjCNHBlxGR8Efot7Uj-P7zOQZcif9Rig)</span><span class="c6"> module in the Pox distribution, which performs Layer 2 learning for multiple switches in a single topology, also makes use of LLDP.</span>

<span class="c6">Another possible hint is that because the controller runs a spanning tree protocol (you should familiarize yourself with what this does and why we have included it, if you haven't already), simply flooding from certain switches in the network as default behavior may not work. (In other words, if you find packets not getting through, consider being explicit in your portmap structure.)</span>

### <a name="h.avav7xaw28ie"></a><span class="c6 c23">Testing your code</span>

<span class="c6">Once you are done updating the video slice component, you can test it as follows:</span>

<span class="c6">As above, make sure that your</span> <span class="c1">videoSlice.py</span><span class="c6"> and</span> <span class="c1">mininetSlice.py</span><span class="c6"> are in same directory (i.e.</span><span class="c1">~/pox/pox/misc</span><span class="c6">).</span>

<span class="c6"></span>

<span class="c6">Launch the POX controller</span>

<span class="c3">~/pox/pox/misc</span><span class="c10">$</span> <span class="c3">pox.py log.level --DEBUG misc.videoSlice  
</span>

<span class="c6">In a separate terminal, launch your Mininet script.</span>

<span class="c3">~/pox/pox/misc</span><span class="c10">$</span> <span class="c3">sudo python mininetSlice.py  
</span>

<span class="c6">Wait until the application indicates that the OpenFlow switch has connected.</span>

<span class="c6"></span>

<span class="c6">Now verify that the all the hosts are able to communicate with each other. This is a simple sanity check to make sure that your logic is not affecting connectivity in general.</span>

<span class="c3">mininet> pingall  
</span>

<span class="c6">You should see this output:</span>

<span class="c3">mininet> pingall  
*** Ping: testing ping reachability  
h1 -> h2 h3 h4   
h2 -> h1 h3 h4   
h3 -> h1 h2 h4   
h4 -> h1 h2 h3   
*** Results: 0% dropped</span> <span class="c3 c13">(</span><span class="c3">12/12 received</span><span class="c3 c13">)</span><span class="c3">  
</span>

<span class="c6">You can now test that your slices work properly be ensuring that video (in this case, port 80) traffic traverses the 10 Mbps link and non-port 80 traffic traverses the 1 Mbps link. For example, you can test the two paths between h2 and h3 as below. (Your code should work for</span> <span class="c6 c37">all</span><span class="c6"> pairwise paths.)</span>

<span class="c3">mininet > h3 iperf -s -p</span> <span class="c25">80</span><span class="c3"> &  
mininet > h3 iperf -s -p</span> <span class="c25">22</span><span class="c3"> &  
mininet> h2 iperf -c h3 -p</span> <span class="c25">80</span><span class="c3"> -t 2 -i 1  
------------------------------------------------------------  
Client connecting to 10.0.0.3, TCP port 80  
TCP window size: 85.3 KByte</span> <span class="c3 c13">(</span><span class="c3">default</span><span class="c3 c13">)</span><span class="c3">  
------------------------------------------------------------  
</span><span class="c3 c13">[</span><span class="c3">  3</span><span class="c3 c13">]</span><span class="c3"> </span><span class="c7">local</span> <span class="c3">10.0.0.2 port</span> <span class="c25">52154</span><span class="c3"> connected with 10.0.0.3 port 80  
</span><span class="c3 c13">[</span><span class="c3"> ID</span><span class="c3 c13">]</span><span class="c3"> Interval       Transfer     Bandwidth  
</span><span class="c3 c13">[</span><span class="c3">  3</span><span class="c3 c13">]</span><span class="c3">  0.0- 2.1 sec  2.50 MBytes  9.77 Mbits/sec  
mininet> h2 iperf -c h3 -p</span> <span class="c25">22</span><span class="c3"> -t 2 -i 1   
------------------------------------------------------------  
Client connecting to 10.0.0.3, TCP port 22  
TCP window size: 85.3 KByte</span> <span class="c3 c13">(</span><span class="c3">default</span><span class="c3 c13">)</span><span class="c3">  
------------------------------------------------------------  
</span><span class="c3 c13">[</span><span class="c3">  3</span><span class="c3 c13">]</span><span class="c3"> </span><span class="c7">local</span> <span class="c3">10.0.0.2 port</span> <span class="c25">53695</span><span class="c3"> connected with 10.0.0.3 port 22  

</span><span class="c3 c13">[</span><span class="c3"> ID</span><span class="c3 c13">]</span><span class="c3"> Interval       Transfer     Bandwidth  
</span><span class="c3 c13">[</span><span class="c3">  3</span><span class="c3 c13">]</span><span class="c3">  0.0- 4.0 sec  </span> <span class="c25">512</span><span class="c3"> KBytes  1.05 Mbits/sec  
</span>

<span class="c6">Note that you can observe about 10 Mbps port 80 traffic and about 1 Mbps throughput for port 22 traffic (or any port that is not port 80).</span>

## <a name="h.siu0z1nxn0iv"></a><span class="c6 c38">Submitting your code</span>

<span class="c6">Once you are done testing both the topology and video slice component, you can test it as follows:</span>

<span class="c6">Copy the provided</span> <span class="c1">submit.py</span> <span class="c6"> to</span> <span class="c1">~/pox/pox/misc.</span>

<span class="c6">As above, make sure that your</span> <span class="c1">topologySlice.py, videoSlice.py</span><span class="c6"> and</span> <span class="c1">mininetSlice.py</span><span class="c6"> are in same directory (i.e.</span><span class="c1">~/pox/pox/misc</span><span class="c6">).</span>

<span class="c6"></span>

<span class="c6">To submit your code, run the submit.py script:</span>

<span class="c3">~/pox/pox/misc</span><span class="c10">$</span> <span class="c3">sudo python submit.py</span>

<span class="c6">Your Mininet installation should have Internet access by default, but still verify that it has Internet connectivity (i.e., eth0 set up as NAT). Otherwise,</span> <span class="c1">submit.py</span><span class="c6"> will not be able to post your code and output to our Coursera servers.</span>

<span class="c6"></span>

<span class="c6">The submission script will ask for your login and password. This password is not the general account password, but an assignment-specific password that is uniquely generated for each student. You can get this from the assignments listing page. Once the submission script completes finished, it will provide feedback on the terminal as to whether you have passed or failed.</span>

<span class="c6"></span>

<span class="c6">Note, if during the execution</span> <span class="c6 c26">submit.py</span> <span class="c6">script crashes for some reason, or if you terminate it using CTRL+C, make sure to clean Mininet environment using:</span>

<span class="c10">$</span> <span class="c3">sudo mn -c</span>

<span class="c6">Also, if it still complains about the controller running. Execute the following command to kill it:</span>

<span class="c10">$</span> <span class="c3">sudo fuser -k 6633/tcp</span>

<span class="c6">Part of this assignment is adapted from the</span> <span class="c29">[Flowvisor Tutorial](https://www.google.com/url?q=https%3A%2F%2Fgithub.com%2Fonstutorial%2Fonstutorial%2Fwiki%2FFlowvisor-Exercise&sa=D&sntz=1&usg=AFQjCNFRaHgFZASUPXLOoioC9XvPI5TzXg)</span><span class="c6">. If you are feeling brave, you may want to work your way through that tutorial to learn more; we chose to adapt the assignment for Pox to allow you to work in the Python environment that you're already familiar with, rather than having to install (and re-learn) the Flowvisor's Java-based environment.</span>

<span></span>
