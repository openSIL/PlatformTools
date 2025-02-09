"""
*******************************************************************************
 Copyright (C) 2021-2022 Advanced Micro Devices, Inc. All rights reserved.

*******************************************************************************
"""

from genericpath import exists
from buildsupport import build_module_only, build_show_only, build_quick

import sys
import os
import shutil
import subprocess


def insert_psp_directory():
    """!
    Insert the PSP Directory components into the BIOS binary image

    exception   various
    """
    print('\nInserting PSP Directory')
    if build_module_only():
        print('Skip Inserting PSP Directory')
        return

    # Get environment variables exception if not located
    workspace = os.environ['WORKSPACE']
    soc_sku = os.environ['SOC_SKU']
    soc = os.environ['SOC']
    soc_sku_2 = os.environ.get("SOC_SKU_2")
    firmware_version = os.environ['FIRMWARE_VERSION_STR']

    # Get PSP XML directory
    try:
        # Back to board directory
        psp_platform_dir = os.path.join(os.environ['EDK2_OPENBOARD_SUPPORTED_DIR'], '../')
        psp_platform_common_dir = os.path.join(os.environ['EDK2_OPENBOARD_SUPPORTED_DIR'], '../../')
    except:
        psp_platform_dir = os.environ['AMD_PLATFORM_DIR']
        psp_platform_common_dir = os.environ['AMD_COMMON_PLATFORM_DIR']

    platform_common_dir = os.environ['AMD_COMMON_PLATFORM_DIR']
    build_output = os.environ['BUILD_OUTPUT']
    custom_apcb_path = os.environ['CUSTOM_APCB_PATH']
    python_home = os.environ['PYTHON_HOME'].strip('"').strip("'")

    if sys.platform == "linux":
        python_exe = "python3"
    elif sys.platform.startswith("win"):
        python_exe = "python.exe"
    python = os.path.normpath(os.path.join(python_home, python_exe))

    psp_workspace = os.path.join(build_output, 'PSP_DIR')

    build_psp_directory = os.path.join(
        workspace,
        'AGESA/AgesaModulePkg/AMDTools/',
        'NewPspKit/PspDirectoryTool',
        'BuildPspDirectory.py'
    )
    bios_image = os.path.join(build_output, 'FV/PLATFORM.fd')
    output_image = '{}.FD'.format(firmware_version)
    psp_output = os.path.join(workspace, '')

    # Paths of files to copy
    firmware_dir = os.path.join(
        workspace,
        'AGESA/AgesaModulePkg/Firmwares',
        soc_sku
    )

    if soc_sku_2 is not None:
        firmware_dir_soc_2 = os.path.join(
            workspace,
            'AGESA/AgesaModulePkg/Firmwares',
            soc_sku_2
        )

    bios_image_xml_file = 'PspData{}.xml'.format(
    soc_sku.lower().capitalize())

    # Check to see if the user board-specific PspData xml file exists.
    if (os.path.exists(os.path.join(psp_platform_dir, bios_image_xml_file))):
        bios_image_xml = os.path.join(psp_platform_dir, bios_image_xml_file)
        print("INFO: Using board specific {} file.".format(bios_image_xml_file))
    else:
        bios_image_xml = os.path.join(psp_platform_common_dir, bios_image_xml_file)
        print("INFO: board specific {} file not found, using common file.".format(
            bios_image_xml_file))

    # Get SBIOS platform binaries
    platform_binaries = os.path.join(
        platform_common_dir,
        'Binaries'
    )

    # Copy required files
    if soc_sku_2 is not None:
        copy_dirs = (firmware_dir, firmware_dir_soc_2, custom_apcb_path, platform_binaries)
    else:
        copy_dirs = (firmware_dir, custom_apcb_path, platform_binaries)

    print('psp_workspace: {}'.format(psp_workspace))
    for copy_dir in copy_dirs:
        for root, dirs, files in os.walk(copy_dir):
            for file in files:
                src = os.path.join(root, file)
                dst = os.path.join(psp_workspace, src[len(copy_dir) + 1:])
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy(src, dst)
    sys.stdout.flush()
    with subprocess.Popen(
            [
                os.path.join(python_home, python_exe),
                build_psp_directory,
                '-o', psp_output,
                'bb',
                bios_image,
                bios_image_xml,
                output_image
            ], cwd=psp_workspace) as p:
        p.wait()
        if p.returncode != 0:
            error_text = 'Return code = {}'.format(p.returncode)
            print(error_text)
            raise ValueError(error_text)
