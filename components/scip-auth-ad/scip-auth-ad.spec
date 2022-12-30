Name:             scip-auth-ad
Summary:          Utilities to integrate SciP cluster nodes with Active Directory
Version:          1.3.0
Release:          0
License:          Proprietary
Group:            HPC/Scientific Data Platform
Vendor:           Quantori
Packager:         Quantori SCIP team, <????@quantori.com>
#BuildRequires:    systemd
Requires:         authconfig
Requires:         bind-utils
Requires:         krb5-workstation
Requires:         oddjob-mkhomedir
Requires:         sed
Requires:         sssd
Requires:         systemd
Requires:         sudo

%if "%{?_arch}" == "x86_64"
%global golang_arch "amd64"
%else
%if "%{?_arch}" == "aarch64"
%global golang_arch "arm64"
%else
%global golang_arch "unknown"
%endif
%endif

%global _unitdir %{_prefix}/lib/systemd/system

%description
This package configures sssd daemon for integration SciP cluster instances
with authentication/authorization through Active Directory (AWS SimpleAD).

%prep
test -h etc && unlink etc || :;
%{__ln_s} -f $RPM_SOURCE_DIR/etc etc

%install
%{__install} -m 0775 -d %{buildroot}/%{_bindir} 
curl -sSL -o %{buildroot}/%{_bindir}/gomplate \
     https://github.com/hairyhenderson/gomplate/releases/download/v3.10.0/gomplate_linux-%{golang_arch}

# Install Kerberos configuration
%{__install} -m 0700 -d %{buildroot}/%{_sysconfdir}/skel/Logs
%{__install} -m 0775 -d %{buildroot}/%{_sysconfdir}/scip-auth-ad/krb5.conf.d %{buildroot}/%{_sysconfdir}/scip-auth-ad/sssd
%{__install} -t %{buildroot}%{_sysconfdir}/scip-auth-ad/krb5.conf.d ${RPM_SOURCE_DIR}/etc/scip-auth-ad/templates/krb5.conf.d/*
%{__install} -t %{buildroot}%{_sysconfdir}/scip-auth-ad/sssd ${RPM_SOURCE_DIR}/etc/scip-auth-ad/templates/sssd/*

# Install SSH conifgs
%{__install} -m 0775 -d %{buildroot}/%{_sysconfdir}/scip-auth-ad/ssh
%{__install} -t %{buildroot}%{_sysconfdir}/scip-auth-ad/ssh ${RPM_SOURCE_DIR}/etc/ssh/*

# Install SSSD conifgs and templates
%{__install} -m 0775 -d %{buildroot}/%{_sysconfdir}/sssd/conf.d
%{__install} -t %{buildroot}%{_sysconfdir}/sssd etc/sssd/sssd.conf etc/sssd/sssd-configure
%{__install} -t %{buildroot}%{_sysconfdir}/sssd/conf.d ${RPM_SOURCE_DIR}/etc/sssd/conf.d/*

# Install sudoers configs
%{__install} -m 0775 -d %{buildroot}/%{_sysconfdir}/sudoers.d
%{__install} -t %{buildroot}%{_sysconfdir}/sudoers.d ${RPM_SOURCE_DIR}/etc/sudoers.d/*

# Install systemd unit config
%{__install} -m 0775 -d %{buildroot}%{_unitdir}/systemd-logind.service.d
%{__install} -t %{buildroot}%{_unitdir} ${RPM_SOURCE_DIR}/systemd/system/*.service
%{__install} -t %{buildroot}%{_unitdir}/systemd-logind.service.d ${RPM_SOURCE_DIR}/systemd/system/systemd-logind.service.d/*


%files
%defattr(0600,root,root,-)
%attr(0755,root,root) %{_bindir}/gomplate
%attr(0700,root,root) %{_sysconfdir}/skel/Logs

%{_sysconfdir}/scip-auth-ad

%{_sysconfdir}/sssd/
%exclude %dir %{_sysconfdir}/sssd/conf.d
%exclude %dir %{_sysconfdir}/sssd

%{_sysconfdir}/sudoers.d/
%exclude %dir %{_sysconfdir}/sudoers.d

%{_unitdir}
%exclude %dir %{_unitdir}

%post
systemctl enable scip-auth-ad.service
systemctl restart scip-auth-ad.service sssd.service
authconfig --update --enablemkhomedir --enablesssd --enablesssdauth
# FIX: it's impossible to create dcv session: https://bugs.freedesktop.org/show_bug.cgi?id=66867
systemctl is-active dbus.service && systemctl restart dbus.service

%changelog
* Thu Feb 24 2022 Anton Talevnin <anton.talevnin@quantori.com> - 1.3.0-0
- Enabled ID mapping for usres and groups from Active Directory

* Wed Feb 02 2022 Anton Talevnin <anton.talevnin@quantori.com> - 1.2.1-0
- Restart dbus.service to permit AD users create DCV sessions:
  (fix error: Exhausted all available authentication mechanisms)

* Mon Jan 17 2022 Anton Talevnin <anton.talevnin@quantori.com> - 1.2.0-0
- Templatize Kerberos config to customize REALM depending on installation

* Wed Nov 24 2021 Anton Talevnin <anton.talevnin@quantori.com> - 1.1.0-0
- Permit sudo for hpc-sudoers group without password
- Permit authenticate with password for *.* users through ssh

* Sun Oct 31 2021 Anton Talevnin <anton.talevnin@quantori.com> - 1.0.0-0
- Kerberos client and SSSD configuration templates are added
- Process templates with gomplate using scip-auth-ad.service
