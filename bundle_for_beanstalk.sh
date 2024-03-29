#!/bin/bash

#rebuild node app
pushd ./frontend
if [ ! -d "./node_modules" ]; then
    exec npm ci &
    wait
fi
exec npm run build &
wait

pushd ..

# create the bundle
rm -rf ./bundle
mkdir ./bundle
mkdir ./bundle/.ebextensions
mkdir ./bundle/conf
cp -r ./conf/.ebextensions ./bundle
cp -r ./frontend/dist ./bundle/frontend
cp ./conf/backend.config ./bundle/conf/backend.config
cp ./backend/requirements.txt ./bundle/requirements.txt
cp ./backend/application.py ./bundle/application.py
cp -r ./.ebextensions ./bundle
pushd bundle

rm -rf ../eb_bundle*.zip
# today=`date '+%Y-%m-%d--%H-%M-%S'`
# zip -r ../eb_bundle-rac-interface-$today.zip -r * .[^.]*
zip -r ../eb_bundle-rac-interface.zip -r * .[^.]*

#remove the temporary bundle directory
pushd ..
rm -rf ./bundle


exec eb deploy -v &
wait
exec eb status -v 
