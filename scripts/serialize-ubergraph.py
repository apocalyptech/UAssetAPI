#!/usr/bin/env python3
# vim: set expandtab tabstop=4 shiftwidth=4:

# Copyright 2022 Christopher J Kucera
# <cj@apocalyptech.com>
# <https://apocalyptech.com/contact.php>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Initial Imports
import os
import clr
import sys
import argparse
import pythonnet

# Load UAssetAPI.  We're attempting to be clever here.  Perhaps that will
# shoot us in the foot!  To hardcode the directory where UAssetAPI.dll is
# stored, rather than searching for it, set `dll_dir_override`
dll_dir_override = None
if dll_dir_override:
    dirs_to_search = [dll_dir_override]
else:
    my_dir = os.path.dirname(os.path.realpath(__file__))
    dirs_to_search = []
    dirs_to_search.append(my_dir)
    dirs_to_search.append(os.path.realpath(os.path.join(my_dir, '..', 'UAssetAPI', 'bin', 'Debug', 'netstandard2.0', 'publish')))
    dirs_to_search.append(os.path.realpath(os.path.join(my_dir, '..', 'UAssetAPI', 'bin', 'Release', 'netstandard2.0', 'publish')))
dll_found = False
for dir_name in dirs_to_search:
    if os.path.exists(os.path.join(dir_name, 'UAssetAPI.dll')):
        print(f'Loading UAssetAPI.dll from: {dir_name}')
        clr.AddReference(os.path.join(dir_name, 'UAssetAPI'))
        dll_found = True
        break
if not dll_found:
    print('WARNING: Could not find UAssetAPI.dll - Looked in the following places:')
    for dir_name in dirs_to_search:
        print(f' -> {dir_name}')
import UAssetAPI

def get_serializations(filename):
    """
    Given a filename, yields tuples containing the following:
       1. Export index (1-indexed, not 0-indexed)
       2. Export Name
       3. Serialized Ubergraph Bytecode
       4. "Raw" on-disk Bytecode (will not match in-memory bytecode!)
    """
    ass = UAssetAPI.UAsset(
            path=filename,
            engineVersion=UAssetAPI.UnrealTypes.EngineVersion.VER_UE4_20,
            )

    UAssetAPI.Kismet.KismetSerializer.asset = ass
    for idx, export in enumerate(ass.Exports):
        if hasattr(export, 'ScriptBytecode'):
            if export.ScriptBytecode:
                # Attempt serialization (return is an object, but stringifies nicely)
                serialized = UAssetAPI.Kismet.KismetSerializer.SerializeScript(export.ScriptBytecode)
                yield (idx+1, export.ObjectName, serialized, export.ScriptBytecodeRaw)

def main():

    parser = argparse.ArgumentParser(
            description='Serialize Ubergraph Bytecode using UAssetAPI',
            )

    parser.add_argument('-r', '--raw',
            action='store_true',
            help='Also save out raw bytecode',
            )

    parser.add_argument('--runtime',
            action='store_true',
            help='Show .NET runtime being used',
            )

    parser.add_argument('filename',
            type=str,
            nargs=1,
            help='Filename to process',
            )

    args = parser.parse_args()
    args.filename = args.filename[0]

    if args.runtime:
        print(pythonnet.get_runtime_info())

    obj_exts = {'uasset', 'umap'}
    _, filename_alone = os.path.split(args.filename)
    if '.' in filename_alone:
        filename_base, ext = args.filename.rsplit('.', 1)
    else:
        filename_base = args.filename
        ext = ''
    if ext not in obj_exts:
        for ext in obj_exts:
            if os.path.exists(f'{filename_base}.{ext}'):
                args.filename = f'{filename_base}.{ext}'
                break
    if not os.path.exists(args.filename):
        raise RuntimeError(f'Not found: {args.filename}')

    for index, name, serialization, raw in get_serializations(args.filename):
        to_filename = f'{filename_base}-ubergraph-{index:03d}-{name}.json'
        with open(to_filename, 'w') as odf:
            odf.write(str(serialization))
        print(f'Wrote to: {to_filename}')

        if args.raw:
            raw_filename = f'{filename_base}-ubergraph-{index:03d}-{name}.raw'
            with open(raw_filename, 'wb') as odf:
                odf.write(bytes(raw))
            print(f'Wrote raw to: {raw_filename}')

if __name__ == '__main__':
    main()

