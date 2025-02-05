"""
*******************************************************************************
 Copyright (C) 2021-2024 Advanced Micro Devices, Inc. All rights reserved.

*******************************************************************************
"""

from buildsupport import build_module_only, build_show_only, build_quick
from apcb_token_generate import apcb_token_generate

from external import external_only

import sys
import os
import subprocess
import shutil


def build_apcb_board(soc_sku):
    """!
    build the APCB for the board

    exception   various
    """
    if build_quick() or build_show_only() or build_module_only():
        print('\nSkipping APCB build')
        return

    print('\nExecuting APCB build')

    # Get environment variables exception if not located
    workspace = os.environ['WORKSPACE']
    build_type = os.environ['AMD_PLATFORM_BUILD_TYPE']
    custom_apcb_path = os.environ['CUSTOM_APCB_PATH']

    # Generate Platform APCB token override
    apcb_token_generate ()
    if not os.path.exists(custom_apcb_path):
        os.makedirs(custom_apcb_path)

    apcb_tool_temp_path = os.environ['APCB_TOOL_TEMP_PATH']
    apcb_script = 'ApcbCreate.py'

    cmd_env = os.environ.copy()
    cmd_env["APCB_EXTERNAL_BUILD"] = "1"

    # Check OS to avoid Linux from defaulting to python 2.xx
    if sys.platform.startswith("linux"):
        cmd = ["python3"]
    elif sys.platform.startswith("win"):
        cmd = ["python"]

    # path to APCB script
    cmd.append(os.path.join(apcb_tool_temp_path, apcb_script))
    cmd.append("CLEAN")
    cmd.append("BUILD")

    # Execute the APCB build
    sys.stdout.flush()
    completed_process = subprocess.run(
        cmd, env=cmd_env, cwd=apcb_tool_temp_path)
    if completed_process.returncode != 0:
        error_text = 'Return code = {}'.format(completed_process.returncode)
        print(error_text)
        raise ValueError(error_text)

    # Copy built files
    src = os.path.join(apcb_tool_temp_path, 'Release')
    dst = custom_apcb_path
    files = (
        'APCB_{}_D4_DefaultRecovery.bin'.format(soc_sku),
        'APCB_{}_D4_Updatable.bin'.format(soc_sku),
        'APCB_{}_D4_EventLog.bin'.format(soc_sku)
    )
    for file in files:
        src_file = os.path.join(src, file)
        dst_file = os.path.join(dst, file)
        if os.path.exists(src_file):
            print('Copying "{}"->"{}"'.format(src_file, dst_file))
            shutil.copy(src_file, dst_file)
        else:
            print('[WARNING] Source file:{} not present.'.format(src_file))

    # Delete build time folders
    for dir in ('Release', 'Build', 'Log'):
        shutil.rmtree(
            os.path.join(apcb_tool_temp_path, dir),
            ignore_errors=True
        )

def build_apcb():
    """!
    build the APCB

    exception   various
    """
    soc_sku = os.environ['SOC_SKU']
    if os.environ.get("APCB_BOARD_LIST_2") is not None:
        workspace = os.environ['WORKSPACE']
        build_output = os.environ['BUILD_OUTPUT']
        soc = os.environ['SOC_2']
        soc_sku_2 = os.environ['SOC_SKU_2']
        socket = os.environ.get("SOCKET").title()
        if socket == 'Turin':
            #TODO, this should be remove once .json file updated
            socket = 'Sp5'

        os.environ['APCB_TOOL_TEMP_PATH'] = os.path.normpath(os.path.join(
            workspace,
            'AGESA/AgesaPkg/Addendum/Apcb/'+soc+socket+'Rdimm'
        ))
        os.environ['APCB_MULTI_BOARD_SUPPORT'] = '1'
        os.environ['APCB_DATA_BOARD_DIR_LIST'] = os.environ.get('APCB_BOARD_LIST_2')
        os.environ['CUSTOM_APCB_PATH'] = os.path.normpath(os.path.join(
            build_output,
            'Apcb'
        ))
        build_apcb_board(soc_sku_2)

    if os.environ.get("APCB_BOARD_LIST") is not None:
        workspace = os.environ['WORKSPACE']
        build_output = os.environ['BUILD_OUTPUT']
        soc = os.environ['SOC']
        socket = os.environ.get("SOCKET").title()
        if socket == 'Turin':
            #TODO, this should be remove once .json file updated
            socket = 'Sp5'

        os.environ['APCB_TOOL_TEMP_PATH'] = os.path.normpath(os.path.join(
            workspace,
            'AGESA/AgesaPkg/Addendum/Apcb/'+soc+socket+'Rdimm'
        ))
        os.environ['APCB_MULTI_BOARD_SUPPORT'] = '1'
        os.environ['APCB_DATA_BOARD_DIR_LIST'] = os.environ.get('APCB_BOARD_LIST')
        os.environ['CUSTOM_APCB_PATH'] = os.path.normpath(os.path.join(
            build_output,
            'Apcb'
        ))

    build_apcb_board(soc_sku)
