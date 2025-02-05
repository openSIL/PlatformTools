import os
import re


def build_sanity_check():
    """!
    Build sanity check with PI exclude list

    exception   various
    """

    # give preference to SupportedBuilds.json file
    exclude_file_name = os.environ.get ("EXCLUDE_LIST")
    if exclude_file_name is None:
        exclude_file_name = os.environ.get ("SOC")+"_ExcludeList.txt"

    excludefile = (
        "AmdCommonTools/Server/PiExcludeList/{}".format(exclude_file_name))
    buildfile = os.path.join(os.environ["BUILD_OUTPUT"], "build.log")
    excludefile = os.path.join(os.environ["WORKSPACE"], excludefile)
    if os.environ['AMD_PLATFORM_BUILD_TYPE'] == "INTERNAL":
        return
    if os.path.exists(buildfile) and os.path.exists(excludefile):
        print("Build PI sanity check ...")
        with open(buildfile, "r") as build_file:
            data = build_file.read().replace('\\', '/')
            with open(excludefile, "r") as exclude_list:
                for line in exclude_list:
                    searchline = line.lstrip().strip().replace('\\', '/')
                    if "*" in searchline:
                        # contains '*' hence need to regular expression
                        if searchline.startswith('*'):
                            # first character * means none or any character, trim it
                            searchline = searchline[1:]
                        if searchline.startswith('Internal'):
                            # Special case for Internal, look only in PI delivered packages
                            searchline = "(?:AgesaPkg|AgesaModulePkg|AmdCpmPkg)/*.*/" + searchline
                        foundre = set(re.findall(searchline, data))
                        if foundre:
                            #
                            # this is failure scenario
                            # which means we found a file/directory which is in ExcludeList but consumed during
                            # building the BIOS.
                            # Hence print the file/directory name and exit with failure.
                            #
                            #
                            # ignore InternalSwitchStack which is part of edk2 but consumed by AmdCpmPkg
                            #
                            if str(foundre).find ("InternalSwitchStack") == -1:
                                print("!!! ERROR !!!: The build has a file or directory which is excluded.: {}".format(
                                foundre))
                                exit (1)
                    else:
                        if "." not in searchline:
                            if not searchline.endswith('//'):
                                searchline = "".join((searchline, '/'))
                        if searchline in data:
                            print("!!! ERROR !!!: The build has a file or directory which is excluded.: {}".format(
                                searchline))
                            exit (1)
        print("Done.")
