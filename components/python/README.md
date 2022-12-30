# Python 3.7: build guide

This is a build recipes for the Python 3.7.10 which is used by AWS ParallelCluster 2.11.x. The SCIP
platform uses the same version to build binary dependencies that's compatible with ParallelCluster.

The created package includes all Python binaries as well as header files and configurtion scripts.
Hence, it can be installed either a Python runtime or build environment for compiling Python bindings.   

## Amazon 2: Build guide

    docker build --rm --tag build/scip-python/amazon:2 --file Dockerfile.amazon2 ./
