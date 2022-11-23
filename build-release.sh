#!/bin/bash
# vim: set expandtab tabstop=4 shiftwidth=4:

# Check to make sure a tag is supplied
TAG="$1"
if [ "z${TAG}" == "z" ]
then
    echo "Supply a release name as the single arg!"
    exit 1
fi
FULL="UAssetAPI-${TAG}"
ZIP="${FULL}.zip"

# Check to make sure the tag is unique
if [ -f "UAssetAPI/bin/${ZIP}" ]
then
    echo "${FULL}.zip already exists; refusing to overwrite"
    exit 2
fi

# Run the release
cd UAssetAPI
rm -rf bin/Release
# Could auto-restore nuget stuff by including `-r` in the msbuild args
msbuild -t:Publish -p:Configuration=Release UAssetAPI.csproj
cp ../LICENSE ../NOTICE.md ../README.md ../scripts/*.py bin/Release/netstandard2.0/publish
cd bin/Release/netstandard2.0
mv publish "${FULL}"
zip -r "../../${ZIP}" "${FULL}"
mv "${FULL}" publish
cd ..
cd ..
cd ..
cd ..

# Report on the resulting zipfile
echo
ls -lh "UAssetAPI/bin/${ZIP}"
echo

