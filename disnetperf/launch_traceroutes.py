#!/usr/bin/env python

# Author: Sarah Wassermann <sarah.wassermann@student.ulg.ac.be>

"""
This work is licensed under the Creative Commons Attribution-NoDerivatives 4.0 International License.
To view a copy of this license, visit http://creativecommons.org/licenses/by-nd/4.0/ or send a letter to Creative Commons,
PO Box 1866, Mountain View, CA 94042, USA.
"""

import argparse
import datetime
import time
import math
from ripe.atlas.cousteau import Traceroute, AtlasSource, AtlasCreateRequest

import disnetperf.find_psbox as ps


# global vars - begin
INTERVAL_DEFAULT = 600
# global vars - end


def launch_scheduled_traceroutes(destIP, probes, start, stop, interval, numberOfTraceroutes):
    """
    Launches traceroutes.
    The list of probes <probes> will be used as sources and the destination is <destIP>
    When no start time is specified, traceroutes will be launched as soon as possible
    It is not possible to specify a start time, but not a stop time and vice-versa
    When no interval is given, a default interval of 600 seconds is used
    Either a stop-time or a number of traceroutes to be scheduled has to be given. When a stop-time
    is indicated, the number of traceroutes will be ignored
    :param destIP:              the IP towards which traceroutes should be launched
    :param probes:              the list of RIPE Atlas probes which should be used as sources
    :param start:               time (UNIX timestamp) at which first traceroute should be launched
    :param stop:                time (UNIX timestamp) at which no more traceroutes should be launched
    :param interval:            time between 2 consecutive traceroutes (in seconds)
    :param numberOfTraceroutes: number of traceroutes to be scheduled
    """
    currentTime = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H-%M-%S')
    try:
        logFile = open('../logs/' + currentTime + '_current_scheduled_traceroutes.log', 'w', 0)
    except IOError:
        print("error: Could not open/create '../logs/" + currentTime + "_current_scheduled_traceroutes.log'!\n")
        return

    giveUp = False
    measurementIDs = []

    probes = [probes[i:i + 500] for i in range(len(probes), 500)]
    for probesToUse in probes:
        for _ in range(5):  # Perform at most 5 tries before giving up.
            # Create a request depending on the requested parameters.
            if stop:
                startTime = start if start else int(math.ceil(time.time())) + 1
                i = interval if interval else INTERVAL_DEFAULT

                description = "Traceroute target={target} [{start}:{stop}]".format(target=destIP, start=startTime, 
                                                                                   stop=stop)
                traceroute = Traceroute(af=4, target=destIP, description=description, protocol="ICMP")
                source = AtlasSource(type="probes", value=probesToUse)
                request = AtlasCreateRequest(start_time=startTime, stop_time=stop, key=API_KEY,
                                             measurements=[traceroute], sources=[source], is_oneoff=False, interval=i)

            elif not start and not interval and not numberOfTraceroutes:
                description = "Traceroute target={target}".format(target=destIP)
                traceroute = Traceroute(af=4, target=destIP, description=description, protocol="ICMP")
                source = AtlasSource(type="probes", value=probesToUse)
                request = AtlasCreateRequest(key=API_KEY, measurements=[traceroute], sources=[source], is_oneoff=True)

            elif numberOfTraceroutes and interval and not start:
                startTime = int(math.ceil(time.time())) + 1
                stopTime = startTime + numberOfTraceroutes * interval

                description = "Traceroute target={target} [{start}:{stop}]".format(target=destIP, start=startTime, 
                                                                                   stop=stopTime)
                traceroute = Traceroute(af=4, target=destIP, description=description, protocol="ICMP")
                source = AtlasSource(type="probes", value=probesToUse)
                request = AtlasCreateRequest(start_time=startTime, stop_time=stopTime, key=API_KEY, 
                                             measurements=[traceroute], sources=[source], is_oneoff=False, 
                                             interval=interval)

            elif numberOfTraceroutes and not interval:
                startTime = start if start else int(math.ceil(time.time())) + 1
                stopTime = startTime + numberOfTraceroutes * INTERVAL_DEFAULT

                description = "Traceroute target={target} [{start}:{stop}]".format(target=destIP, start=startTime, 
                                                                                   stop=stopTime)
                traceroute = Traceroute(af=4, target=destIP, description=description, protocol="ICMP")
                source = AtlasSource(type="probes", value=probesToUse)
                request = AtlasCreateRequest(start_time=startTime, stop_time=stopTime, key=API_KEY, 
                                             measurements=[traceroute], sources=[source], is_oneoff=False, 
                                             interval=INTERVAL_DEFAULT)

            else:
                break

            # Actually start the request.
            (is_success, response) = request.create()
            if is_success and 'id' in response:
                measurementIDs.append(response['id'])
                break
            else:
                time.sleep(180)
        else:
            giveUp = True
            break

    if not giveUp:
        logFile.write('\t'.join(measurementIDs) + '\t' + destIP + '\n')
    logFile.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Launch traceroutes from the closest RIPE Atlas boxes'
                                                 ' to a set of IPs to a specified destination')
    parser.add_argument('-k', action="store", dest="api-key", help="An API key with 'Measurement creation' permissions", required=True)
    parser.add_argument('-v', action="version", version="version 1.0")
    parser.add_argument('-n', action="store", dest="filename", help="Filename of file containing the IPs "
                                                                    "for which traceroutes from the corresponding "
                                                                    "closest RIPE Atlas boxes should be launched to "
                                                                    "the specified destination. The file has to be stored "
                                                                    "in the folder 'input'")
    parser.add_argument('-o', action="store", dest="targetIP", help="The IP for which you want to find the closest box (if not already specified)"
                                                                    "and then launch traceroutes from this box to the specified destination-IP")
    parser.add_argument('-d', action="store", dest="destIP", help="IP which the traceroutes should be launched to", required=True)
    parser.add_argument('-b', action="store", dest="boxID", type=int, help="ID of the closest box to the IP indicated with -o")
    parser.add_argument('-f', action="store", dest="flag", type=int, choices=[0, 1], help="If 1, the closest boxes are specified "
                                                                                          "(via -b when -o used, in the input-file "
                                                                                          "when -n is used). If 0, the closest boxes "
                                                                                          "are computed before launching traceroutes",
                                                                                    required=True)
    parser.add_argument('-m', action="store", dest="nbTraceroutes", type=int, help="Total number of traceroutes to be launched")
    parser.add_argument('-t', action="store", dest="interval", type=int, help="Time between two consecutive traceroutes (in seconds")
    parser.add_argument('-s', action="store", dest="start", type=int, help="Time when the first traceroute should be launched")
    parser.add_argument('-p', action="store", dest="stop", type=int, help="Time when traceroutes should be stopped")

    arguments = vars(parser.parse_args())

    # check parameters - begin
    if not any(arguments.values()):
        parser.error("error: You must at least specify an IP or a filename of a file containing IPs and a destination-IP!")
        exit(1)
    elif not arguments['filename'] and not arguments['targetIP']:
        parser.error("error: You must either specify an IP or a filename of a file containing IPs!")
        exit(1)
    elif arguments['interval'] and not arguments['nbTraceroutes'] and not arguments['stop']:
        parser.error("error: You must specify the number of traceroutes when setting an interval "
                     "and not indicating the stop-time!")
        exit(1)
    elif arguments['targetIP'] and arguments['flag'] == 1 and not arguments['boxID']:
        parser.error("error: You must specify the RIPE Atlas box to use when setting -f to 1!")
        exit(1)
    elif arguments['flag'] == 0 and arguments['targetIP'] and arguments['boxID']:
        parser.error("error: You cannot specify the RIPE Atlas box to use when setting -f to 0!")
        exit(1)
    elif arguments['stop'] and arguments['nbTraceroutes']:
        parser.error("error: You cannot specify the stop-time when indicating a number of traceroutes to be performed!")
        exit(1)
    # check parameters - end

    API_KEY = arguments['api-key']
    flag = arguments['flag']

    # when the user indicated an IP (-o), always go for it
    if arguments['targetIP']:
        targetIP = arguments['targetIP']
        if flag == 1:
            closestBox = str(arguments['boxID'])
        else:
            closestBoxMap = ps.find_psboxes([targetIP], True)
            if closestBoxMap:
                closestBox = closestBoxMap[targetIP]
            elif closestBoxMap is None:
                exit(3)
            else:
                exit(0)
        closestBox = [closestBox]
    else:  # check file
        try:
            # load IPs from file
            with open('../input/' + arguments['filename'], 'r') as IPfile:
                closestBox = set()
                targetIPs = []
                for line in IPfile:
                    line = line.rstrip('\r\n')
                    if line and not line.isspace():
                        data = line.split('\t')
                        if flag == 1 and len(data) < 2:
                            print('error: You must specify a RIPE Atlas box to use when -f is set to 1, please refer '
                                  'to the manual\n')
                            exit(3)
                        if not ps.checkIP(data[0]):
                            print('error: The indicated IPs must be in the format <X.X.X.X> where X is an integer >= 0!\n')
                            exit(4)
                        targetIPs.append(data[0])
                        if flag == 1:
                            closestBox.add(data[1])
        except IOError:
            print("error: Could not open file '../input/" + arguments['filename'] + "'\n")
            exit(2)

        if flag == 0:
            closestBoxMap = ps.find_psboxes(targetIPs, True, False)
            if closestBoxMap:
                for key in closestBoxMap:
                    closestBox.add(closestBoxMap[key][0])
            elif closestBoxMap is None:
                exit(3)
            else:
                exit(0)
    launch_scheduled_traceroutes(arguments['destIP'], list(closestBox), arguments['start'], arguments['stop'],
                                 arguments['interval'], arguments['nbTraceroutes'])
