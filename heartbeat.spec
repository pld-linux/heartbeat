Summary:	Heartbeat - subsystem for High-Availability Linux
Summary(es):	Subsistema heartbeat para Linux "High-Availability"
Summary(pl):	Podsystem heartbeat dla system�w o podwy�szonej niezawodno�ci
Summary(pt_BR):	Implementa sistema de monitora��o (heartbeats) visando Alta Disponibilidade
Name:		heartbeat
Version:	1.2.0
Release:	0.1
License:	GPL v2+
Group:		Applications/System
Source0:	http://linux-ha.org/download/%{name}-%{version}.tar.gz
# Source0-md5:	b31e3f91c76fe006d2af94a868445293
Patch0:		%{name}-ac.patch
URL:		http://linux-ha.org/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	libnet-devel >= 1.1.0
BuildRequires:	libltdl-devel
BuildRequires:	libtool
BuildRequires:	libxml2-devel
PreReq:		rc-scripts
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(post,preun):	/sbin/chkconfig
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

TEMPL=$RPM_BUILD_ROOT/var/adm/fillup-templates
if [ ! -d $TEMPL ]; then
	install -d $TEMPL
fi
install rc.config.heartbeat $TEMPL

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
%doc doc/{*.html,AUTHORS,apphbd.cf,authkeys,ha.cf,haresources,startstop}
%attr (755,root,root) %{_sysconfdir}/ha.d/harc
%attr (755,root,root) %{_sbindir}/*
%{_sysconfdir}/ha.d/shellfuncs
%{_sysconfdir}/ha.d/rc.d
%{_sysconfdir}/ha.d/README.config
%{_sysconfdir}/ha.d/conf
%{_sysconfdir}/ha.d/resource.d
%dir %{_sysconfdir}/ha.d
/etc/rc.d/init.d/*
/etc/logrotate.d/*

# this is probably not the best location for binaries...
%{_libdir}/heartbeat
#%%{_libdir}/libhbclient.so
#%%{_libdir}/libhbclient.a
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
