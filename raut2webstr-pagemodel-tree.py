#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""
raut2webstr-pagemodel-tree script
"""

# Copyright 2016 Martin Bukatovič <mbukatov@redhat.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import argparse
import os
import sys


# list of python modules expected in page/model python module directory
MODULES = ("models", "pages")


def is_py_file(filename):
    return filename.endswith(".py") and filename != "__init__.py"


def move_files(directory, src_module, src_files, dry_run=False):
    """
    Move python files (provided in src_files) from given src_module
    into new structure, which is created in given directory.
    """
    for filename in src_files:
        # dropping ".py" suffix
        new_module_path = os.path.join(directory, filename[:-3])
        new_module_ini_path = os.path.join(new_module_path, "__ini__.py")
        old_file_path = os.path.join(directory, src_module, filename)
        new_file_path = os.path.join(new_module_path, "{}.py".format(src_module))
        if dry_run:
            print('mkdir {}'.format(new_module_path))
            print('touch {}'.format(new_module_ini_path))
        else:
            try:
                os.mkdir(new_module_path)
            except FileExistsError:
                pass
            os.open(new_module_ini_path, os.O_CREAT, mode=0o664)
        if dry_run:
            print('mv {0} {1}'.format(old_file_path, new_file_path))
        else:
            os.rename(old_file_path, new_file_path)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description='convert raut page/model tree to webstr format')
    parser.add_argument(
        'directory',
        help='file path to page/model directory tree in raut format')
    parser.add_argument('-d', '--dry-run', action="store_true")
    args = parser.parse_args()

    # quick input validation
    if not os.path.isdir(args.directory):
        print("error: '{0}' is not a directory".format(args.directory))
        return 1
    if not os.path.isfile(os.path.join(args.directory, "__init__.py")):
        print("error: '{0}' is not a python module".format(args.directory))
        return 1
    for subdir in [os.path.join(args.directory, i) for i in MODULES]:
        if not os.path.isdir(subdir):
            print("error: '{0}' directory is missing".format(subdir))
            return 1

    # find python files
    files = {} # page or model modules which we are going to rename
    empty_init_files = [] # empty __init__.py files
    for module in MODULES:
        for dirname, subdir_list, file_list in \
                os.walk(os.path.join(args.directory, module)):
            files[module] = [fl for fl in file_list if is_py_file(fl)]
            if "__init__.py" in file_list:
                empty_init_files.append(os.path.join(dirname, "__init__.py"))

    # do the transformation, happens in place
    for mod in MODULES:
        move_files(args.directory, mod, files[mod], dry_run=args.dry_run)
    # delete empty __ini__.py files in old page/model directories
    for init_file in empty_init_files:
        if args.dry_run:
            print("rm {}".format(init_file))
        else:
            os.remove(init_file)
    # delete page/model directories (if empty)
    for mod in MODULES:
        mod_path = os.path.join(args.directory, mod)
        if args.dry_run:
            print("rmdir {}".format(mod_path))
        elif len(os.listdir(mod_path)) == 0:
            os.rmdir(mod_path)


if __name__ == '__main__':
    sys.exit(main())
