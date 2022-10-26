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
msbuild /p:Configuration=Release UAssetAPI.csproj
cp ../LICENSE ../NOTICE.md ../README.md ../scripts/*.py bin/Release/
cd bin
mv Release "${FULL}"
zip -r "${ZIP}" "${FULL}"
mv "${FULL}" Release
cd ..
cd ..

# Report on the resulting zipfile
echo
ls -lh "UAssetAPI/bin/${ZIP}"
echo

