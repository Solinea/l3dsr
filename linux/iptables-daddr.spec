Source1: iptables-daddr-spec.conf
%{expand:%([ ! -r %{SOURCE1} ] || cat '%{SOURCE1}')}
%{expand:%([ -r %{SOURCE1} ] || echo 'NoSource: 1')}

%if 0%{!?kmod_name:1}
%define kmod_name iptables-daddr
%endif
%if 0%{!?kmod_driver_version:1}
%define kmod_driver_version 0.6.2
%endif
%if 0%{!?kmod_rpm_release:1}
%define kmod_rpm_release uncontrolled
%endif
%if 0%{!?iptables_version_maj:1}
%define iptables_version_maj 1
%endif
%if 0%{!?iptables_version_min:1}
%define iptables_version_min 4
%endif

%if %{iptables_version_maj} == 1 && %{iptables_version_min} <= 3
Summary: Iptables destination address rewriting for IPv4
%else
Summary: Iptables destination address rewriting for IPv4 and IPv6
%endif
Name: %{kmod_name}
Version: %{kmod_driver_version}
Release: %{kmod_rpm_release}%{?dist}
License: GPLv2
Group: Applications/System
%if 0%{?url:1}
URL: %{url}
%endif
Vendor: Yahoo! Inc.
Packager: Quentin Barnes <qbarnes@yahoo-inc.com>

BuildRequires: /bin/sed

%if 0%{?rhel_version} == 406
Requires: module-init-tools >= 3.1-0.pre5.3.10
%endif

%if 0%{?rhel_version} == 600
# Only needed if building RHEL6 kvariants, skip for now.
#BuildRequires: redhat-rpm-config >= 9.0.3-40
%endif

%if %{iptables_version_maj} == 1 && %{iptables_version_min} == 2
BuildRequires: iptables-devel >= 1.2.11, iptables-devel < 1.3
Requires: iptables >= 1.2.11, iptables < 1.3
%endif
%if %{iptables_version_maj} == 1 && %{iptables_version_min} == 3
BuildRequires: iptables-devel >= 1.3.5-5.3, iptables-devel < 1.4
Requires: iptables >= 1.3.5, iptables < 1.4
%endif
%if %{iptables_version_maj} == 1 && %{iptables_version_min} == 4
BuildRequires: iptables-devel >= 1.4.7, iptables-devel < 1.5
Requires: iptables >= 1.4.7, iptables < 1.5
%endif

%if %{iptables_version_maj} == 1 && %{iptables_version_min} == 3
%package -n iptables-ipv6-daddr
Summary: Iptables destination address rewriting for IPv6
Group: Applications/System
Requires: iptables-ipv6 >= 1.3.5, iptables-ipv6 < 1.4
Requires: %{name}-kmod = %{version}
%endif

Requires: %{name}-kmod >= %{version}

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%define _prefix %{nil}
%define rpmversion %{version}-%{release}
%define fullpkgname %{name}-%{rpmversion}

Source0: %{name}-%{version}.tar.bz2
%if 0%{?kmodtool_local}
Source3: kmodtool
%endif

%if 0%{?kmodtool_local}
%define kmodtool sh %{SOURCE3}
%else
%define kmodtool sh /usr/lib/rpm/redhat/kmodtool
%endif

# Create a preinstall and preuninstall scripts as a macro for processing
# with sed that ensures any existing {ipt,xt}_DADDR module, if present, can
# be removed.  If not, fail.
%if %{iptables_version_maj} == 1 && %{iptables_version_min} == 2
%define pkgko ipt_DADDR
%else
%define pkgko xt_DADDR
%endif
%define kmodrm rmmod '%{pkgko}' 2> /dev/null || true;if %__grep -qw '^%{pkgko}' /proc/modules;then echo -e >\\&2 "WARNING: Unable to remove current %{pkgko} module!\\\\nRemove iptables rules using DADDR and try again.";exit 1;fi
%define prekmodrm if [ "$1" -eq 1 ];then %{kmodrm};fi
%define preunkmodrm if [ "$1" -eq 0 ];then %{kmodrm};fi

%if 0%{?rhel_version} >= 406 && 0%{?rhel_version} <= 505
  %define kverrel %(%{kmodtool} verrel %{?kmod_kernel_version} 2>/dev/null)
%else
  %if 0%{?kmod_kernel_version:1}
    %define kverrel %(%{kmodtool} verrel %{?kmod_kernel_version}.%{_target_cpu} 2>/dev/null)
  %else
    %define kverrel %(%{kmodtool} verrel 2>/dev/null)
  %endif
%endif

%define upvar ""

%ifarch ppc64
%define kdumpvar kdump
%endif

%if 0%{?rhel_version} == 406
  %ifarch i686
  %define paevar hugemem
  %define smpvar smp
  %endif
  %ifarch x86_64
  %define smpvar smp largesmp
  %endif
  %ifarch i686 ia64 x86_64
  %define xenvar xenU
  %endif
%endif
%if 0%{?rhel_version} == 505
  %ifarch i686
  %define paevar PAE
  %endif
  %ifarch i686 ia64 x86_64
  %define xenvar xen
  %endif
%endif

# hint: this can he overridden with "--define kvariants foo bar" on the
# rpmbuild command line, e.g. --define 'kvariants "" smp'
%if 0%{?rhel_version} != 406
%{!?kvariants: %define kvariants %{?upvar} %{?smpvar} %{?xenvar} %{?kdumpvar} %{?paevar}}
%else
# Split the output into two chunks on RHEL4 due to bug in its rpm utils
# not able to handle all the output from a single expand below.
%{!?kvariants1: %define kvariants1 %{?upvar} %{?smpvar}}
%{!?kvariants2: %define kvariants2 %{?xenvar} %{?kdumpvar} %{?paevar}}
%endif

# Use kmodtool to generate individual kmod subpackages directives.
%if 0%{?rhel_version} >= 406 && 0%{?rhel_version} <= 505
  %define kmodtemplate rpmtemplate_kmp
%else
  %define kmodtemplate rpmtemplate
  %define kmod_version %{version}
  %define kmod_release %{release}
%endif
%if 0%{?rhel_version} != 406
%{expand:%(%{kmodtool} %{kmodtemplate} %{kmod_name} %{kverrel} %{kvariants} 2>/dev/null | sed -e 's@^\(%%preun \)\(.*\)$@%%pre \2\n%{prekmodrm}\n\n\1\2\n%{preunkmodrm}\n@g')}
%else
%{expand:%(%{kmodtool} %{kmodtemplate} %{kmod_name} %{kverrel} %{kvariants1} 2>/dev/null | sed -e 's@^\(%%preun \)\(.*\)$@%%pre \2\n%{prekmodrm}\n\1\2\n%{preunkmodrm}@g')}
%{expand:%(%{kmodtool} %{kmodtemplate} %{kmod_name} %{kverrel} %{kvariants2} 2>/dev/null | sed -e 's@^\(%%preun \)\(.*\)$@%%pre \2\n%{prekmodrm}\n\1\2\n%{preunkmodrm}@g')}
%endif


%description
%if %{iptables_version_maj} == 1 && %{iptables_version_min} == 2
Enables IPv4 destination address rewriting using iptables rules.
%else
Enables IPv4 and IPv6 destination address rewriting using iptables rules.
%endif

The "%{name}" package provides an iptables user-space
plugin "DADDR" target.  The plugin requires installation of a
"kmod-%{name}" package providing a matching kernel module for
the running kernel.

For further information: %{url}

%if %{iptables_version_maj} == 1 && %{iptables_version_min} == 3
%description -n iptables-ipv6-daddr
Enables IPv6 destination address rewriting using iptables rules.

The "iptables-ipv6-daddr" package provides an iptables user-space
plugin "DADDR" target.  The plugin requires installation of a
"kmod-%{name}" package providing a matching kernel module
for the running kernel.

For further information: %{url}
%endif

%prep
%setup -q -c -T -a 0
for kvariant in %{kvariants} ; do
    cp -a %{kmod_name}-%{version} _kmod_build_$kvariant
done


%build
%__make -C "_kmod_build_/extensions" all
for kvariant in %{kvariants}
do
%if 0%{?rhel_version} >= 406 && 0%{?rhel_version} <= 505
    ksrc="%{_usrsrc}/kernels/%{kverrel}${kvariant:+-$kvariant}-%{_target_cpu}"
%else
    ksrc="%{_usrsrc}/kernels/%{kverrel}${kvariant:+.$kvariant}"
%endif
    %__make \
	-C "$ksrc" \
	M="$PWD/_kmod_build_${kvariant}/kmod" \
        MODVERSION='%{kmod_driver_version}'
done


%install
%__rm -rf -- '%{buildroot}'
%makeinstall -C "_kmod_build_/extensions"
for kvariant in %{kvariants}
do
%if 0%{?rhel_version} >= 406 && 0%{?rhel_version} <= 505
    ksrc="%{_usrsrc}/kernels/%{kverrel}${kvariant:+-$kvariant}-%{_target_cpu}"
%else
    ksrc="%{_usrsrc}/kernels/%{kverrel}${kvariant:+.$kvariant}"
%endif
    kodir="%{buildroot}/lib/modules/%{kverrel}${kvariant}/extra/%{kmod_name}"
    %__make \
	-C "$ksrc" \
	M="$PWD/_kmod_build_${kvariant}/kmod" \
        MODVERSION='%{kmod_driver_version}'
	# Need to make sure execute bits are set due to case #00603038.
	install -m 755 -D \
            "_kmod_build_${kvariant}/kmod/%{pkgko}.ko" \
            "$kodir/%{pkgko}.ko"
done


%clean
%__rm -rf -- '%{buildroot}'


%pre
%{expand:%(echo | sed -e 's@^@%{prekmodrm}@g')}


%preun
%{expand:%(echo | sed -e 's@^@%{preunkmodrm}@g')}


%files
%defattr(-, root, root)
%if %{iptables_version_maj} == 1 && %{iptables_version_min} <= 3
/lib*/iptables/libipt_DADDR.so
%else
/lib*/xtables/libxt_DADDR.so
%endif

%if %{iptables_version_maj} == 1 && %{iptables_version_min} == 3
%files -n iptables-ipv6-daddr
%defattr(-, root, root)
/lib*/iptables/libip6t_DADDR.so
%endif


%changelog
* Sun Aug 18 2013 Quentin Barnes <qbarnes@yahoo-inc.com> 0.6.2-20130818
- Update to new build process.
- Synchronize all released versions.

* Sat Jul 28 2012 Quentin Barnes <qbarnes@yahoo-inc.com> 0.6.0-20120728
- First release for Fedora 17.

* Thu Jul 12 2012 Quentin Barnes <qbarnes@yahoo-inc.com> 0.6.1-20120712
- Fix problem with DADDR updates being lost with some NICs.

* Thu Jul 05 2012 Quentin Barnes <qbarnes@yahoo-inc.com> 0.6.0-20120705
- Add IPv6 support.

* Wed Nov 23 2011 Quentin Barnes <qbarnes@yahoo-inc.com> 0.5.0-20111123
- Eliminate dependency on YlkmMgr, now using standard 'weak-modules' approach.
- Convert package over to building using standard 'kmodtool'.
- Split into separate binary packages for iptables plugin and each LKM.

* Sat Jan 15 2011 Quentin Barnes <qbarnes@yahoo-inc.com> 0.2.1-20110115
- Add xenU kernel support.  [BZ #4237848]
- Fix theoretical packaging dependency and some more "rpm -U ..." problems.

* Fri Oct 1 2010 Quentin Barnes <qbarnes@yahoo-inc.com> 0.2.0-20101001
- Fix problem when running "rpm -U ..." on package.

* Fri Aug 6 2010 Quentin Barnes <qbarnes@yahoo-inc.com> 0.2.0-20100806
- Update to use the new statically configuring ylkmmgr 0.2.0.

* Tue Nov 3 2009 Quentin Barnes <qbarnes@yahoo-inc.com> 0.1.1-20091103
- Update Makefiles to simplify build.
- Fix uninstall problems to remove kernel module if loaded.

* Mon Sep 11 2008 Quentin Barnes <qbarnes@yahoo-inc.com> 0.1-20080911
- Initial release
