Summary:	Heartbeat - subsystem for High-Availability Linux
Summary(es):	Subsistema heartbeat para Linux "High-Availability"
Summary(pl):	Podsystem heartbeat dla systemów o podwy¿szonej niezawodno¶ci
Summary(pt_BR):	Implementa sistema de monitoração (heartbeats) visando Alta Disponibilidade
Name:		heartbeat
Version:	0.4.9.1
Release:	0.9
License:	GPL v2+
Group:		Applications/System
Source0:	http://linux-ha.org/download/%{name}-%{version}.tar.gz
Patch0:		%{name}.dirty.time.h.patch
Patch1:		%{name}-remove_groupadd_and_chgrp.patch
Patch2:		%{name}-manpath.patch
Patch3:		%{name}-doc_fix.patch
Patch4:		%{name}-install_stupidity.patch
# SuSE-specific; transformation unfinished
Patch5:		%{name}-init.patch
URL:		http://linux-ha.org/
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
BuildRequires:	links
Requires(pre):	/sbin/chkconfig
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(post):	/usr/sbin/groupdel
Requires:	syslogdaemon

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
%patch0 -p0
%patch1 -p0
%patch2 -p0
%patch3 -p1
%patch4 -p1
%patch5 -p0

%build
#zmienic to:
sed -e 's/MAKE=gmake/MAKE=make/g' < Makefile > aqq
mv -f aqq Makefile
cd doc
sed -e 's/lynx/links/' > aqq < Makefile
mv -f aqq Makefile
cd ..
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
RPM_BUILD=yes BUILD_ROOT=$RPM_BUILD_ROOT %{__make} install

rm -f $RPM_BUILD_ROOT%{_sysconfdir}/ha.d/resource.d/ldirectord
ln -sf %{_sbindir}/ldirectord $RPM_BUILD_ROOT%{_sysconfdir}/ha.d/resource.d/ldirectord

TEMPL=$RPM_BUILD_ROOT/var/adm/fillup-templates
if [ ! -d $TEMPL ]; then
	install -d $TEMPL
fi
install rc.config.heartbeat $TEMPL

rm -f doc/{*.html,*.8,COPYING,Makefile*}


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
/sbin/chkconfig --add heartbeat

%preun
Uninstall_PPP_hack() {
  file2hack=etc/ppp/ip-up.local
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
	if [ ! -x etc/ppp/ip-up.heart ]; then
		Uninstall_PPP_hack
	fi
fi

%postun
if [ "$1" = "0" ]; then
	/usr/sbin/groupdel haclient 2>/dev/null
fi

%files
%defattr(644,root,root,755)
%doc doc/*
%attr (755,root,root) %{_sysconfdir}/ha.d/harc
%attr (755,root,root) %{_sbindir}/*
%{_sysconfdir}/ha.d/shellfuncs
%{_sysconfdir}/ha.d/rc.d
%{_sysconfdir}/ha.d/README.config
%{_sysconfdir}/ha.d/conf
%{_sysconfdir}/ha.d/resource.d/
%dir %{_sysconfdir}/ha.d
/etc/rc.d/init.d/*
/etc/logrotate.d/*

# this is probably not the best location for binaries...
%{_libdir}/heartbeat
#%{_libdir}/libhbclient.so
#%{_libdir}/libhbclient.a
%{_libdir}/*.so
%{_libdir}/*.a
%dir %{_libdir}/stonith
%{_libdir}/stonith/*.so
/var/adm/fillup-templates/rc.config.heartbeat
%dir /var/lib/heartbeat
%attr (600,root,root) /var/lib/heartbeat/fifo
%attr (750,root,haclient) /var/lib/heartbeat/api
%attr (620,root,haclient) /var/lib/heartbeat/register
%attr (1770,root,haclient) /var/lib/heartbeat/casual
%{_mandir}/man8/*.8*
