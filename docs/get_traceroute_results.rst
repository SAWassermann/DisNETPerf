=========================
get_traceroute_results.py
=========================

| This script retrieves and saves the results of traceroute measurements.

| To launch it, please use the command

.. code:: bash

 python get_traceroute_results.py -n <UDM filename>

| <UDM filename> refers to the filename of the file in which the measurement IDs of the measurements are stored. **This file has to be stored in the 'input' folder.** Each line has to follow this format:

| ``<UDM_ID_1>...<UDM_ID_X> <targetIP``

| where <UDM_ID_1>...<UDM_ID_X> are the IDs of the traceroute measurements launched towards the IP address <targetIP>

Output
......

*get_traceroute_results.py* creates a file in the folder *output*. The naming scheme of such an output-file is ``<timestamp>_scheduled_traceroutes.txt`` where ``<timestamp>`` refers to the timestamp
indicating when ``get_traceroute_results.py`` was launched.
In this file, each measurement is represented in the following way:

| ``PROBEID: <ID>``
| ``TIMESTAMP: <TS>``
| ``NBHOPS: <N>``
| ``HOP: <IP 1> [<avg RTT>]``
| ``...``
| ``HOP: <IP N> [<avg RTT>]``
| ``ASPATH: <ASHOP 1>...<ASHOP X>``
| ``POPPATH: <POPHOP 1>...<POPHOP Y>``
| ``IPPATH: <IPHOP 1>...<IPHOP Z>``

<IP X> either reports the IP address of the encountered router interface or is replaced by NA\_TR. NA\_TR indicates that the IP address of the router could not be inferred (and therefore the average RTT could not be computed). ASPATH, POPPATH, and IPPATH indicate the paths at the three considered levels. Regarding the AS hops, we display NA\_MAP when the IP address could not be mapped to an AS, and NA\_TR when the IP address is unknown.
