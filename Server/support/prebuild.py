"""
*******************************************************************************
 Copyright (C) 2021-2022 Advanced Micro Devices, Inc. All rights reserved.

*******************************************************************************
"""

import os
import sys
from external import external_only

# Add selected platform support directory to beginning of python script search path
try:
    search_path = os.path.join(os.environ['EDK2_OPENBOARD_SUPPORTED_DIR'], '')
except:
    search_path = os.path.join(os.environ['AMD_PLATFORM_DIR'], 'support', '')
sys.path.insert(0, search_path)

def prebuild():
    print('PreBuild')
    print('Launched Python Version: {}.{}.{}'.format(
        sys.version_info.major,
        sys.version_info.minor,
        sys.version_info.micro))
    # Execute first in prebuild
    if os.environ.get("APCB_BOARD_LIST") == None:
        from projectprebuild import projectprebuild
        projectprebuild()
    print("No CBS package")

def main():
    """!
    Execute PreBuild items

    Execute anything that needs to be completed before the EDKII BUILD
    """
    prebuild()

if __name__ == '__main__':
    main()
