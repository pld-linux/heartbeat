%include	/usr/lib/rpm/macros.perl
Summary:	Heartbeat - subsystem for High-Availability Linux
Summary(es):	Subsistema heartbeat para Linux "High-Availability"
Summary(pl):	Podsystem heartbeat dla systemów o podwy¿szonej niezawodno¶ci
Summary(pt_BR):	Implementa sistema de monitoração (heartbeats) visando Alta Disponibilidade
Name:		heartbeat
Version:	1.2.0
Release:	0.1
License:	GPL v2+
Group:		Applications/System
Source0:	http://linux-ha.org/download/%{name}-%{version}.tar.gz
# Source0-md5:	b31e3f91c76fe006d2af94a868445293
Patch0:		%{name}-ac.patch
URL:		http://linux-ha.org/
BuildRequires:	OpenIPMI-devel
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	curl-devel
BuildRequires:	glib-devel
BuildRequires:	libnet-devel >= 1.1.0
BuildRequires:	libltdl-devel
BuildRequires:	libtool
BuildRequires:	libxml2-devel
BuildRequires:	net-snmp-devel
BuildRequires:	perl-libwww
BuildRequires:	rpm-perlprov
PreReq:		rc-scripts
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(post,preun):	/sbin/chkconfig
Requires(post,postun):	/sbin/ldconfig
Requires(postun):	/usr/sbin/groupdel
Requires:	syslogdaemon
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
heartbeat es un sistema básico para Linux-HA. La función de este
software es ejecutar scripts en la inicialización y al apagar las
máquinas que lo utilizan.

%description -l pl
heartbeat jest podstawowym podsystemem dla systemów o podwy¿szonej
dostêpno¶ci budowanych w oparciu o Linuksa. Zajmuje siê uruchamianiem
skryptów podczas startu i zamykania systemu. Ta wersja pakietu pozwala
na przejmowanie adresów IP. Oprogramowanie dzia³a poprawnie dla
konfiguracji sk³adaj±cej siê z 2 hostów, mo¿na je równie¿ stosowaæ do
bardziej skomplikowanych konfiguracji.

#%package stonith
#Summary: Provides an interface to Shoot The Other Node In The Head
#Group: Utilities

%prep
%setup -q
%patch0 -p1

rm -rf libltdl

%build
%{__libtoolize} --ltdl
%{__aclocal}
%{__autoconf}
%{__automake}
%configure \
	PING=/bin/ping \
	--with-initdir=/etc/rc.d/init.d

%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

rm -f $RPM_BUILD_ROOT%{_sysconfdir}/ha.d/resource.d/ldirectord
ln -sf %{_sbindir}/ldirectord $RPM_BUILD_ROOT%{_sysconfdir}/ha.d/resource.d/ldirectord

# plugins are lt_dlopened, but using *.so names, so *.la are not used
rm -f $RPM_BUILD_ROOT%{_libdir}/{heartbeat,pils,stonith}/plugins/*/*.{la,a}

%clean
rm -rf $RPM_BUILD_ROOT

%pre
if [ -n "`/usr/bin/getgid haclient`" ]; then
	if [ "`/usr/bin/getgid haclient`" != "60" ]; then
		echo "Error: group haclient doesn't have gid=60. Correct this before installing heartbeat." 1>&2
		exit 1
	fi
else
	/usr/sbin/groupadd -g 60 -r haclient
fi

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
	/usr/sbin/groupdel haclient 2>/dev/null
fi

%files
%defattr(644,root,root,755)
%doc doc/{*.html,AUTHORS,apphbd.cf,authkeys,ha.cf,haresources,startstop}
%attr(755,root,root) %{_sbindir}/*
%attr(755,root,root) %{_libdir}/lib*.so.*.*.*
%dir %{_libdir}/heartbeat
%dir %{_libdir}/heartbeat/cts
%attr(755,root,root) %{_libdir}/heartbeat/cts/*.py
%dir %{_libdir}/heartbeat/plugins
%dir %{_libdir}/heartbeat/plugins/*
%attr(755,root,root) %{_libdir}/heartbeat/plugins/*/*.so
%attr(755,root,root) %{_libdir}/heartbeat/[!cp]*
%attr(755,root,root) %{_libdir}/heartbeat/c[!t]*
%dir %{_libdir}/pils
%dir %{_libdir}/pils/plugins
%dir %{_libdir}/pils/plugins/*
%attr(755,root,root) %{_libdir}/pils/plugins/*/*.so
%dir %{_libdir}/stonith
%dir %{_libdir}/stonith/plugins
%dir %{_libdir}/stonith/plugins/stonith
%attr(755,root,root) %{_libdir}/stonith/plugins/stonith/*.so
%dir %{_sysconfdir}/ha.d
%dir %{_sysconfdir}/ha.d/conf
%attr(755,root,root) %{_sysconfdir}/ha.d/rc.d
%attr(755,root,root) %{_sysconfdir}/ha.d/resource.d
%{_sysconfdir}/ha.d/README.config
%attr(755,root,root) %{_sysconfdir}/ha.d/harc
%{_sysconfdir}/ha.d/shellfuncs
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) /etc/logrotate.d/heartbeat
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) /etc/logrotate.d/ldirectord
%attr(754,root,root) /etc/rc.d/init.d/heartbeat
%attr(754,root,root) /etc/rc.d/init.d/ldirectord
%dir /var/lib/heartbeat
%attr(750,root,haclient) %dir /var/lib/heartbeat/api
%attr(1770,root,haclient) %dir /var/lib/heartbeat/casual
#%attr(755,hacluster,haclient) %dir /var/lib/heartbeat/ccm
%attr(755,root,haclient) %dir /var/lib/heartbeat/ccm
%attr(755,root,haclient) %dir /var/lib/heartbeat/ckpt
%attr(600,root,root) /var/lib/heartbeat/fifo
%{_mandir}/man8/*.8*
