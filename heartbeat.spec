Summary:	Heartbeat - subsystem for High-Availability Linux
Summary(pl):	Podsystem heartbeat dla systemów o podwy¿szonej niezawodno¶ci
Name:		heartbeat
Version:	0.4.9
Release:	3
License:	GPL
URL:		http://linux-ha.org/
Group:		Applications/System
Source0:	http://linux-ha.org/download/%{name}-%{version}.tar.gz
Patch0:		%{name}.dirty.time.h.patch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
BuildRequires:	links
Requires:	sysklogd
Prereq:		/sbin/chkconfig
Prereq:		/usr/bin/getgid
Prereq:		/usr/sbin/groupadd
Prereq:		/usr/sbin/groupdel

%description
heartbeat is a basic heartbeat subsystem for Linux-HA. It will run
scripts at initialization, and when machines go up or down. This
version will also perform IP address takeover using gratuitous ARPs.
It works correctly for a 2-node configuration, and is extensible to
larger configurations.

It implements the following kinds of heartbeats:
 - Bidirectional Serial Rings ("raw" serial ports)

%description -l pl
heartbeat jest podstawowym podsystemem dla systemów o podwy¿szonej
dostêpno¶ci budowanych w oparciu o Linuxa. Zajmuje siê uruchamianiem
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
(
cd $RPM_BUILD_ROOT%{_sysconfdir}/ha.d/resource.d
  rm -f ldirectord
ln -sf %{_sbindir}/ldirectord ldirectord
)

TEMPL=$RPM_BUILD_ROOT/var/adm/fillup-templates
if
  [ ! -d $TEMPL ]
then
  install -d $TEMPL
fi
install rc.config.heartbeat $TEMPL

%files
%defattr(644,root,root,755)
%defattr(-,root,root)
%dir %{_sysconfdir}/ha.d
%{_sysconfdir}/ha.d/harc
%{_sysconfdir}/ha.d/shellfuncs
%{_sysconfdir}/ha.d/rc.d
%{_sysconfdir}/ha.d/README.config
%{_sysconfdir}/ha.d/conf
%{_libdir}/heartbeat
%{_libdir}/libhbclient.so
%{_libdir}/libhbclient.a
%{_sysconfdir}/ha.d/resource.d/
%{_sysconfdir}/init.d/heartbeat
/etc/logrotate.d/heartbeat
/var/adm/fillup-templates/rc.config.heartbeat
%dir /var/lib/heartbeat
%attr (600, root, root)       /var/lib/heartbeat/fifo
%attr (750, root, haclient) /var/lib/heartbeat/api
%attr (620, root, haclient) /var/lib/heartbeat/register
%attr (1770, root, haclient) /var/lib/heartbeat/casual
%{_mandir}/man8/heartbeat.8*
%doc doc/*

%clean
rm -rf $RPM_BUILD_ROOT

%pre
if [ -n "`/usr/bin/getgid haclient`" ]; then
	if [ "`/usr/bin/getgid haclient`" != "60" ]; then
		echo "Warning: group haclient haven't gid=60. Correct this before installing heartbeat" 1>&2
		exit 1
	fi
else
	/usr/sbin/groupadd -g 60 -r
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
