package main

import (
	"bufio"
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"os/exec"

	"github.com/openshift/image-inspector/pkg/api"
)

const (
	ClamDaemonPath = "/usr/sbin/clamd"
	InspectorPath  = "/usr/bin/image-inspector"
)

var (
	ClamDaemonDefaultArgs = []string{
		"--config-file", "/etc/clamd.d/local.conf",
	}
	InspectorDefaultArgs = []string{
		"-clam-socket", "/tmp/clamd.sock",
		"-dockercfg", "/secrets/docker/.dockercfg",
		"-path", "/image-data",
		"-scan-type", "clamav",
		"-post-results-url", "http://127.0.0.1:8080/",
	}
)

func RunClam(ready chan struct{}) error {
	cmd := exec.Command(ClamDaemonPath, ClamDaemonDefaultArgs...)
	stdout, err := cmd.StdoutPipe()
	cmd.Stderr = os.Stderr
	if err != nil {
		return err
	}
	go func() {
		r := bufio.NewReader(stdout)
		for {
			line, _, err := r.ReadLine()
			if err == io.EOF {
				log.Fatalf("Failed to run clamd")
				break
			}
			if err != nil {
				log.Fatalf("Failed to read clamd output: %v", err)
			}
			if bytes.Contains(line, []byte("Listening daemon")) {
				log.Printf("clamd is ready to scan ...")
				close(ready)
				break
			}
		}
	}()
	if err := cmd.Start(); err != nil {
		return err
	}
	go cmd.Wait()
	return nil
}

func RunResultsServer(result chan api.ScanResult) error {
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		body, err := ioutil.ReadAll(r.Body)
		if err != nil {
			log.Fatalf("Error reading response body: %v", err)
		}
		resultObj := api.ScanResult{}
		if err := json.Unmarshal(body, &resultObj); err != nil {
			log.Fatalf("Error parsing response body: %v", err)
		}
		log.Printf("--> Scan report received, %d problems found ...", len(resultObj.Results))
		result <- resultObj
	})

	go func() {
		log.Printf("--> Waiting for scan results on 127.0.0.1:8080 ...")
		http.ListenAndServe("127.0.0.1:8080", nil)
	}()
	return nil
}

func RunInspector(image string) error {
	inspectorArgs := InspectorDefaultArgs
	inspectorArgs = append(inspectorArgs, []string{"-image", image}...)

	cmd := exec.Command(InspectorPath, inspectorArgs...)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	if err := cmd.Start(); err != nil {
		return err
	}
	return cmd.Wait()
}

func ValidateEnv() error {
	if len(os.Getenv("TARGET_IMAGE")) == 0 {
		return errors.New("must specify TARGET_IMAGE variable")
	}
	if _, err := os.Stat(ClamDaemonPath); os.IsNotExist(err) {
		return fmt.Errorf("clamd not available at %q", ClamDaemonPath)
	}
	if _, err := os.Stat(InspectorPath); os.IsNotExist(err) {
		return fmt.Errorf("image-inspector not available at %q", InspectorPath)
	}

	return nil
}

func main() {
	if err := ValidateEnv(); err != nil {
		log.Fatalf("Error: %v", err)
	}

	clamIsReady := make(chan struct{})
	if err := RunClam(clamIsReady); err != nil {
		log.Fatalf("Error running clamd: %v", err)
	}
	// Wait until clamd is fully initialized.
	<-clamIsReady

	results := make(chan api.ScanResult)
	err := RunResultsServer(results)
	if err != nil {
		log.Fatalf("Error running result server: %v", err)
	}

	if err := RunInspector(os.Getenv("TARGET_IMAGE")); err != nil {
		log.Fatalf("Error running image inspector: %v", err)
	}

	report := <-results
	log.Printf("report=%#v", report)
}
