# $Id: heartbeat.spec,v 1.2 1999-05-11 01:27:31 kloczek Exp $
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

%changelog
* Sun May 10 1999 Alan Robertson <alanr@henge.com>
+ Version 0.3.1
  + Make ChangeLog file from RPM specfile
  + Made ipresources only install in the DOC directory as a sample

* Sun May 09 1999 Alan Robertson <alanr@henge.com>
+ Version 0.3.0
  + Added UDP broadcast heartbeat (courtesy of Tom Vogt)
  + Significantly restructured code making it easier to add heartbeat media
  + added new directives to config file:
    + udp interface-name
    + udpport port-number
    + baud    serial-baud-rate
  + made manual daemon shutdown easier (only need to kill one)
  + moved the sample ha.cf file to the Doc directory

* Sat Mar 27 1999 Alan Robertson <alanr@henge.com>
+ Version 0.2.0
  + Make an RPM out of it
  + Integrated IP address takeover gotten from Horms
  + Added support to tickle a watchdog timer whenever our heart beats
  + Integrated enough basic code to allow a 2-node demo to occur
  + Integrated patches from Andrew Hildebrand <andrew@pdi.com> to allow it
    to run under IRIX.
  - Known Bugs
    - Only supports 2-node clusters
    - Only supports a single IP interface per node in the cluster
    - Doesn't yet include Tom Vogt's ethernet heartbeat code
    - No documentation
    - Not very useful yet :-)
