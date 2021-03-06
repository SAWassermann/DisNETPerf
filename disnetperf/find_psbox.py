#!/usr/bin/env python

# Author: Sarah Wassermann <sarah@wassermann.lu>

"""
This work is licensed under the Creative Commons Attribution-NoDerivatives 4.0 International License.
To view a copy of this license, visit http://creativecommons.org/licenses/by-nd/4.0/ or send a letter to Creative Commons,
PO Box 1866, Mountain View, CA 94042, USA.
"""

from __future__ import print_function

import sys
sys.path.append('../')

import argparse
import datetime
import time
import os
import random
import ipaddress
from ripe.atlas.cousteau import Ping, AtlasSource, AtlasCreateRequest, AtlasResultsRequest, ProbeRequest

import disnetperf.AUX_IP_to_AS_map as IPToAS
import disnetperf.AUX_probe_analysing as pa
import disnetperf.AUX_check_measurements as cm


# global vars - begin
probeToASMap = {}
additionalInfoAboutMeasurements = {}
# global vars - end


def checkIP(ip):
    """
    Checks whether the IP address <ip> has the correct format
    :param ip: a representation of an IP (for instance, a string)
    :return: True if the IP is valid (either IPv4 or IPv6), False otherwise
    """
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def getSmallestPingProbe(measurementIDsDict, outputFileName):
    """
    Retrieves closest RIPE atlas boxes to target Ps and stores results
    :param measurementIDsDict:  a dictionary whose keys are RIPE user-defined measurement (udm) IDs and the corresponding
                                values are the targets of the UDMs
    :param outputFileName:      name of the file which the results of the analysis should be written to.
                                A line of the file has the format:
                                "<target-IP> <RIPE probe ID> <RIPE probe IP> <RIPE probe AS> <min RTT> <Label> "
                                <Label> is [RANDOM] when the candidate-boxes have been selected randomly,
                                [NO_AS] if no AS could be associated to the target-IP and [OK] if the candidate boxes were
                                found either in the same AS as the target IP or in neighbour ASes
    :return: a dictionary whose keys are target IPs and values are tuples in the form (<probeID>, <probeIP>, <probeAS>, <minRTT>)
    """
    IPToPSBoxMap = {}
    for IP in measurementIDsDict:
        UDMs = measurementIDsDict[IP]
        pingMeasurements = []

        for udm in UDMs:
            for _ in range(5):
                is_success, resultInfo = AtlasResultsRequest(msm_id=udm).create()

                if is_success and resultInfo:
                    break
                else:
                    time.sleep(30)
            else:
                print("Can't get udm-results...\n")
                continue

            if not resultInfo:
                continue

            for line in resultInfo:
                srcIP = line['src_addr']
                destIP = line['dst_addr']

                if srcIP == destIP:
                    continue

                if line['min'] != '*':
                    pingMeasurements.append((line['prb_id'], line['from'], line['min']))  # probe's ID/IP/RTT

        if not pingMeasurements:  # target unreachable
            continue
        probeMinRTT = min(pingMeasurements, key=lambda tup: tup[2])

        outputFileName.write(IP + '\t' + str(probeMinRTT[0]) + '\t' + str(probeMinRTT[1]) + '\t'
                             + str(probeToASMap[probeMinRTT[0]]) + '\t' + str(probeMinRTT[2]) + '\t'
                             + str(additionalInfoAboutMeasurements[IP]) + '\n')

        IPToPSBoxMap[IP] = (probeMinRTT[0], probeMinRTT[1], probeToASMap[probeMinRTT[0]], str(probeMinRTT[2]))

    return IPToPSBoxMap


def find_psboxes(IPs, verbose, recovery=False):
    """
    Finds the closest box to each IP in <IPs>, displays the results on the screen and stores them in a file in the
    'output' folder and whose naming-scheme is '<timestamp_of_creation_time>_psbox.txt'
    :param IPs:      a list containing all the IPs a closest box should be found to
    :param verbose:  if true, an error message gets displayed when an internal problem occurs; otherwise not
    :param recovery: if true, the recovery mode will be enabled (for more info, please see the docs in the folder
                     'doc')
    :return:         a dictionary whose values are the IPs and the keys are the corresponding closest boxes. If there
                     is no entry for a given IP, no box has been found
    """

    currentTime = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H-%M-%S')
    measurementIDs = set()
    IPsToMeasurementIDs = {}
    IPsAlreadyAnalysed = set()

    if recovery:  # recovery mode enabled
        # recover ID-to-AS mapping that has been done so far - begin
        try:
            ASMap = open('../logs/ID_To_AS.log', 'r')
        except IOError:
            if verbose:
                print("error: Could not open/create file '../logs/ID_To_AS.log'\n")
            return None

        for line in ASMap:
            line = line.rstrip('\r\n')
            if line:
                data = line.split('\t')
                probeToASMap[data[0]] = data[1]
        ASMap.close()
        # recover ID-to-AS mapping that has been done so far - end

        # recover IPs that have been analysed so far and the corresponding output-file - begin
        try:
            logFile = open('../logs/current_ping_measurementIDs.log', 'r')
        except IOError:
            if verbose:
                print("error: Could not open file '../logs/current_ping_measurementIDs.log'\n")
            return None

        cnt = 0
        timeStamp = ''
        for line in logFile:
            line = line.rstrip('\r\n')
            if line:
                if cnt == 0:
                    timeStamp = line
                else:
                    data = line.split('\t')
                    IPsToMeasurementIDs[data[-2]] = data[:-2]
                    measurementIDs.update(data[:-2])
                    additionalInfoAboutMeasurements[data[-2]] = data[-1]
                    IPsAlreadyAnalysed.add(data[-2])
                cnt += 1
        logFile.close()
        # recover IPs that have been analysed so far and the corresponding output-file - end

    if not recovery:
        try:
            ASMap = open('../logs/ID_To_AS.log', 'w')  # clear content of ID-to-AS log
        except IOError:
            if verbose:
                print("error: Could not open/create file '../logs/ID_To_AS.log'\n")
            return None
        ASMap.close()

    # open/create output-file - begin
    try:
        if recovery:
            output = open('../output/' + str(timeStamp) + '_psbox.txt', 'a', 1)
        else:
            output = open('../output/' + currentTime + '_psbox.txt', 'w', 1)
    except IOError:
        if verbose:
            if recovery:
                print("error: Could not open/create file '../output/" + str(timeStamp) + "_psbox.txt'\n")
            else:
                print("error: Could not open/create file '../output/" + currentTime + "_psbox.txt'\n")
        return None
    # open/create output-file - end

    # open/create log-file - begin
    try:
        if recovery:
            logFile = open('../logs/current_ping_measurementIDs.log', 'a', 1)
        else:
            logFile = open('../logs/current_ping_measurementIDs.log', 'w', 1)
            logFile.write(currentTime + '\n')
    except IOError:
        if verbose:
            print("error: Could not open/create file '../logs/current_ping_measurementIDs.log'\n")
        return None
    # open/create log-file - end

    # open file containing RIPE Atlas boxes and load data - begin
    try:
        with open('../lib/probelist.txt', 'r') as plFile:
            probeList = []  # load list with all currently connected RIPE probes
            for line in plFile:
                line = line.rstrip('\r\n')
                if line:
                    probeData = line.split('\t')
                    probeList.append((probeData[0], probeData[3]))
    except IOError:
        if verbose:
            print("error: Could not open file '../lib/probelist.txt'\n")
        output.close()
        logFile.close()
        return None
    # open file containing RIPE Atlas boxes and load data - end

    targetIPs = list(IPs)

    IPToASMap = IPToAS.mapIPtoAS(targetIPs, '../lib/GeoIPASNum2.csv', True)

    if IPToASMap is None:
        output.close()
        logFile.close()
        return None

    encounteredASes = {}

    # launching measurements to find closest box - start
    for IP in IPToASMap:
        if IP in IPsAlreadyAnalysed:
            continue
        IPsAlreadyAnalysed.add(IP)

        if verbose:
            print('Starting to do measurements for IP: ' + IP + '...\n')
        AS = IPToASMap[IP]

        if AS == 'NA_MAP':
            additionalInfoAboutMeasurements[IP] = '[NO_AS]'
            idx = random.sample(range(len(probeList)), 100)
            selectedProbes = [probeList[i][0] for i in idx]

            for i in idx:
                probeToASMap[probeList[i][0]] = probeList[i][1]

            try:
                with open('../logs/ID_To_AS.log', 'a', 0) as ASMap:
                    for i in idx:
                        ASMap.write(probeList[i][0] + '\t' + probeList[i][1] + '\n')
            except IOError:
                if verbose:
                    print("error: Could not open/create file '../logs/ID_To_AS.log'\n")
                output.close()
                logFile.close()
                return None

            probes = [selectedProbes[i:i + 500] for i in range(len(selectedProbes), 500)]

        elif AS not in encounteredASes:  # check whether we have already retrieved probes for this AS
            # check whether there are probes in IP's AS
            probes = list(ProbeRequest(asn=IPToASMap[IP]))
            # TODO: what if problem in executing request?

            # if not, look at the neighbour ASes
            if not probes:
                neighbours = pa.findASNeighbourhood(IPToASMap[IP], True)
                if neighbours is None:
                    output.close()
                    logFile.close()
                    return None

                for neighbour in neighbours:
                    probes = list(ProbeRequest(asn=neighbour))
            # TODO: what if problem in executing request?

            if probes:  # we have found neighbouring probes
                probes = pa.parseProbeListOutput(probes, True, probeToASMap)
                if probes is None:
                    output.close()
                    logFile.close()
                    return None

                encounteredASes[AS] = probes
            else:
                encounteredASes[AS] = ''

        # pinging neighbours - start
        if AS != 'NA_MAP':
            probes = encounteredASes[AS]

        if not probes:  # if no probes in neighbourhood, use randomly selected probes
            additionalInfoAboutMeasurements[IP] = '[RANDOM]'

            idx = random.sample(range(len(probeList)), 100)
            selectedProbes = [probeList[i][0] for i in idx]

            for i in idx:
                probeToASMap[probeList[i][0]] = probeList[i][1]

            try:
                with open('../logs/ID_To_AS.log', 'a', 0) as ASMap:
                    for i in idx:
                        ASMap.write(probeList[i][0] + '\t' + probeList[i][1] + '\n')
            except IOError:
                if verbose:
                    print("error: Could not open/create file '../logs/ID_To_AS.log'\n")
                output.close()
                logFile.close()
                return None

            probes = [list(map(int, selectedProbes[i:i + 500])) for i in range(len(selectedProbes), 500)]
        elif AS != 'NA_MAP':
            additionalInfoAboutMeasurements[IP] = '[OK]'

        giveUp = False

        for probesToUse in probes:
            for _ in range(5):  # Perform at most 5 tries before giving up.
                description = "Ping target={target}".format(target=IP)
                ping = Ping(af=4, target=IP, description=description, protocol="ICMP", packets=10)
                source = AtlasSource(type="probes", value=','.join(map(str, probesToUse)), requested=len(probesToUse))
                request = AtlasCreateRequest(key=API_KEY, measurements=[ping], sources=[source], is_oneoff=True)

                (is_success, response) = request.create()

                if is_success and 'measurements' in response:
                    if IP not in IPsToMeasurementIDs:
                        IPsToMeasurementIDs[IP] = [response['measurements'][0]]
                    else:
                        IPsToMeasurementIDs[IP].append(response['measurements'][0])
                    measurementIDs.add(response['measurements'][0])
                    break
                else:
                    time.sleep(180)
            else:
                giveUp = True
                IPsToMeasurementIDs.pop(IP, None)  # delete this entry; should not be analyzed
                break
        if giveUp:
            break

        if IPsToMeasurementIDs[IP]:
            logFile.write('\t'.join(map(str, IPsToMeasurementIDs[IP])) + '\t' + IP + '\t'
                                    + additionalInfoAboutMeasurements[IP] + '\n')
        # pinging neighbours - end

    # launching measurements to find closest box - end
    logFile.close()

    # waiting for ping-measurements to finish
    if verbose:
        print('Waiting for ping measurements to finish...\n')
    status = cm.checkMeasurements(measurementIDs, True)
    if status is None:
        return None

    while not status:
        time.sleep(180)
        status = cm.checkMeasurements(measurementIDs, True)

        if status is None:
            output.close()
            return None

    if verbose:
        print('Computing closest RIPE Atlas box...\n')

    results = getSmallestPingProbe(IPsToMeasurementIDs, output)

    output.close()
    # os.remove('../logs/current_ping_measurementIDs.log')
    # if os.path.exists('../logs/ID_To_AS.log'):
    #     os.remove('../logs/ID_To_AS.log')

    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Find the closest RIPE Atlas box to a set of IPs')
    parser.add_argument('-v', action="version", version="version 1.0")
    parser.add_argument('-k', action="store", dest="api-key", help="An API key with 'Measurement creation' permissions", required=True)
    parser.add_argument('-n', action="store", dest="filename", help="File containing the IPs for which you want to find the closest box."
                                                                    "The file has to be stored in the folder 'input'")
    parser.add_argument('-o', action="store", dest="targetIP", help="The IP for which you want to find the closest box.")
    parser.add_argument('-r', action="store", dest="recovery", type=int, choices=[0, 1], default=0,
                                                                                            help="1 if you want to enable the"
                                                                                              "recovery-mode, 0 otherwise."
                                                                                              "For more information about the "
                                                                                              "recovery-mode, please have a look "
                                                                                              "at the documentation in 'doc'")

    arguments = vars(parser.parse_args())

    if not arguments['targetIP'] and not arguments['filename']:
        parser.error("You must either specify an IP or a filename of a file containing IPs!")
        exit(1)

    API_KEY = arguments['api-key']

    # if an IP is specified, we always go for the IP
    if arguments['targetIP']:
        targetIP = arguments['targetIP']
        if not checkIP(targetIP):
            print('error: The indicated IPs must be in the format <X.X.X.X>!\n')
            exit(3)
        targetIPs = [targetIP]
    else:   # check file
        try:
            IPfile = open('../input/' + arguments['filename'], 'r')
        except IOError:
            print("error: Could not open file '../input/" + arguments['filename'] + "'\n")
            exit(2)

        # load IPs from file
        targetIPs = []
        for line in IPfile:
            l = line.rstrip('\r\n')
            if l and not l.isspace():
                if not checkIP(l):
                    print('error: The indicated IPs must be in the format <X.X.X.X>!\n')
                    IPfile.close()
                    exit(3)
                targetIPs.append(l)
        IPfile.close()

    # launch measurements and get psboxes
    if arguments['recovery'] and arguments['recovery'] == 1:
        if not os.path.exists('../logs/current_ping_measurementIDs.log'):
            print("error: Could not launch recovery-mode!\n")
            exit(5)
        psBoxMap = find_psboxes(targetIPs, True, True)
    else:
        psBoxMap = find_psboxes(targetIPs, True, False)

    if psBoxMap is not None and psBoxMap:
        for IP in targetIPs:
            if IP in psBoxMap:
                print(IP + '\t' + '\t'.join(map(str, psBoxMap[IP])) + '\t' + str(additionalInfoAboutMeasurements[IP]) + '\n')
    if psBoxMap is None:
        exit(4)
    else:
        exit(0)
