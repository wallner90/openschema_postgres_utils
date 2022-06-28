# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.234.0/containers/cpp/.devcontainer/base.Dockerfile

# [Choice] Debian / Ubuntu version (use Debian 11, Ubuntu 18.04/22.04 on local arm64/Apple Silicon): debian-11, debian-10, ubuntu-22.04, ubuntu-20.04, ubuntu-18.04
ARG VARIANT="bullseye"
FROM mcr.microsoft.com/vscode/devcontainers/cpp:0-${VARIANT}

# [Optional] Install CMake version different from what base image has already installed. 
# CMake reinstall choices: none, 3.21.5, 3.22.2, or versions from https://cmake.org/download/
ARG REINSTALL_CMAKE_VERSION_FROM_SOURCE="none"

# Optionally install the cmake for vcpkg
COPY ./.devcontainer/reinstall-cmake.sh /tmp/
RUN if [ "${REINSTALL_CMAKE_VERSION_FROM_SOURCE}" != "none" ]; then \
        chmod +x /tmp/reinstall-cmake.sh && /tmp/reinstall-cmake.sh ${REINSTALL_CMAKE_VERSION_FROM_SOURCE}; \
    fi \
    && rm -f /tmp/reinstall-cmake.sh

# [Optional] Uncomment this section to install additional vcpkg ports.
# RUN su vscode -c "${VCPKG_ROOT}/vcpkg install <your-port-name-here>"

# add postgres keys and repo
RUN sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

# [Optional] Uncomment this section to install additional packages.
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install libboost-all-dev python3-pip \
                          aptitude vim \
                          lcov doxygen \
                          libpqxx-dev \
                          postgresql postgresql-contrib \ 
                          libpq-dev postgresql-server-dev-all \
                          libpdal-plugin-pgpointcloud postgresql postgis qgis  \


    && apt-get autoremove -y -qq \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install SQLAlchemy GeoAlchemy2 GeoPandas fiona pyproj rtree shapely msgpack-python

