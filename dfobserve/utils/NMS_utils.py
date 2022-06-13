'''
Utility functions for finding out things about the NMS site at the current moment.
'''

import subprocess as sp


def isRoofOpen():
    r = sp.run('curl -s https://nmskies.com/weather1.txt',
                shell=True,
                capture_output=True)
    use_str = r.stdout.decode('utf-8')
    # Get info for pod 2 (us)
    status = use_str.split('Pod 2')[1].strip()
    if status.upper() == 'CLOSED':
        return False
    elif status.upper() == 'OPEN':
        return True