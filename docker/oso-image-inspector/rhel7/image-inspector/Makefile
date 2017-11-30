# Old-skool build tools.
#
# Targets (see each target for more information):
#   all: Build code.
#   build: Build code.
#   test-unit: Run unit tests.
#   clean: Clean up.

OUT_DIR = _output

# Build code.
#
# Example:
#   make
#   make all
all build:
	hack/build-go.sh
.PHONY: all build

# Remove all build artifacts.
#
# Example:
#   make clean
clean:
	rm -rf $(OUT_DIR)
.PHONY: clean

# Verify code conventions are properly setup.
#
# Example:
#   make verify
verify: build
	hack/verify-gofmt.sh
.PHONY: verify

# Run unit tests.
#
# Args:
#   WHAT: Directory names to test.  All *_test.go files under these
#     directories will be run.  If not specified, "everything" will be tested.
#   TESTS: Same as WHAT.
#   GOFLAGS: Extra flags to pass to 'go' when building.
#   TESTFLAGS: Extra flags that should only be passed to hack/test-go.sh
#
# Example:
#   make test-unit
#   make test-unit WHAT=pkg/build GOFLAGS=-v
test-unit:
	GOTEST_FLAGS="$(TESTFLAGS)" hack/test-go.sh $(WHAT) $(TESTS)
.PHONY: test-unit

# Install travis dependencies
#
install-travis:
	hack/install-tools.sh
.PHONY: install-travis
