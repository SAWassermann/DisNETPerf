# Author: Sarah Wassermann <sarah.wassermann@student.ulg.ac.be>

"""
This work is licensed under the Creative Commons Attribution-NoDerivatives 4.0 International License.
To view a copy of this license, visit http://creativecommons.org/licenses/by-nd/4.0/ or send a letter to Creative Commons,
PO Box 1866, Mountain View, CA 94042, USA.
"""

from __future__ import print_function


def parseProbeListOutput(output, verbose, map=None):
    """
    Parses a list of RIPE Altas probe descriptions and returns a list of the found probe IDs
    :param output:  the list of probe descriptions
    :param verbose: if true, an error message gets displayed when an internal problem occurs, otherwise not
    :param map:     if != none, the key-value pairs (probeID, AS) will be saved to the dictionary <map>
    :return:        a list of sublists in which each sublist contains at most 500 probe IDs
    """
    if not output:
        return ''

    try:
        with open('../logs/ID_To_AS.log', 'a', 0) as ASMap:
            probes = list()

            for el in output:
                probes.append(el['id'])  # append probe ID
                ASMap.write(str(el['id']) + '\t' + str(el['asn_v4']) + '\n')
                if map is not None:  # save AS to dict
                    map[el['id']] = el['asn_v4']
    except IOError:
        if verbose:
            print("error: Could not open file '../logs/ID_To_AS.log'\n")
        return None

    return [probes[i:i + 500] for i in range(len(probes), 500)]


def findASNeighbourhood(ASN, verbose):
    """
    Finds neighbours of AS with ASN <ASN> according to CAIDA's relationship dataset.
    :param ASN:     the ASN of the AS you want to find the neighbours for
    :param verbose: if true, an error message in case of an internal problem will be displayed, otherwise not
    :return:        a list of the detected neighbours
    """
    try:
        with open('../lib/ASNeighbours.txt', 'r') as file:
            neighbours = set()
            for line in file:
                line = line.rstrip('\r\n')
                if not line or line.isspace() or line.startswith('#'):
                    continue

                line = line.split('|')
                if ASN in line:
                    if line[0] == ASN:
                        neighbours.add(line[1])
                    else:
                        neighbours.add(line[0])
            return list(neighbours)
    except IOError:
        if verbose:
            print("error: Could not open file '../lib/ASNeighbours.txt'\n")
        return None

