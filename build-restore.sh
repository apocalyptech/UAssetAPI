#!/bin/bash
# vim: set expandtab tabstop=4 shiftwidth=4:

cd UAssetAPI
msbuild -t:Restore UAssetAPI.csproj
cd ..

