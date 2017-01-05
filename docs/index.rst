.. DisNETPerf documentation master file, created by
   sphinx-quickstart on Thu Jan 05 19:09:16 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to DisNETPerf's documentation!
======================================
DisNETPerf - a Distributed Internet Paths Performance Analyzer - is a tool that allows one to locate the closest RIPE Atlas box (in terms of minimum RTT) to a given IP. You can either run DisNETPerf for a single IP or for a set of IPs.
Furthermore, once the closest RIPE Atlas box has been located, DisNETPerf permits to launch traceroutes from this box to a destination IP address provided by the user.

RIPE Atlas is a large active measurement network composed of geographically distributed probes used to measure Internet connectivity and reachability.

**How DisNETPerf works:**

Given a certain server, with IP address IPs, and a target customer, with IP address IPd, DisNETPerf locates the closest RIPE Atlas probe to IPs, namely IPc, and periodically runs traceroute from IPc to IPd, collecting different path performance metrics such as RTT per hop, end-to-end RTT, etc. This data collected is then used to troubleshoot ''reverse'' paths, from the server to the target customer.
To select IPc, DisNETPerf makes use of a combined topological and latency-based approach, using standard pings and BGP routing tables. In a nutshell, it locates the RIPE Atlas probe with minimum RTT to the selected server IPs, among a set of prefiltered IPc candidates, which are located at either the same AS of IPs or in the neighbor ASes.

Contents of the documentation:

.. toctree::
   :maxdepth: 4
   
   find_psbox
   launch_traceroutes
   get_traceroute_results
   recovery-mode

