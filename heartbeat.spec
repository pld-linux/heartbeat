%include	/usr/lib/rpm/macros.perl
Summary:	Heartbeat - subsystem for High-Availability Linux
Summary(es):	Subsistema heartbeat para Linux "High-Availability"
Summary(pl):	Podsystem heartbeat dla system�w o podwy�szonej niezawodno�ci
Summary(pt_BR):	Implementa sistema de monitora��o (heartbeats) visando Alta Disponibilidade
Name:		heartbeat
Version:	1.99.5
Release:	0.3
License:	GPL v2+
Group:		Applications/System
Source0:	http://linux-ha.org/download/%{name}-%{version}.tar.gz
# Source0-md5:	808dd7884954553515757af6ad6dedb2
Source1:	%{name}.init
Source2:	ldirectord.init
URL:		http://linux-ha.org/
BuildRequires:	OpenIPMI-devel >= 1.4
BuildRequires:	OpenIPMI-devel < 2.0.0
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	gdbm-devel
BuildRequires:	glib2-devel
BuildRequires:	libnet-devel >= 1.1.0
BuildRequires:	libltdl-devel
BuildRequires:	libtool
BuildRequires:	libuuid-devel
BuildRequires:	libwrap-devel
BuildRequires:	libxml2-devel
BuildRequires:	net-snmp-devel
BuildRequires:	pkgconfig
BuildRequires:	rpm-devel
BuildRequires:	rpm-perlprov
BuildRequires:	rpmbuild(macros) >= 1.202
BuildRequires:	swig
PreReq:		rc-scripts
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(post,preun):	/sbin/chkconfig
Requires(post,postun):	/sbin/ldconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires:	syslogdaemon
Provides:	group(haclient)
Provides:	user(hacluster)
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
heartbeat is a basic heartbeat subsystem for Linux-HA. It will run
scripts at initialization, and when machines go up or down. This
version will also perform IP address takeover using gratuitous ARPs.
It works correctly for a 2-node configuration, and is extensible to
larger configurations.

It implements the following kinds of heartbeats:
 - Bidirectional Serial Rings ("raw" serial ports)

%description -l es
heartbeat es un sistema b�sico para Linux-HA. La funci�n de este
software es ejecutar scripts en la inicializaci�n y al apagar las
m�quinas que lo utilizan.

%description -l pl
heartbeat jest podstawowym podsystemem dla system�w o podwy�szonej
dost�pno�ci budowanych w oparciu o Linuksa. Zajmuje si� uruchamianiem
skrypt�w podczas startu i zamykania systemu. Ta wersja pakietu pozwala
na przejmowanie adres�w IP. Oprogramowanie dzia�a poprawnie dla
konfiguracji sk�adaj�cej si� z 2 host�w, mo�na je r�wnie� stosowa� do
bardziej skomplikowanych konfiguracji.

%package stonith
Summary:	Provides an interface to Shoot The Other Node In The Head
Summary(pl):	Interfejs do "odstrzelenia" drugiego w�z�a w klastrze
Group:		Applications/System

%description stonith
Provides an interface to Shoot The Other Node In The Head.

%description stonith -l pl
STONITH (Shoot The Other Node In The Head) to interfejs s�u��cy do
"odstrzelenia" drugiego w�z�a w klastrze.

%package ldirectord
Summary:	Monitor virtual services provided by LVS
Summary(pl):	Demon monitoruj�cy wirtualne serwisy dostaczanych przez LVS
Group:		Applications/System
PreReq:         rc-scripts
Requires(post,preun):   /sbin/chkconfig
Requires:	ipvsadm

%description ldirectord
ldirectord is a stand-alone daemon to monitor services of real
for virtual services provided by The Linux Virtual Server
(http://www.linuxvirtualserver.org/).

%package devel
Summary:	Heartbeat developement header files and libraries
Summary(pl):	Pliki nag��wkowe i biblioteki heartbeat
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
Heartbeat developement header files and libraries.

%description devel -l pl
Pliki nag��wkowe i biblioteki heartbeat.

%package static
Summary:	Heartbeat static libraries
Summary(pl):	Biblioteki statyczne heartbeat
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Heartbeat static libraries.

%description -l static
Biblioteki statyczne heartbeat.

%prep
%setup -q

rm -rf libltdl

%build
%{__libtoolize} --ltdl
%{__aclocal}
%{__autoconf}
%{__automake}
%configure \
	PING=/bin/ping \
	MOUNT=/bin/mount \
	FSCK=/sbin/fsck \
	--with-initdir=/etc/rc.d/init.d \
	--enable-lrm \
	--enable-crm \
	--enable-perl-vendor

%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

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

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 60 haclient
%useradd -u 17 -d /var/lib/heartbeat/cores/hacluster -c "Heartbeat User" -g haclient hacluster

%post
/sbin/ldconfig
/sbin/chkconfig --add heartbeat

%preun
Uninstall_PPP_hack() {
	file2hack=/etc/ppp/ip-up.local
	echo "NOTE: Restoring /$file2hack"
	MARKER="Heartbeat"
	ed -s $file2hack <<-!EOF  2>/dev/null
H
g/ $MARKER\$/d
w
!EOF
}

if [ "$1" = "0" ]; then
	/sbin/chkconfig --del heartbeat
	if [ ! -x /etc/ppp/ip-up.heart ]; then
		Uninstall_PPP_hack
	fi
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
%doc doc/{*.html,AUTHORS,apphbd.cf,authkeys,ha.cf,haresources,startstop}
%attr(755,root,root) %{_libdir}/lib*.so.*.*.*
%dir %{_libdir}/heartbeat
%dir %{_libdir}/heartbeat/cts
%attr(755,root,root) %{_libdir}/heartbeat/cts/*.py
%dir %{_libdir}/heartbeat/plugins
%dir %{_libdir}/heartbeat/plugins/*
%attr(755,root,root) %{_libdir}/heartbeat/plugins/*/*.so
%attr(755,root,root) %{_libdir}/heartbeat/*
%dir %{_libdir}/pils
%dir %{_libdir}/pils/plugins
%dir %{_libdir}/pils/plugins/*
%attr(755,root,root) %{_libdir}/pils/plugins/*/*.so
%dir %{_sysconfdir}/ha.d
%attr(755,root,root) %{_sysconfdir}/ha.d/rc.d
%attr(755,root,root) %{_sysconfdir}/ha.d/resource.d
%{_sysconfdir}/ha.d/README.config
%attr(755,root,root) %{_sysconfdir}/ha.d/harc
%{_sysconfdir}/ha.d/shellfuncs
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/heartbeat
%attr(754,root,root) /etc/rc.d/init.d/heartbeat
%attr(755,root,root) %{_libdir}/ocf
%dir /var/lib/heartbeat
#%%attr(750,root,haclient) %dir /var/lib/heartbeat/api
#%%attr(1770,root,haclient) %dir /var/lib/heartbeat/casual
#%%attr(755,hacluster,haclient) %dir /var/lib/heartbeat/ccm
%attr(755,root,haclient) %dir /var/lib/heartbeat/ccm
#%%attr(755,root,haclient) %dir /var/lib/heartbeat/ckpt
#%%attr(600,root,root) /var/lib/heartbeat/fifo
%{_mandir}/man1/*.1*
%{_mandir}/man8/[a-h]*.8*
/var/lib/heartbeat/cores
%attr(755,root,root) %{_bindir}/cl*
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/ha.d/haresources
%attr(600,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/ha.d/authkeys
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/ha.d/ha.cf
%{_datadir}/snmp/mibs/*mib

%files stonith
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libstonith.so.*.*.*
%dir %{_libdir}/stonith
%dir %{_libdir}/stonith/plugins
%dir %{_libdir}/stonith/plugins/external
%dir %{_libdir}/stonith/plugins/stonith2
%attr(755,root,root) %{_libdir}/stonith/plugins/*/*
%attr(755,root,root) %{_sbindir}/meatclient
%attr(755,root,root) %{_sbindir}/stonith
%{_mandir}/man8/stonith.8.gz
%{_mandir}/man8/meatclient.8.gz

%files ldirectord
%defattr(644,root,root,755)
%dir %{_sysconfdir}/ha.d/conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/ha.d/ldirectord.cf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/ldirectord
%attr(754,root,root) /etc/rc.d/init.d/ldirectord
%attr(755,root,root) %{_sbindir}/*ldirectord*
%{_mandir}/man8/*ldirectord*.8*

%files devel
%defattr(644,root,root,755)
%{_includedir}/*
%{_libdir}/*.la
%{perl_vendorarch}/heartbeat
%dir %{perl_vendorarch}/auto/heartbeat
%dir %{perl_vendorarch}/auto/heartbeat/cl_raw
%{perl_vendorarch}/auto/heartbeat/cl_raw/cl_raw.bs
%attr(755,root,root) %{perl_vendorarch}/auto/heartbeat/cl_raw/cl_raw.so
%{_mandir}/man3/*

%files static
%defattr(644,root,root,755)
%{_libdir}/*.a
