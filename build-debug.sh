#!/bin/bash
# vim: set expandtab tabstop=4 shiftwidth=4:

cd UAssetAPI
msbuild /p:Configuration=Debug UAssetAPI.csproj
cd ..

