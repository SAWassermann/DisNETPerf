=============
Recovery-mode
=============

DisNETPerf offers a recovery-mode when computing the closest RIPE Atlas boxes.
If DisNETPerf encounters an internal problem while ``find_psbox.py`` is running, and stops, you can simply rerun the script
and set the parameter -r to 1.
DisNETPerf will then automatically detect the created output-file for the failed measurements (if a file has been created)
and will launch the remaining measurements and analyses.

For this mode to work properly, some constraints have to be respected:
    -   the run of find_psbox.py that should perform the recovery must be launched immediately after the failed run. If you run
        find_psbox.py for another purpose before the recovery-run, the recovery will not be possible anymore
    -   the created files 'current_ping_measurementIDs.log' and 'ID_To_AS.log' in the folder 'log' are necessary. Please
        do not delete or modify them.