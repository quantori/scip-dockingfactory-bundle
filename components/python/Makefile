#!/usr/bin/env make -f
# -*- makefile -*-

.DEFAULT_GOAL = python.rpm
# A path where this file is placed
MYDIR := $(dir $(lastword $(MAKEFILE_LIST)))
BUILDDIR ?= $(MYDIR).build
SHELL := /bin/bash

PYTHON_VERSION ?= 3.7.10
PYTHON_INSTALL_PREFIX ?= $(BUILDDIR)/scip-python
PARALLEL ?= 16


$(BUILDDIR)/Python-$(PYTHON_VERSION).tar.xz:
	@mkdir -p $(@D)
	curl -o $@ https://www.python.org/ftp/python/$(PYTHON_VERSION)/Python-$(PYTHON_VERSION).tar.xz

python.rpm: RPM_SPEC=$(MYDIR)/scip-python3.spec
python.rpm: SOURCEDIR ?= $(BUILDDIR)/SOURCES
python.rpm: $(RPM_SPEC) $(BUILDDIR)/Python-$(PYTHON_VERSION).tar.xz
	@mkdir -p $(BUILDDIR)/{BUILD,RPMS,SRPMS}
	rpmbuild -D "_topdir $(BUILDDIR)" \
	         -D "_sourcedir $(SOURCEDIR)" \
	         -D "_prefix $(PYTHON_INSTALL_PREFIX)" \
	         -D "debug_package %{nil}" \
	         -bb "$<"
