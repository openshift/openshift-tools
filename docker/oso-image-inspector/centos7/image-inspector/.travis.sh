#!/usr/bin/env bash

function build_container(){
    docker build -t travis/image-inspector-base .
    docker build -t travis/image-inspector -f Dockerfile.travis .
}

function run_tests(){
  docker run --rm --privileged \
             -v /var/run/docker.sock:/var/run/docker.sock \
             --entrypoint make \
             travis/image-inspector verify test-unit
}

function usage() {
    echo "usage: .travis.sh build|run"
    exit 1
}

case "$1" in
    build)
        build_container
        ;;
    run)
        run_tests
        ;;
    *)
        usage
        ;;
esac
