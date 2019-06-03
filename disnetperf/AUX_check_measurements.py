# Author: Sarah Wassermann <sarah@wassermann.lu>

"""
This work is licensed under the Creative Commons Attribution-NoDerivatives 4.0 International License.
To view a copy of this license, visit http://creativecommons.org/licenses/by-nd/4.0/ or send a letter to Creative Commons,
PO Box 1866, Mountain View, CA 94042, USA.
"""

from __future__ import print_function

from ripe.atlas.cousteau import AtlasResultsRequest


def checkMeasurements(measurementIDs, verbose):
    """
    Check whether measurements are completed
    :param measurementIDs:  a list of the measurement IDs of the measurements you want to check
    :param verbose:         if true, an error-message gets displayed when an internal problem occurs; otherwise not
    :return:                True if every measurement completed; False otherwise
    """
    stopped = 0
    total = 0

    nbOfConsecutiveFailures = 0

    for udm in measurementIDs:
        total += 1
        while True:
            is_success, statusInfo = AtlasResultsRequest(msm_id=udm).create()
            if is_success:
                nbOfConsecutiveFailures = 0
                break
            else:
                nbOfConsecutiveFailures += 1

                # if 5 consecutive checks failed, abort
                if nbOfConsecutiveFailures == 5:
                    if verbose:
                        print('error: Could not check measurement-status!\n')
                    return None

        runningFlags = ["'name' => 'Scheduled'", "'name' => 'Ongoing'", "'name' => 'Specified'"]
        if not any(flag in statusInfo for flag in runningFlags):  # UDM finished
            stopped += 1

    return not (total - stopped > 0)
