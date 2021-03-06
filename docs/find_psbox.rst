=============
find_psbox.py
=============

This script locates the closest RIPE Atlas probes (called *proximity services boxes*) to IP addresses.

| In order to launch this script, please use the following command:


.. code:: bash

 python find psbox.py -k <API-KEY> [-n <IP filename>] [-o <targetIP>] [-r {0,1}]

| <API-Key> points to a RIPE Atlas API Key with *Measurement creation* permissions. Such a key can easily be created through the Web interface of RIPE Atlas.
| <IP filename> refers to the name of the file in which the IP addresses DisNETPerf should locate the closest RIPE Atlas box to are listed. **This file has to be stored in the 'input' folder.** The file should contain one IP per line. An IP should be in the usual format, i.e. X.X.X.X where X is an integer >= 0.

| If you want to analyze only a single IP, you can also use the -o parameter and replace <targetIP> with that particular IP.

| If you set the -r parameter to 1, the recovery-mode will be enabled. For further information about this mode, please have a look at the documentation about it. (The default-value for this parameter is 0.)

Output
------
The output file of the script ``find_psbox.py`` contains information about the targetIPs and the corresponding computed
closest boxes. The naming scheme of such an output-file is ``<timestamp>_psbox.txt`` where ``<timestamp>`` refers to the timestamp
indicating when ``find_psbox.py`` was launched. This file is saved into the folder *output*.

| The lines of an output-file follow the format:

| *<targetIP> <psBox ID> <psBox IP> <AS number> <min RTT> <label>*

| where <psBox ID/IP> refers to the ID/IP of the found proximity service box, <AS number> to the AS number in which this probe is installed, and <min RTT> to the minimum RTT measured from this box to the targetIP.
| Finally, <label> can have the following values:

    -   **[OK]**: the candidate RIPE Atlas boxes (i.e. among the ones the closest one has been chosen) are either in the same AS as <target-IP> or in the neighbour-ASes
    -   **[NO_AS]**: <targetIP> could not be mapped to an AS and thus the candidate RIPE Atlas boxes have been chosen randomly
    -   **[Random]**: No candidate boxes have been found in the same AS as <target-IP> and in the neighbour-ASes. Boxes have thus been chosen randomly

Please note that the lines in this file are tab-separated.

