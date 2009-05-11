#
%include	/usr/lib/rpm/macros.perl
Summary:	Heartbeat - subsystem for High-Availability Linux
Summary(es.UTF-8):	Subsistema heartbeat para Linux "High-Availability"
Summary(pl.UTF-8):	Podsystem heartbeat dla systemów o podwyższonej niezawodności
Summary(pt_BR.UTF-8):	Implementa sistema de monitoração (heartbeats) visando Alta Disponibilidade
Name:		heartbeat
Version:	2.99.2
Release:	0.1
License:	GPL v2+
Group:		Applications/System
Source0:	http://hg.linux-ha.org/dev/archive/beta-%{version}.tar.bz2
# Source0-md5:	ef79dc10100451bfcbb55b4707d28eb1
Source1:	%{name}.init
Source2:	ldirectord.init
Patch0:		%{name}-ac.patch
Patch1:		%{name}-no_ipmilan_test.patch
URL:		http://www.linux-ha.org/Heartbeat
BuildRequires:	OpenIPMI-devel >= 2.0.3
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	gdbm-devel
BuildRequires:	glib2-devel
BuildRequires:	gnutls-devel
BuildRequires:	libltdl-devel
BuildRequires:	libnet-devel >= 1.1.0
BuildRequires:	libnl-devel
BuildRequires:	libtool
BuildRequires:	libuuid-devel
BuildRequires:	libwrap-devel
BuildRequires:	libxml2-devel
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
Requires(post,postun):	/sbin/ldconfig
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires:	psmisc >= 22.5-2
Requires:	rc-scripts
Requires:	syslogdaemon
Requires:	which
Provides:	group(haclient)
Provides:	user(hacluster)
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

%package stonith
Summary:	Provides an interface to Shoot The Other Node In The Head
Summary(pl.UTF-8):	Interfejs do "odstrzelenia" drugiego węzła w klastrze
Group:		Applications/System
Requires:	OpenIPMI >= 2.0.3

%description stonith
Provides an interface to Shoot The Other Node In The Head.

%description stonith -l pl.UTF-8
STONITH (Shoot The Other Node In The Head) to interfejs służący do
"odstrzelenia" drugiego węzła w klastrze.

%package ldirectord
Summary:	Monitor virtual services provided by LVS
Summary(pl.UTF-8):	Demon monitorujący wirtualne usługi dostarczane poprzez LVS
Group:		Applications/System
Requires(post,preun):	/sbin/chkconfig
Requires:	ipvsadm
Requires:	rc-scripts

%description ldirectord
ldirectord is a stand-alone daemon to monitor services of real for
virtual services provided by The Linux Virtual Server
(http://www.linuxvirtualserver.org/).

%description ldirectord -l pl.UTF-8
ldirectord to samodzielny demon monitorujący rzeczywiste usługi dla
wirtualnych usług dostarczanych poprzez Linux Virtual Server
(http://www.linuxvirtualserver.org/).

%package devel
Summary:	Heartbeat developement header files and libraries
Summary(pl.UTF-8):	Pliki nagłówkowe i biblioteki heartbeat
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

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
%setup -qn Linux-HA-Dev-beta-%{version}
%patch0 -p1
%patch1 -p1

rm -rf libltdl

%build
%{__libtoolize} --ltdl
%{__aclocal}
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
	FSCK=/sbin/fsck \
	FUSER=/bin/fuser \
	IPTABLES=/usr/sbin/iptables \
	MAILCMD=/bin/mail \
	MOUNT=/bin/mount \
	PING=/bin/ping \
	--with-initdir=/etc/rc.d/init.d \
	--enable-fatal-warnings=no \
	--enable-mgmt \
	--enable-quorumd \
	--enable-snmp-subagent

%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/var/run/heartbeat

rm -f $RPM_BUILD_ROOT%{_sysconfdir}/ha.d/resource.d/ldirectord
ln -sf %{_sbindir}/ldirectord $RPM_BUILD_ROOT%{_sysconfdir}/ha.d/resource.d/ldirectord

# plugins are lt_dlopened, but using *.so names, so *.la are not used
rm -f $RPM_BUILD_ROOT%{_libdir}/{heartbeat,pils,stonith}/plugins/*/*.{la,a}

rm -f $RPM_BUILD_ROOT/etc/rc.d/init.d/heartbeat
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/heartbeat

> $RPM_BUILD_ROOT/etc/ha.d/haresources
echo -e "auth 2\n2 crc" > $RPM_BUILD_ROOT/etc/ha.d/authkeys
install doc/ha.cf $RPM_BUILD_ROOT/etc/ha.d

rm -f $RPM_BUILD_ROOT/etc/rc.d/init.d/ldirectord
install %{SOURCE2} $RPM_BUILD_ROOT/etc/rc.d/init.d/ldirectord
install ldirectord/ldirectord.cf $RPM_BUILD_ROOT%{_sysconfdir}/ha.d

rm -f $RPM_BUILD_ROOT%{_datadir}/heartbeat/cts/README

for tool in ha_logger hb_addnode hb_delnode hb_standby hb_takeover; do
	ln -sf %{_libdir}/heartbeat/$tool $RPM_BUILD_ROOT%{_bindir}
done

sed -i -e's, /%{_lib}/libpam.la, /usr/%{_lib}/libpam.la,g' $RPM_BUILD_ROOT%{_libdir}/*.la

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 60 haclient
%useradd -u 17 -d /var/lib/heartbeat/cores/hacluster -c "Heartbeat User" -g haclient hacluster

%post
/sbin/ldconfig
/sbin/chkconfig --add heartbeat
%service %{name} restart

%preun
if [ "$1" = "0" ]; then
	%service -q %{name} stop
	/sbin/chkconfig --del heartbeat
fi

%postun
/sbin/ldconfig
if [ "$1" = "0" ]; then
	%userremove hacluster
	%groupremove haclient
fi

%post	stonith -p /sbin/ldconfig
%postun	stonith -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc doc/{*.html,AUTHORS,apphbd.cf,authkeys,ha.cf,logd.cf,haresources,startstop}
%attr(755,root,root) %{_libdir}/libapphb.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libapphb.so.2
%attr(755,root,root) %{_libdir}/libccmclient.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libccmclient.so.1
%attr(755,root,root) %{_libdir}/libclm.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libclm.so.1
%attr(755,root,root) %{_libdir}/libhbclient.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libhbclient.so.1
%attr(755,root,root) %{_libdir}/liblrm.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/liblrm.so.2
%attr(755,root,root) %{_libdir}/libpils.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libpils.so.2
%attr(755,root,root) %{_libdir}/libplumb.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libplumb.so.2
%attr(755,root,root) %{_libdir}/libplumbgpl.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libplumbgpl.so.2
%attr(755,root,root) %{_libdir}/libstonith.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libstonith.so.1
%dir %{_libdir}/heartbeat
%dir %{_libdir}/heartbeat/plugins
%dir %{_libdir}/heartbeat/plugins/*
%attr(755,root,root) %{_libdir}/heartbeat/plugins/*/*.so
%attr(755,root,root) %{_libdir}/heartbeat/[!cp]*
%attr(755,root,root) %{_libdir}/heartbeat/c[!t]*
%dir %{_libdir}/pils
%dir %{_libdir}/pils/plugins
%dir %{_libdir}/pils/plugins/*
%dir %{_datadir}/heartbeat
%attr(755,root,root) %{_datadir}/heartbeat/BasicSanityCheck
%attr(755,root,root) %{_datadir}/heartbeat/ResourceManager
%attr(755,root,root) %{_datadir}/heartbeat/TestHeartbeatComm
%attr(755,root,root) %{_datadir}/heartbeat/ha_*
%attr(755,root,root) %{_datadir}/heartbeat/hb_*
%attr(755,root,root) %{_datadir}/heartbeat/lrmtest
%attr(755,root,root) %{_datadir}/heartbeat/mach_down
%attr(755,root,root) %{_datadir}/heartbeat/req_resource
%attr(755,root,root) %{_datadir}/heartbeat/utillib.sh
%{_datadir}/heartbeat/ra-api-1.dtd
%attr(755,root,root) %{_libdir}/pils/plugins/*/*.so
%dir %{_sysconfdir}/ha.d
%attr(755,root,root) %{_sysconfdir}/ha.d/rc.d
%attr(755,root,root) %{_sysconfdir}/ha.d/resource.d
%exclude %{_sysconfdir}/ha.d/resource.d/ldirectord
%{_sysconfdir}/ha.d/README.config
%attr(755,root,root) %{_sysconfdir}/ha.d/harc
%{_sysconfdir}/ha.d/shellfuncs
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/heartbeat
%attr(754,root,root) /etc/rc.d/init.d/heartbeat
%attr(755,root,root) %{_prefix}/lib/ocf
%dir /var/run/heartbeat
%attr(750,hacluster,haclient) %dir /var/run/heartbeat/ccm
%dir /var/lib/heartbeat
%attr(770,root,haclient) %dir /var/lib/heartbeat/lrm
%attr(711,root,root) %dir /var/lib/heartbeat/cores
%attr(700,root,root) %dir /var/lib/heartbeat/cores/root
# we don't want any files owned by nobody
%attr(700,root,root) %dir /var/lib/heartbeat/cores/nobody
%attr(700,hacluster,root) %dir /var/lib/heartbeat/cores/hacluster
%{_mandir}/man1/*.1*
%{_mandir}/man8/[a-h]*.8*
%attr(755,root,root) %{_bindir}/cl_respawn
%attr(2755,root,haclient) %{_bindir}/cl_status
%attr(755,root,root) %{_bindir}/ha_logger
%attr(755,root,root) %{_bindir}/hb_addnode
%attr(755,root,root) %{_bindir}/hb_delnode
%attr(755,root,root) %{_bindir}/hb_standby
%attr(755,root,root) %{_bindir}/hb_takeover
%attr(755,root,root) %{_sbindir}/[a-i]*
%attr(755,root,root) %{_sbindir}/ocf-tester
%attr(755,root,root) %{_sbindir}/sbd
%attr(755,root,root) %{_sbindir}/sfex_init
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/ha.d/haresources
%attr(600,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/ha.d/authkeys
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/ha.d/ha.cf

%files stonith
%defattr(644,root,root,755)
%dir %{_libdir}/stonith
%dir %{_libdir}/stonith/plugins
%dir %{_libdir}/stonith/plugins/external
%dir %{_libdir}/stonith/plugins/stonith2
%attr(755,root,root) %{_libdir}/stonith/plugins/*/*
%attr(755,root,root) %{_libdir}/stonith/plugins/xen0-ha-dom0-stonith-helper
%attr(755,root,root) %{_sbindir}/meatclient
%attr(755,root,root) %{_sbindir}/stonith
%{_mandir}/man8/stonith.8*
%{_mandir}/man8/meatclient.8*

%files ldirectord
%defattr(644,root,root,755)
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/ha.d/ldirectord.cf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/ldirectord
%attr(755,root,root) %{_sysconfdir}/ha.d/resource.d/ldirectord
%attr(754,root,root) /etc/rc.d/init.d/ldirectord
%attr(755,root,root) %{_sbindir}/*ldirectord*
%{_mandir}/man8/*ldirectord*.8*

%files devel
%defattr(644,root,root,755)
%{_includedir}/*
%attr(755,root,root) %{_libdir}/lib*.so
%{_libdir}/*.la

%files static
%defattr(644,root,root,755)
%{_libdir}/*.a

%files cts
%defattr(644,root,root,755)
%doc cts/README
%{_libdir}/heartbeat/cts
%dir %{_datadir}/heartbeat/cts
%attr(755,root,root) %{_datadir}/heartbeat/cts/*.py
%{_datadir}/heartbeat/cts/*.py[co]
%attr(755,root,root) %{_datadir}/heartbeat/cts/*.sh
%attr(755,root,root) %{_datadir}/heartbeat/cts/*Dummy
