# $Id: heartbeat.spec,v 1.4 1999-07-12 23:05:58 kloczek Exp $
Summary:	heartbeat - heartbeat subsystem for High-Availability Linux
Name:		heartbeat
Version:	0.3.1
Release:	1
Copyright:	GPL
Group:		Utilities
Source:		http://www.henge.com/~alanr/ha/download/%{name}-%{version}.tar.gz
URL:		http://www.henge.com/~alanr/ha/
Buildroot:	/tmp/%{name}-%{version}-root

%description
heartbeat is a basic heartbeat subsystem for Linux-HA.
It will run scripts at initialization, and when machines go up or down.
This version will also perform IP address takeover using gratuitious ARPs.
It can even do it correctly for a 2-node configuration.

%prep
%setup -q

%build
make

%install
rm -rf $RPM_BUILD_ROOT

make install

%clean
rm -rf $RPM_BUILD_ROOT

%files
%dir /etc/ha.d
/etc/rc.d/init.d/heartbeat
%config /etc/ha.d/ipresources
/etc/ha.d/heartbeat-fifo
/etc/ha.d/harc
/etc/ha.d/shellfuncs
/etc/ha.d/rc.d
/etc/ha.d/bin
%doc /usr/doc/heartbeat-0.3.1
