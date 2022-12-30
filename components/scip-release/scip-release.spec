Name:             scip-release
Summary:          YUM/DNF configuration for Quantori SCIP packages
Version:          1.1.0
Release:          2
BuildArch:        noarch
License:          Proprietary
Group:            HPC/Scientific Data Platform
Vendor:           Quantori
Packager:         Quantori SCIP team, <????@quantori.com>
#BuildRequires:    gettext
Requires:         coreutils

%{!?scip_environment: %define scip_environment develop}

%description
This package contains the YUM/DNF configuration as well as
GPG key for Quantori SCIP repository and packages

%prep
test -h etc && unlink etc || :;
%{__ln_s} -f $RPM_SOURCE_DIR/etc etc

%install
%{__install} -m 0775 -d %{buildroot}/%{_sysconfdir}/yum.repos.d
%{__install} -m 0644 etc/yum.repos.d/* %{buildroot}%{_sysconfdir}/yum.repos.d/

cat > %{buildroot}%{_sysconfdir}/scip-release.defaults <<- EOF
	# AWS S3 bucket where binaries and packages are located
	SCIP_DEPLOYMENT_BUCKET=\${SCIP_DEPLOYMENT_BUCKET:-%{scip_deployment_bucket}}
	
	# Environment name
	SCIP_ENVIRONMENT=\${SCIP_ENVIRONMENT:-%{scip_environment}}
	
	# An owner of the installation
	SCIP_OWNER=\${SCIP_OWNER:-%{scip_owner}}
EOF

%files
%defattr(-,root,root,-)
%{_sysconfdir}/yum.repos.d/scip.repo
%{_sysconfdir}/scip-release.defaults

%preun
rm -f /etc/yum/vars/scip*
rm -f %{_sysconfdir}/scip-release %{_sysconfdir}/scip-release.*

%post
init_scip_release() {
    local defaults=%{_sysconfdir}/scip-release.defaults
    local customized=%{_sysconfdir}/scip-release.${SCIP_OWNER:-defaults}
    test -f "$customized" || {
      (echo "cat <<EOF" ; cat $defaults ; echo EOF) | sh > "${customized}"
    }
    ln -s -f "$customized" %{_sysconfdir}/scip-release
}

init_scip_release

source /etc/os-release
source %{_sysconfdir}/scip-release
test "${ID}x" == "amznx" && ID=amazon
echo "${ID}" > %{_sysconfdir}/yum/vars/scipdist
echo "${SCIP_DEPLOYMENT_BUCKET}" > %{_sysconfdir}/yum/vars/scipbucket


%changelog

* Fri Jan 14 2022 Anton Talevnin <anton.talevnin@quantori.com> - 1.1.0
- Ability to customize /etc/scip-release through environment variables

* Wed Sep 15 2021 Anton Talevnin <anton.talevnin@quantori.com> - 1.0.0
- Initial version. YUM configuration is added
