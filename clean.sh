#!/bin/bash
# vim: set expandtab tabstop=4 shiftwidth=4:

cd UAssetAPI
msbuild /t:Clean UAssetAPI.csproj
msbuild /p:Configuration=Release /t:Clean UAssetAPI.csproj
cd ..

