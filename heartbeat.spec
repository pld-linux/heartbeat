# TODO
# - merge mibs supackage from 2.1 branch
# - cleanup deps, users for 3.x
# - fixup deps, inner deps, think of subpackages, ugprade path from 2.1
#
%include	/usr/lib/rpm/macros.perl
Summary:	Heartbeat - subsystem for High-Availability Linux
Summary(es.UTF-8):	Subsistema heartbeat para Linux "High-Availability"
Summary(pl.UTF-8):	Podsystem heartbeat dla systemów o podwyższonej niezawodności
Summary(pt_BR.UTF-8):	Implementa sistema de monitoração (heartbeats) visando Alta Disponibilidade
Name:		heartbeat
Version:	3.0.5
Release:	6
License:	GPL v2+
Group:		Networking/Daemons
Source0:	http://hg.linux-ha.org/heartbeat-STABLE_3_0/archive/STABLE-%{version}.tar.bz2
# Source0-md5:	f8686abde8722c42265c6d84fbe3d3bf
Source1:	%{name}.init
Source2:	%{name}.tmpfiles
Patch0:		%{name}-type_mismatch.patch
Patch1:		%{name}-ac.patch
Patch2:		%{name}-libs.patch
Patch3:		%{name}-tls.patch
URL:		http://www.linux-ha.org/Heartbeat
BuildRequires:	OpenIPMI-devel >= 2.0.3
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	cluster-glue-libs-devel
BuildRequires:	docbook-dtd44-xml
BuildRequires:	docbook-style-xsl
BuildRequires:	gdbm-devel
BuildRequires:	glib2-devel
BuildRequires:	glibc-misc
BuildRequires:	gnutls-devel
BuildRequires:	libltdl-devel
BuildRequires:	libnet-devel >= 1.1.0
BuildRequires:	libnl-devel
BuildRequires:	libtool
BuildRequires:	libuuid-devel
BuildRequires:	libwrap-devel
BuildRequires:	libxml2-devel
BuildRequires:	libxslt-progs
BuildRequires:	lm_sensors-devel
BuildRequires:	ncurses-devel >= 5.4
BuildRequires:	net-snmp-devel >= 5.1
BuildRequires:	pam-devel
BuildRequires:	pkgconfig
BuildRequires:	python-devel
BuildRequires:	rpm-perlprov
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.268
BuildRequires:	swig-perl >= 1.3.25
BuildRequires:	swig-python >= 1.3.25
Requires:	%{name}-libs = %{version}-%{release}
Requires:	cluster-glue
Requires:	psmisc >= 22.5-2
Requires:	rc-scripts
Requires:	resource-agents >= 3.9.2-2
Requires:	syslogdaemon
Requires:	which
# disappeared
Obsoletes:	perl-heartbeat
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		specflags		-fgnu89-inline
%define		filterout_ld	-Wl,--as-needed

%description
heartbeat is a basic heartbeat subsystem for Linux-HA. It will run
scripts at initialization, and when machines go up or down. This
version will also perform IP address takeover using gratuitous ARPs.
It works correctly for a 2-node configuration, and is extensible to
larger configurations.

It implements the following kinds of heartbeats:
 - Bidirectional Serial Rings ("raw" serial ports)

%description -l es.UTF-8
heartbeat es un sistema básico para Linux-HA. La función de este
software es ejecutar scripts en la inicialización y al apagar las
máquinas que lo utilizan.

%description -l pl.UTF-8
heartbeat jest podstawowym podsystemem dla systemów o podwyższonej
dostępności budowanych w oparciu o Linuksa. Zajmuje się uruchamianiem
skryptów podczas startu i zamykania systemu. Ta wersja pakietu pozwala
na przejmowanie adresów IP. Oprogramowanie działa poprawnie dla
konfiguracji składającej się z 2 hostów, można je również stosować do
bardziej skomplikowanych konfiguracji.

%package libs
Summary:	Heartbeat libraries
Summary(pl.UTF-8):	Biblioteki heartbeat
Group:		Libraries
Conflicts:	heartbeat < 2.99.2-0.1

%description libs
Heartbeat libraries.

%description libs -l pl.UTF-8
Biblioteki heartbeat.

%package devel
Summary:	Heartbeat developement header files and libraries
Summary(pl.UTF-8):	Pliki nagłówkowe i biblioteki heartbeat
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}

%description devel
Heartbeat developement header files and libraries.

%description devel -l pl.UTF-8
Pliki nagłówkowe i biblioteki heartbeat.

%package static
Summary:	Heartbeat static libraries
Summary(pl.UTF-8):	Biblioteki statyczne heartbeat
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Heartbeat static libraries.

%description static -l pl.UTF-8
Biblioteki statyczne heartbeat.

%package cts
Summary:	Cluster Test Suite
Summary(pl.UTF-8):	Zestaw testów klastra
Group:		Applications/System
Requires:	%{name} = %{version}-%{release}

%description cts
Cluster Test Suite for heartbeat.

%description cts -l pl.UTF-8
Zestaw testów klastra opartego o heartbeat.

%prep
%setup -qn Heartbeat-3-0-STABLE-%{version}
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
rm -rf libltdl

%build
%{__libtoolize} --ltdl
%{__aclocal}
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
	--with-initdir=/etc/rc.d/init.d \
	--docdir=%{_docdir}/%{name}-%{version} \
	--enable-fatal-warnings=no \
	--enable-mgmt \
	--enable-quorumd \
	--enable-snmp-subagent

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
%{__make} -j1 install \
	DESTDIR=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT{/var/run/heartbeat,/usr/lib/tmpfiles.d}

# plugins are lt_dlopened, but using *.so names, so *.la are not used
rm -f $RPM_BUILD_ROOT%{_libdir}/heartbeat/plugins/*/*.{la,a}

rm -f $RPM_BUILD_ROOT/etc/rc.d/init.d/heartbeat
install -p %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/heartbeat

> $RPM_BUILD_ROOT/etc/ha.d/haresources
echo -e "auth 2\n2 crc" > $RPM_BUILD_ROOT/etc/ha.d/authkeys
cp -a doc/ha.cf $RPM_BUILD_ROOT/etc/ha.d

for tool in hb_addnode hb_delnode hb_standby hb_takeover; do
	tool=%{_datadir}/%{name}/$tool
	[ -x $RPM_BUILD_ROOT$tool ] || exit 1
	ln -s $tool $RPM_BUILD_ROOT%{_bindir}
done

rm $RPM_BUILD_ROOT%{_datadir}/heartbeat/cts/README

sed -i -e's, /%{_lib}/libpam.la, /usr/%{_lib}/libpam.la,g' $RPM_BUILD_ROOT%{_libdir}/*.la

install %{SOURCE2} $RPM_BUILD_ROOT/usr/lib/tmpfiles.d/%{name}.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add heartbeat
%service heartbeat restart

%preun
if [ "$1" = "0" ]; then
	%service -q heartbeat stop
	/sbin/chkconfig --del heartbeat
fi

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc doc/{*.html,AUTHORS,apphbd.cf,authkeys,ha.cf,haresources,startstop}
%dir %{_libdir}/heartbeat
%dir %{_libdir}/heartbeat/plugins
%dir %{_libdir}/heartbeat/plugins/*
%attr(755,root,root) %{_libdir}/heartbeat/plugins/*/*.so
%attr(755,root,root) %{_libdir}/heartbeat/[!cp]*
%attr(755,root,root) %{_libdir}/heartbeat/c[!t]*
%dir %{_datadir}/heartbeat
%attr(755,root,root) %{_datadir}/heartbeat/BasicSanityCheck
%attr(755,root,root) %{_datadir}/heartbeat/ResourceManager
%attr(755,root,root) %{_datadir}/heartbeat/TestHeartbeatComm
%attr(755,root,root) %{_datadir}/heartbeat/ha_*
%attr(755,root,root) %{_datadir}/heartbeat/hb_*
%attr(755,root,root) %{_datadir}/heartbeat/mach_down
%attr(755,root,root) %{_datadir}/heartbeat/req_resource
%attr(755,root,root) %{_sysconfdir}/ha.d/rc.d
%{_sysconfdir}/ha.d/README.config
%attr(755,root,root) %{_sysconfdir}/ha.d/harc
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/heartbeat
%attr(754,root,root) /etc/rc.d/init.d/heartbeat
%dir /var/run/heartbeat
%attr(750,hacluster,haclient) %dir /var/run/heartbeat/ccm
%dir /var/lib/heartbeat
%{_mandir}/man1/*.1*
%{_mandir}/man8/[a-h]*.8*
%{_mandir}/man5/authkeys.5*
%{_mandir}/man5/ha.cf.5*
%attr(755,root,root) %{_bindir}/cl_respawn
%attr(2755,root,haclient) %{_bindir}/cl_status
%attr(755,root,root) %{_bindir}/hb_addnode
%attr(755,root,root) %{_bindir}/hb_delnode
%attr(755,root,root) %{_bindir}/hb_standby
%attr(755,root,root) %{_bindir}/hb_takeover
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/ha.d/haresources
%attr(600,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/ha.d/authkeys
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/ha.d/ha.cf
/usr/lib/tmpfiles.d/%{name}.conf

%files libs
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libapphb.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libapphb.so.2
%attr(755,root,root) %{_libdir}/libccmclient.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libccmclient.so.1
%attr(755,root,root) %{_libdir}/libclm.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libclm.so.1
%attr(755,root,root) %{_libdir}/libhbclient.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libhbclient.so.1

%files devel
%defattr(644,root,root,755)
%{_includedir}/heartbeat
%{_includedir}/ocf
%{_includedir}/saf
%attr(755,root,root) %{_libdir}/libapphb.so
%attr(755,root,root) %{_libdir}/libccmclient.so
%attr(755,root,root) %{_libdir}/libclm.so
%attr(755,root,root) %{_libdir}/libhbclient.so
%{_libdir}/libapphb.la
%{_libdir}/libccmclient.la
%{_libdir}/libclm.la
%{_libdir}/libhbclient.la

%files static
%defattr(644,root,root,755)
%{_libdir}/libapphb.a
%{_libdir}/libccmclient.a
%{_libdir}/libclm.a
%{_libdir}/libhbclient.a

%files cts
%defattr(644,root,root,755)
%doc cts/README
%dir %{_datadir}/heartbeat/cts
%attr(755,root,root) %{_datadir}/heartbeat/cts/*.py
%{_datadir}/heartbeat/cts/*.py[co]
%attr(755,root,root) %{_datadir}/heartbeat/cts/*.sh
%attr(755,root,root) %{_datadir}/heartbeat/cts/*Dummy
