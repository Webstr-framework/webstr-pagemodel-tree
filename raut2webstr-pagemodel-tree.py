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


# list of python modules expected in RAUT page/model python module directory
RAUT_MODULES = ("models", "pages")


def is_py_file(filename):
    return filename.endswith(".py") and filename != "__init__.py"


def move_files(directory, raut_module, src_directory, src_files,
               dry_run=False, root_path=None):
    """
    Move python files (provided in ``src_files`` list) from given
    ``src_directory`` of a python module into new python module directory tree
    structure.

    Args:
        directory: full file path of directory which contains raut python
                   module directories (as listed in RAUT_MODULES list)
        raut_module: name of raut module (item from RAUT_MODULES list)
        src_directory (str): full file path of source (original) python module
        src_files (list): list of python files (in src_directory)
        dry_run (bool): don't touch anything, just show what "would be done"
        root_path (str): full file path of a project
    """
    # directory where new python modules created for each python source file from
    # ``src_files`` are going to be created
    new_directory = os.path.normpath(os.path.join(
        directory,
        os.path.relpath(
            src_directory,
            start=os.path.join(directory, raut_module))))
    for filename in src_files:
        # we are going to create a *new python module* in ``new_directory`` for
        # the python source file ``filename``
        new_module_path = os.path.join(new_directory, filename[:-3])
        new_module_init = os.path.join(new_module_path, "__init__.py")
        old_file_path = os.path.join(src_directory, filename)
        new_file_path = os.path.join(new_module_path, "{}.py".format(raut_module))
        if root_path is not None:
            import_path = os.path.relpath(new_module_path,
                                          root_path).replace('/', '.') + '.'
        if dry_run:
            print('mkdir -p {}'.format(new_module_path))
            print('touch {}'.format(new_module_init))
            print('mv {0} {1}'.format(old_file_path, new_file_path))
            if root_path is not None:
                print('echo "import {0}{1}\n" >> {2}'.format(import_path,
                                                             module_basename,
                                                             new_module_init))
        else:
            os.makedirs(new_module_path, exist_ok=True)
            os.open(new_module_init, os.O_CREAT, mode=0o664)
            os.rename(old_file_path, new_file_path)
            if root_path is not None:
                ini_file = open(new_module_init, 'a')
                ini_file.write('import {0}{1}\n'.format(import_path, module_basename))
                ini_file.close()


def main(argv=None):
    parser = argparse.ArgumentParser(
        description='convert raut page/model tree to webstr format')
    parser.add_argument(
        'directory',
        help='file path to page/model directory tree in raut format')
    parser.add_argument('-d', '--dry-run', action="store_true")
    parser.add_argument('-r', '--root-path', type=str,
                        help='root path of the project, the import path '
                             'will be constructed relatively to this path')
    args = parser.parse_args()

    # quick input validation
    if not os.path.isdir(args.directory):
        print("error: '{0}' is not a directory".format(args.directory))
        return 1
    if not os.path.isfile(os.path.join(args.directory, "__init__.py")):
        print("error: '{0}' is not a python module".format(args.directory))
        return 1
    for subdir in [os.path.join(args.directory, i) for i in RAUT_MODULES]:
        if not os.path.isdir(subdir):
            print("error: '{0}' directory is missing".format(subdir))
            return 1

    # do the transformation, happens in place
    empty_init_files = [] # list of empty __init__.py files
    for raut_module in RAUT_MODULES:
        for dirname, subdir_list, file_list in \
                os.walk(os.path.join(args.directory, raut_module)):
            python_files = [fl for fl in file_list if is_py_file(fl)]
            move_files(args.directory, raut_module, dirname, python_files,
                       dry_run=args.dry_run, root_path=args.root_path)
            if "__init__.py" in file_list and \
                    os.path.getsize(os.path.join(dirname, '__init__.py')) == 0:
                empty_init_files.append(os.path.join(dirname, "__init__.py"))

    # delete empty __ini__.py files in old page/model directories
    for init_file in empty_init_files:
        if args.dry_run:
            print("rm {}".format(init_file))
        else:
            os.remove(init_file)
    # delete any remaining raut directories (if empty)
    for raut_module in RAUT_MODULES:
        for dirname, subdir_list, file_list in os.walk(
                os.path.join(args.directory, raut_module), topdown=False):
            if args.dry_run:
                print("rmdir {}".format(dirname))
            elif len(os.listdir(dirname)) == 0:
                os.rmdir(dirname)


if __name__ == '__main__':
    sys.exit(main())
