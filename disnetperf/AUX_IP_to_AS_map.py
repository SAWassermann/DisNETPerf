# Author: Sarah Wassermann <sarah.wassermann@student.ulg.ac.be>

"""
This work is licensed under the Creative Commons Attribution-NoDerivatives 4.0 International License.
To view a copy of this license, visit http://creativecommons.org/licenses/by-nd/4.0/ or send a letter to Creative Commons,
PO Box 1866, Mountain View, CA 94042, USA.
"""

from __future__ import print_function

import csv


def IPToInt(ip):
    """
    Returns the integer corresponding th the IP address <ip>
    :param ip:  a string representing an IP
    :return:    <ip> converted into an integer
    """
    parts = list(map(int, ip.split('.')))
    return (16777216 * parts[0]) + (65536 * parts[1]) + (256 * parts[2]) + parts[3]


def mapIPtoAS(IPListArg, IPtoASFilename, verbose):
    """
    Returns a dictionary containing the IP-to-AS mappings
    :param IPList:          list containing the IPs to be analysed
    :param IPtoASFilename:  CSV-file containing IP-to-AS mappings (IPs given in ranges).
                            Line-format: <IP lower bound> <IP upper bound> <AS>
    :param verbose:         if true, an error-message gets displayed when an internal problem occurs; otherwise not
    :return:                a dictionary with an IP as key and the corresponding AS as value
    """
    IPtoASMap = dict()

    try:
        with open(IPtoASFilename, 'rb') as csvfile:
            reader = csv.reader(csvfile)
            IPRangeData = list(reader)
    except IOError:
        if verbose:
            print("error: Could not open '" + IPtoASFilename + "'\n")
        return None

    IPList = list(IPListArg)
    IPList.sort(key=IPToInt)

    currentIndex = 0
    nbOfMappings = len(IPRangeData)

    for ip in IPList:
        IP = IPToInt(ip)

        while currentIndex < nbOfMappings:
            mapping = IPRangeData[currentIndex]
            lowerbound, upperbound = int(mapping[0]), int(mapping[1])
            if IP >= lowerbound and IP <= upperbound:
                ASdata = mapping[2].split()
                IPtoASMap[ip] = ASdata[0][2:]
                break
            elif lowerbound > IP:  # no match found!
                IPtoASMap[ip] = 'NA_MAP'
                break
            else:
                currentIndex += 1

    return IPtoASMap