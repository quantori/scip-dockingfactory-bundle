#!/usr/bin/env make -f
# -*- makefile -*-

MYDIR_RELATIVE := $(dir $(lastword $(MAKEFILE_LIST)))
MYDIR := $(realpath $(MYDIR_RELATIVE))
RPM_PATH = /root/rpmbuild/RPMS/x86_64/
PARALLEL ?= 16
GO_VERSION=1.16
SINGULARITY_VERSION=3.9.6
OS=linux
export ARCH := $(shell uname -m)
.DEFAULT_GOAL := singularity

# Install golang as a build dependency for singularity
$(MYDIR)/tmp/golang/bin/go: GOLANG_ARCH := $(shell test "${ARCH}" = "aarch64" && echo arm64 || echo $(GOLANG_ARCH))
$(MYDIR)/tmp/golang/bin/go: GOLANG_ARCH := $(shell test "${ARCH}" = "x86_64" && echo amd64 || echo $(GOLANG_ARCH))
$(MYDIR)/tmp/golang/bin/go:
	@mkdir -p $(@D)
	@mkdir -p $(MYDIR)/tmp/golang/.cache
	curl -L https://dl.google.com/go/go${GO_VERSION}.${OS}-${GOLANG_ARCH}.tar.gz  | tar -xz -C $(MYDIR)/tmp/golang --strip-components 1
golang: $(MYDIR)/tmp/golang/bin/go

# Build RPM for singularity
$(RPM_PATH): $(MYDIR)/tmp/golang/bin/go
$(RPM_PATH): export GOPATH = $(MYDIR)/tmp/golang/
$(RPM_PATH): export PATH := $(GOPATH)/bin:$(PATH)
$(RPM_PATH):
	git clone https://github.com/sylabs/singularity.git $(GOPATH)/src/github.com/sylabs/singularity
	cd $(GOPATH)/src/github.com/sylabs/singularity/; git checkout v$(SINGULARITY_VERSION); \
	./mconfig && make -C builddir rpm RPMPREFIX=/shared/bundle/singularity

singularity: $(RPM_PATH)



