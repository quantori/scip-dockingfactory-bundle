%define version_parts()  %(/bin/python3 -c 'print("%1-0".split("-")[%2])')

%global slurm_version %{version_parts %slurm_full_version 0}
%global slurm_release %{version_parts %slurm_full_version 1}

Name:             scip-slurmrestd
Summary:          Slurm REST API binaries and plugins for SCIP platform
Version:          %slurm_version
Release:          %slurm_release
License:          GPLv2+
Group:            HPC/Scientific Data Platform
Vendor:           Quantori
Packager:         Quantori SCIP team, <????@quantori.com>
URL:              https://slurm.schedmd.com/
Requires:         coreutils http-parser json-c libyaml libjwt
BuildRequires:    http-parser-devel

Source0: https://github.com/SchedMD/slurm/archive/refs/tags/slurm-%{version}.tar.gz
Source1: slurm_scip.conf
Source2: slurmrestd.service

%define _unpackaged_files_terminate_build 0
# Exclude from dependencies which are provided by AWS ParalellCluster
%define __requires_exclude libslurmfull.so

%description
Slurm REST API binaries and plugins 

%prep
%setup -n slurm-slurm-%(/bin/python3 -c "print('%slurm_full_version'.replace('.', '-'))")

%build
./configure \
    --disable-debug \
    --prefix=/opt/slurm \
    --with-pmix=$($PKG_CONFIG --variable=prefix pmix)
CORES=$(grep processor /proc/cpuinfo | wc -l)
make -j $CORES

%install
%{__install} -m 0775 -d %{buildroot}/opt/slurm/{sbin,etc,lib}
%{__install} -m 0644 %{_sourcedir}/slurm_scip.conf %{buildroot}/opt/slurm/etc/

%{__install} -m 0775 -d %{buildroot}/%{_sysconfdir}/systemd/system
%{__install} -m 0644 %{_sourcedir}/slurmrestd.service %{buildroot}/%{_sysconfdir}/systemd/system/
make install DESTDIR=%{buildroot}

# Remove everything beside Slurm REST libriries
find %{buildroot} -name '*.a' -exec rm {} \;
find %{buildroot} -name '*.la' -exec rm {} \;

%files
%defattr(-,root,root,-)
%config %{_sysconfdir}/systemd/system/slurmrestd.service
/opt/slurm/sbin/slurmrestd
%config /opt/slurm/etc/slurm_scip.conf
/opt/slurm/lib/slurm/auth_jwt.so
/opt/slurm/lib/slurm/openapi_*.so
/opt/slurm/lib/slurm/rest_auth_*.so

%preun
systemctl stop slurmrestd.service

%pre
test -f /opt/slurm/etc/slurm_parallelcluster.conf || {
  printf "Can't find an AWS ParalellCluster installation in /opt/slurm directory"
  exit 7
}

%post
SLURM_JWT_KEY_FILE=/opt/slurm/etc/jwt_hs256.key
dd if=/dev/random of=${SLURM_JWT_KEY_FILE} bs=32 count=1 
chown slurm:slurm ${SLURM_JWT_KEY_FILE}
chmod 0400 ${SLURM_JWT_KEY_FILE}

SLURM_SCIP_INCLUDE_LINE=$(sed -n '/# SCIP/=' /opt/slurm/etc/slurm.conf)
test -n "${SLURM_SCIP_INCLUDE_LINE}" || {
  sed -i.bak '/^# WARNING!!! .* slurm_parallelcluster.conf .*/i # SCIP authentication\ninclude slurm_scip.conf\n#' /opt/slurm/etc/slurm.conf
}

systemctl restart slurmctld.service slurmrestd.service
systemctl enable slurmrestd.service


%changelog

* Wed Sep 15 2021 Anton Talevnin <anton.talevnin@quantori.com> - 1.0.0
- Initial version. Pack Slurm REST API binaries in a package
