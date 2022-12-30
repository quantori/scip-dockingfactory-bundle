%define product   scip
%define service   python

%global pybasever 3.7

%if "%{?dist}" == ".el7"
%global centos7 1
%endif

Name:             %{product}-%{service}
Summary:          Interpreter of the Python programming language
Version:          %{pybasever}.10
Release:          0
License:          Python
Group:            HPC/Scientific Platform
Vendor:           Quantori
URL:              https://www.python.org/
Packager:         Quantori SCIP team, <anton.talevnin@quantori.com>
%if 0%{?centos7}
BuildRequires:    centos-release-scl devtoolset-8-gcc
%else
BuildRequires:    gcc >= 7
%endif
BuildRequires:    bzip2
BuildRequires:    bzip2-devel
BuildRequires:    expat-devel
BuildRequires:    libffi-devel
BuildRequires:    openssl-devel
BuildRequires:    readline-devel
BuildRequires:    sqlite-devel
BuildRequires:    xz-devel
BuildRequires:    zlib-devel

Provides: %{_bindir}/python%{pybasever}

Source: https://www.python.org/ftp/python/%{version}/Python-%{version}%{?prerel}.tar.xz

# Turn off the brp-python-bytecompile script
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')

%description
Python is an accessible, high-level, dynamically typed, interpreted programming
language, designed with an emphasis on code readability.
It includes an extensive standard library, and has a vast ecosystem of
third-party libraries.


%prep
%setup -q -n Python-%{version}%{?prerel}
find -name '*.exe' -print -delete ;\


%build
%if 0%{?centos7}
source /opt/rh/devtoolset-8/enable
%endif
# Regenerate the configure script and pyconfig.h.in
#autoconf
#autoheader

%configure \
  --enable-ipv6 \
  --enable-optimizations \
  --with-ssl-default-suites=openssl
make PROFILE_TASK="-m test.regrtest --pgo -j8" -j 8


%install
make \
  DESTDIR=%{buildroot} \
  INSTALL="install -p" \
  install

# Switch all shebangs to refer to the specific Python version.
LD_LIBRARY_PATH=./ ./python \
  Tools/scripts/pathfix.py \
  -i "%{_bindir}/python%{pybasever}" -pn \
  %{buildroot}

# Remove shebang lines from .py files that aren't executable, and
# remove executability from .py files that don't have a shebang line:
find %{buildroot} -name \*.py \
  \( \( \! -perm /u+x,g+x,o+x -exec sed -e '/^#!/Q 0' -e 'Q 1' {} \; \
  -print -exec sed -i '1d' {} \; \) -o \( \
  -perm /u+x,g+x,o+x ! -exec grep -m 1 -q '^#!' {} \; \
  -exec chmod a-x {} \; \) \)

# Get rid of DOS batch files:
find %{buildroot} -name \*.bat -exec rm {} \;

# Get rid of backup files:
find %{buildroot}/ -name "*~" -exec rm -f {} \;
find . -name "*~" -exec rm -f {} \;

%files
%defattr(-,root,root,-)
%{_prefix}

%preun
alternatives --remove python-scip %{_bindir}/python%{pybasever}

%post
alternatives --install /usr/bin/python-scip python-scip %{_bindir}/python%{pybasever} 100

#%changelog
