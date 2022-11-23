#!/bin/bash
# vim: set expandtab tabstop=4 shiftwidth=4:

# Could auto-restore nuget stuff by including `-r` in the msbuild args
cd UAssetAPI
msbuild -t:Publish -p:Configuration=Debug UAssetAPI.csproj
cd ..

