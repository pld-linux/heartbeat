# $Id: heartbeat.spec,v 1.10 2000-07-12 14:58:55 arturs Exp $
Summary:	heartbeat - heartbeat subsystem for High-Availability Linux
Summary(pl):	heartbeat - Podsystem pulsu (heartbeat) dla systemu wysokiej dostêpno¶ci dla Linuksa
Name:		heartbeat
Version:	0.3.1
Release:	1
License:	GPL
Group:		Utilities
Group(pl):	Narzêdzia
Source0:	http://www.henge.com/~alanr/ha/download/%{name}-%{version}.tar.gz
URL:		http://www.henge.com/~alanr/ha/
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
heartbeat is a basic heartbeat subsystem for Linux-HA. It will run
scripts at initialization, and when machines go up or down. This
version will also perform IP address takeover using gratuitious ARPs.
It can even do it correctly for a 2-node configuration.

%description -l pl
heartbeat to podsystem ³±cza stanu dla systemów wysokiej dostêpno¶ci dla Linuksa. 
Uruchamia on skrypty podczas inicjalizacji oraz wtedy, kiedy maszyny s± uruchamiane 
i wy³±czane. Ta wersja dokonuje równie¿ przejêcia adresu IP wykorzystuj±c wolne ARP.
Zostanie to wykonane prawid³owo nawet w przypadku konfiguracji dwuelementowej. 

%prep
%setup -q

%build
%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%dir /etc/ha.d
/etc/rc.d/init.d/heartbeat
%config /etc/ha.d/ipresources
/etc/ha.d/heartbeat-fifo
/etc/ha.d/harc
/etc/ha.d/shellfuncs
/etc/ha.d/rc.d
/etc/ha.d/bin
%doc %{_prefix}/doc/heartbeat-0.3.1
