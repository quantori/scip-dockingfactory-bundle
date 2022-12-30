#!/usr/bin/env make -f
# -*- makefile -*-


RPM_SPEC := $(dir $(lastword $(MAKEFILE_LIST)))/scip-auth-ad.spec

include $(dir $(RPM_SPEC))/../../ops-tools/Makefile

all: rpm deploy clean

rpm/%: $(RPM_SPEC)
	@mkdir -p $(BUILDDIR)/rpmbuild/{BUILD,RPMS,SRPMS}
	rpmbuild -D "_topdir $(BUILDDIR)/rpmbuild" \
	         -D "_sourcedir $(abspath $(dir $(RPM_SPEC)))" \
	         --target $* \
	         -bb "$<"

.PHONY: rpm
rpm: rpm/aarch64 rpm/x86_64

s3upload/%:
	find $(BUILDDIR)/rpmbuild/RPMS/$(notdir $*) -name *.rpm -type f -exec \
	     $(AWSCMD) s3 cp {} s3://$(SCIP_DEPLOYMENT_BUCKET)/RPM/$*/Packages/ \;

.PHONY: deploy
deploy: s3upload/amazon/2/aarch64 s3upload/amazon/2/x86_64 s3upload/centos/7/x86_64

clean:
	rm -rf $(BUILDDIR)/rpmbuild
