#!/bin/bash

echo "--> building run-clam-scan ..."
go build -o run-clam-scan/run-clam-scan run-clam-scan/main.go

echo "--> copying image-inspector ..."
cp ../../../_output/local/bin/local/image-inspector .

echo "--> building docker.io/mfojtik/clamav-scan:latest ..."
docker build --quiet -t docker.io/mfojtik/clamav-scan:latest .
