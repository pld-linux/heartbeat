Summary: heartbeat - heartbeat subsystem for High-Availability Linux
Summary(pl):  podsystem heartbeat dla systemów o podwy¿szonej niezawodno¶ci
Name:	heartbeat
Version:	0.4.9
Release:	3
Copyright: GPL
URL: http://linux-ha.org/
Group: Utilities
Group(pl): Narzêdzia
Source: http://linux-ha.org/download/heartbeat-0.4.9.tar.gz
Patch0: heartbeat.dirty.time.h.patch
BuildRoot:      %{tmpdir}/%{name}-%{version}-root-%(id -u -n)
BuildPreReq: links
Requires: sysklogd

#%package stonith
#Summary: Provides an interface to Shoot The Other Node In The Head 
#Group: Utilities

%description
heartbeat is a basic heartbeat subsystem for Linux-HA.
It will run scripts at initialization, and when machines go up or down.
This version will also perform IP address takeover using gratuitous ARPs.
It works correctly for a 2-node configuration, and is extensible to larger
configurations.


It implements the following kinds of heartbeats:
	- Bidirectional Serial Rings ("raw" serial ports)
	- UDP/IP broadcast (ethernet, etc)
	- Bidirectional Serial PPP/UDP Rings (using PPP)
	- "ping" heartbeats (for routers, switches, etc.)
	   (to be used for breaking ties in 2-node systems)
%description(pl)
heartbeat jest podstawowym podsystemem dla systemów o podwy¿szonej dostêpno¶ci budowanych w oparciu o Linuxa. Zajmuje siê uruchamianiem skryptów podczas startu i zamykania systemu. Ta wersja pakietu pozwala na przejmowanie adresów IP. Oprogramowanie dzia³a poprawnie dla konfiguracji sk³adaj±cej siê z 2 hostów, mo¿na je równie¿ stosowaæ do bardziej skomplikowanych konfiguracji.

%changelog
#
%prep
%setup -q
%patch0 -p0
%build
# 
#zmienic to:
sed -e 's/MAKE=gmake/MAKE=make/g' < Makefile > aqq
mv aqq Makefile
cd doc
sed -e 's/lynx/links/' > aqq < Makefile
mv aqq Makefile
cd ..
make
###########################################################
%install
###########################################################
if
  [ -z "${RPM_BUILD_ROOT}"  -a "${RPM_BUILD_ROOT}" != "/" ]
then
  rm -rf $RPM_BUILD_ROOT
fi
RPM_BUILD=yes BUILD_ROOT=$RPM_BUILD_ROOT make install
(
  cd $RPM_BUILD_ROOT/etc/ha.d/resource.d
  rm -f ldirectord
  ln -s /usr/sbin/ldirectord ldirectord
)

TEMPL=$RPM_BUILD_ROOT/var/adm/fillup-templates
if
  [ ! -d $TEMPL ]
then
  mkdir -p $TEMPL
fi
install -m 644 rc.config.heartbeat $TEMPL

###########################################################
%files
###########################################################
%defattr(-,root,root)
%dir /etc/ha.d
/etc/ha.d/harc
/etc/ha.d/shellfuncs
/etc/ha.d/rc.d
/etc/ha.d/README.config
/etc/ha.d/conf
/usr/lib/heartbeat
/usr/lib/libhbclient.so
/usr/lib/libhbclient.a
/etc/ha.d/resource.d/
/etc/init.d/heartbeat
/etc/logrotate.d/heartbeat
/var/adm/fillup-templates/rc.config.heartbeat
%dir /var/lib/heartbeat
%attr (600, root, root)       /var/lib/heartbeat/fifo
%attr (750, root, haclient) /var/lib/heartbeat/api
%attr (620, root, haclient) /var/lib/heartbeat/register
%attr (1770, root, haclient) /var/lib/heartbeat/casual
/usr/man/man8/heartbeat.8*
%doc doc/*


###########################################################
%clean
###########################################################
rm -rf $RPM_BUILD_ROOT
rm -rf $RPM_BUILD_DIR/heartbeat-0.4.9

###########################################################
%pre
###########################################################
#
#	This isn't perfect.  But getting every distribution
#	to agree on group id's seems hard to me :-(
#
if
  grep '^haclient:' etc/group >/dev/null
then
  : OK group haclient already present
else
  GROUPOPT="-g 60"
  if
    usr/sbin/groupadd $GROUPOPT haclient 2>/dev/null
  then
    : OK we were able to add group haclient
  else
    usr/sbin/groupadd haclient
  fi
fi
#
#  Multi-distribution kludge for init scripts...
#
if
  [ ! -d etc/init.d ]
then
  if
    [ -d sbin/init.d  -a ! -L sbin/init.d ]
  then
    ln -s ../sbin/init.d etc/init.d
  elif
    [ -d etc/rc.d/init.d ]
  then
    ln -s rc.d/init.d etc/init.d
  else
    # I give up!
    echo "Warning: making directory /etc/init.d"
    mkdir -p etc/init.d
  fi
fi
###########################################################
#
#  Multi-distribution kludge for init scripts...
#
if
  [ ! -d etc/init.d ]
then
  if
    [ -d sbin/init.d  -a ! -L sbin/init.d ]
  then
    ln -s ../sbin/init.d etc/init.d
  elif
    [ -d etc/rc.d/init.d ]
  then
    ln -s rc.d/init.d etc/init.d
  else
    # I give up!
    echo "Warning: making directory /etc/init.d"
    mkdir -p etc/init.d
  fi
fi
###########################################################
%post
###########################################################

# Run heartbeat on startup
if
  [ -f etc/SuSE-release ]
then
  for d in etc/rc.d/init.d/rc[23].d
  do
    rm -f $d/S10heartbeat
    rm -f $d/S99heartbeat; ln -s ../heartbeat $d/S99heartbeat 
    rm -f $d/K35heartbeat; ln -s ../heartbeat $d/K35heartbeat
  done
  FILLUP=/bin/fillup
  if 
    $FILLUP -q -d = etc/rc.config var/adm/fillup-templates/rc.config.heartbeat
  then
    : fillup returned OK
  else
    echo "ERROR: $FILLUP failed. This should not happen. Please compare"
    echo "/etc/rc.config and /var/adm/fillup-templates/rc.config.heartbeat"
    echo "and update by hand."
  fi
elif
  [ -x sbin/chkconfig ]
then
  sbin/chkconfig --add heartbeat
fi
true

###########################################################
%preun
###########################################################

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

if
  [ $1 = 0 ]
then
  [ -x sbin/chkconfig ] && sbin/chkconfig --del heartbeat
  if
    [ ! -x etc/ppp/ip-up.heart ]
  then
    Uninstall_PPP_hack
  fi
fi
if
   [ -r etc/SuSE-release ]
then
  rm -f sbin/init.d/rc[23]/*heartbeat
fi
true
