[![mPlane](http://www.ict-mplane.eu/sites/default/files//public/mplane_final_256x_0.png)](http://www.ict-mplane.eu/)

DisNETPerf
==============
DisNETPerf - a Distributed Internet Paths Performance Analyzer - is a tool that allows one to locate the closest RIPE Atlas box (in terms of minimum RTT) to a given IP. You can either run DisNETPerf for a single IP or for a set of IPs.
Furthermore, once the closest RIPE Atlas box has been located, DisNETPerf permits to launch traceroutes from this box to a destination IP address provided by the user.

RIPE Atlas is a large active measurement network composed of geographically distributed probes used to measure Internet connectivity and reachability.

Given a certain server, with IP address IP_s, and a target customer, with IP address IP_d, DisNETPerf locates the closest RIPE Atlas probe to IP_s, namely IP_c, and periodically runs traceroute from IP_c to IP_d, collecting different path performance metrics such as RTT per hop, end-to-end RTT, etc. This data collected is then used to troubleshoot ''reverse'' paths, from the server to the target customer.

To select IP_c, DisNETPerf makes use of a combined topological and latency-based approach, using standard pings and BGP routing tables. In a nutshell, it locates the RIPE Atlas probe with minimum RTT to the selected server IP_s, among a set of prefiltered IP_c candidates, which are located at either the same AS of IP_s or in the neighbor ASes.

#### List of runnable scripts

- **find_psbox.py**: locate the closest boxes for a set of IPs
- **launch_traceroutes.py**: launch traceroutes from RIPE Atlas boxes to a given destination IP address
- **get_traceroute_results.py**: Retrieve the results of the launched traceroute-measurements

All the scripts whose names are prefixed with **AUX_** cannot be run but are used by the scripts explained above.

#### Structure

DisNETPerf is structured into 7 folders:
- **contrib**: contains the RIPE Atlas Toolbox developed by **Pierdomenico Fiadino**. DisNETPerf heavily relies on this toolbox
- **doc**: contains .txt-files explaining how to use DisNETPerf
- **input**: should include the files used as input for DisNETPerf
- **lib**: contains datasets needed in order to locate the closest RIPE Atlas boxes
- **logs**: includes log-files
- **output**: the result-files generated by DisNETPerf are saved into this folder
- **scripts**: includes all the Python-scripts

Prerequisites
-------------
To run DisNETPerf, Python 2.7 must be installed. You can download Python 2.7 on <https://www.python.org/download/releases/2.7/>
Furthermore, please fulfill all the prerequisites for the RIPE Atlas Toolbox explained on <https://github.com/pierdom/atlas-toolbox>

DisNETPerf has partially been tested on Debian 7 with Python 2.7.3.

Acknowledgement
---------------

This work has been partially funded by the European Commission 
funded mPlane ICT-318627 project (www.ict-mplane.eu).

Author
------

* Main author: **Sarah Wassermann** -  <sarah.wassermann@student.ulg.ac.be> - <http://wassermann.lu>
* Contributor: **Pierdomenico Fiadino** - <http://userver.ftw.at/~fiadino>
