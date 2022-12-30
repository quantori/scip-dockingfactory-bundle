#!/usr/bin/env make -f
# -*- makefile -*-

.DEFAULT_GOAL = build
# A path where this file is placed
MYDIR := $(dir $(lastword $(MAKEFILE_LIST)))
BUILDDIR ?= $(MYDIR).build

CMAKE3 ?= /usr/local/bin/cmake
OPENBABEL_VERSION ?= 3-1-1
OPENBABEL_INSTALL_PREFIX ?= $(BUILDDIR)/openbabel


$(BUILDDIR)/openbabel-$(OPENBABEL_VERSION).tar.gz:
	@mkdir -p $(@D)
	rm -rf $(BUILDDIR)/openbabel
	curl -Ls -o $(BUILDDIR)/openbabel-$(OPENBABEL_VERSION).tar.gz https://github.com/openbabel/openbabel/archive/openbabel-$(OPENBABEL_VERSION).tar.gz

$(BUILDDIR)/sourcecode/CMakeLists.txt: $(BUILDDIR)/openbabel-$(OPENBABEL_VERSION).tar.gz
	@mkdir -p $(@D)
	tar -xf $< --strip 1 -C $(@D)

$(BUILDDIR)/build/Makefile: $(BUILDDIR)/sourcecode/CMakeLists.txt
	patch -d $(dir $<) -p0 < $(MYDIR)/openbabel.patch
	$(CMAKE3) -DBOOST_ROOT=$(BOOSTROOT) \
              -DBoost_NO_SYSTEM_PATHS=1 -DBoost_NO_BOOST_CMAKE=1 \
	          -DCMAKE_INSTALL_PREFIX:PATH=$(OPENBABEL_INSTALL_PREFIX) \
		  -DPYTHON_BINDINGS=OFF \
	          -S $(dir $<) \
	          -B $(dir $@)

$(BUILDDIR)/build/install_manifest.txt: $(OPENBABEL_INSTALL_PREFIX)/lib/openbabel $(BUILDDIR)/build/Makefile

$(OPENBABEL_INSTALL_PREFIX)/lib/openbabel: $(BUILDDIR)/build/Makefile
	$(CMAKE3) --install $(dir $<) --prefix $(OPENBABEL_INSTALL_PREFIX)

.PHONY: build
build: $(BUILDDIR)/build/Makefile
	$(CMAKE3) --build $(dir $<) -j 4

.PHONY: install
install: $(OPENBABEL_INSTALL_PREFIX)/lib/openbabel

.PHONY: clean
clean:
	rm -rf $(BUILDDIR)/openbabel $(BUILDDIR)/build $(BUILDDIR)/sourcecode
	rm -f  $(BUILDDIR)/openbabel-*.tar.gz

clean-installed:
	xargs rm < $(BUILDDIR)/build/install_manifest.txt
