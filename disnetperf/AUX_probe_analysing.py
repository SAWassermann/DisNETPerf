# Author: Sarah Wassermann <sarah.wassermann@student.ulg.ac.be>

"""
This work is licensed under the Creative Commons Attribution-NoDerivatives 4.0 International License.
To view a copy of this license, visit http://creativecommons.org/licenses/by-nd/4.0/ or send a letter to Creative Commons,
PO Box 1866, Mountain View, CA 94042, USA.
"""

from __future__ import print_function


def parseProbeListOutput(output, verbose, map=None):
    """
    Parses the output of the script 'probe-list.pl', i.e. the script which retrieves a list of RIPE Atlas probes, and
    returns a list of the found probe IDs
    :param output:  the output of probe-list.pl
    :param verbose: if true, an error-message gets displayed when an internal problem occurs, otherwise not
    :param map:     if != none, the key-value pairs (probeID, AS) will be saved to the dictionary <map>
    :return:        a list of sublists in which each sublist contains at most 500 probe IDs
    """
    if not output:
        return ''
    else:
        resultLines = output.rsplit('\n')
        probes = list()
        try:
            ASMap = open('../logs/ID_To_AS.log', 'a', 0)
        except IOError:
            if verbose:
                print("error: Could not open file '../logs/ID_To_AS.log'\n")
            return None

        for line in resultLines:
            if not line:
                continue
            elements = line.split('\t')
            probes.append(elements[0]) # append probe ID
            ASMap.write(elements[0] + '\t' + elements[3] + '\n')
            if map is not None:  # save AS to dict
                map[elements[0]] = elements[3]
        ASMap.close()
    return [probes[i:i + 500] for i in range(len(probes), 500)]


def findASNeighbourhood(ASN, verbose):
    """
    Finds neighbours of AS with ASN <ASN> according to CAIDA's relationship dataset.
    :param ASN:     the ASN of the AS you want to find the neighbours for
    :param verbose: if true, an error message in case of an internal problem will be displayed, otherwise not
    :return:        a list of the detected neighbours
    """
    try:
        file = open('../lib/ASNeighbours.txt', 'r')
    except:
        if verbose:
            print("error: Could not open file '../lib/ASNeighbours.txt'\n")
        return None

    neighbours = set()
    for line in file:
        l = line.rstrip('\r\n')
        if not l or l.isspace() or l.startswith('#'):
            continue
        else:
            l = l.split('|')
            if ASN in l:
                if l[0] == ASN:
                    neighbours.add(l[1])
                else:
                    neighbours.add(l[0])
    file.close()
    return list(neighbours)
