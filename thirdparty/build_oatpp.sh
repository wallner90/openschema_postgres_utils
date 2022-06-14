#!/usr/bin/env bash

pushd /workspaces/openschema_postgres_utils/thirdparty
pushd oatpp
mkdir -p build && cd build
cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo .. && make -j8 && sudo make install
popd

pushd oatpp-postgresql
mkdir -p build && cd build
cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo .. && make -j8 && sudo make install
popd
popd