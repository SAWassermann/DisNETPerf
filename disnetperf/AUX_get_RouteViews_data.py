#!/usr/bin/env python

# Author: Sarah Wassermann <sarah.wassermann@student.ulg.ac.be>

"""
This work is licensed under the Creative Commons Attribution-NoDerivatives 4.0 International License.
To view a copy of this license, visit http://creativecommons.org/licenses/by-nd/4.0/ or send a letter to Creative Commons,
PO Box 1866, Mountain View, CA 94042, USA.
"""

import os


def getASPath(start, end):
    """
    Tries to find an ASPath between the ASes <start> and <end> through RouteViews data
    :param start:   the start-AS of the path
    :param end:     the end-AS of the path
    :return:        a list containing all the AS-hops between <start> and <end> (including <start> and <end>) if a path
                    was found; en empty list otherwise
    """
    if not os.path.exists('../lib/routeviews_paths/' + start + '.txt'):
        return list()

    with open('../lib/routeviews_paths/' + start + '.txt', 'r') as file:
        for line in file:
            pathList = line.rstrip('\r\n').split()
            if pathList[-1] == end:
                file.close()
                return pathList

    return list()
