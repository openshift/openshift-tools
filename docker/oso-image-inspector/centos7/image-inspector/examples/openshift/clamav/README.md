# Running clamav image scan in OpenShift example

This example shows how you can run the image-inspector in OpenShift infrastructure using
the ClamAV scan type to identify problems with the image.

Note that this example is just a PoC and should not be used in production as it just
demostrate the use-case.

## Preparing scanner image

To build the scanner image from scratch you can run:

```
cd examples/openshift/clamav
./build.sh
```

This will build `docker.io/mfojtik/clamav-scan:latest` (you can replace that with custom
name).

Otherwise you can use the pre-built `docker.io/mfojtik/clamav-scan:latest` image.

## Deploying in OpenShift

To run the scan of an image in OpenShift cluster, you can run the following command:

```
oc create -f examples/openshift/clamav/clam-scan.yaml
```

Running this command will create a Pod using the `docker.io/mfojtik/clamav-scan:latest`
image and scan the `docker.io/mfojtik/virus-test:latest` image with ClamAV. The sample
image contains `./virus` file which contains clamav EICAR signature that the scan
should report as "virus".

To target different image for scan, open the `clam-scan.yaml` file and replace the
`TARGET_IMAGE` variable value.

To see the scan logs you can use `oc logs` command.

## Caveats

* Currently running the scan requires **privileged** container so the image-inspector can
  access the Docker socket file on the host to pull the image into the Pod container.
  To allow this in OpenShift, you have to be "system:admin" user and edit the SCC
  policies: `oc edit scc restricted --as=system:admin`.

  Make sure these policies are allowed:
  - allowPrivilegedContainer
  - allowHostDirVolumePlugin
