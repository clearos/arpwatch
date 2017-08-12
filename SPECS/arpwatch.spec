%global _vararpwatch %{_localstatedir}/lib/arpwatch
%global _hardened_build 1

Name: arpwatch
Epoch: 14
Version: 2.1a15
Release: 36%{?dist}
Summary: Network monitoring tools for tracking IP addresses on a network
Group: Applications/System
License: BSD with advertising
URL: http://ee.lbl.gov/
Requires(pre): shadow-utils 
Requires: /usr/sbin/sendmail
BuildRequires: /usr/sbin/sendmail libpcap-devel systemd

Source0: ftp://ftp.ee.lbl.gov/arpwatch-%{version}.tar.gz
Source1: arpwatch@.service
Source2: arpwatch.sysconfig
# created by:
# wget -O- http://standards.ieee.org/regauth/oui/oui.txt | \
# iconv -f iso8859-1 -t utf8 | massagevendor | bzip2
Source3: ethercodes-20110707.dat.bz2
Patch1: arpwatch-2.1a4-fhs.patch
Patch2: arpwatch-2.1a10-man.patch
Patch3: arpwatch-drop.patch
Patch4: arpwatch-drop-man.patch
Patch5: arpwatch-addr.patch
Patch6: arpwatch-dir-man.patch
Patch7: arpwatch-scripts.patch
Patch8: arpwatch-2.1a15-nolocalpcap.patch
Patch9: arpwatch-2.1a15-bogon.patch
Patch10: arpwatch-2.1a15-extraman.patch
Patch11: arpwatch-exitcode.patch
Patch12: arpwatch-2.1a15-dropgroup.patch
Patch13: arpwatch-2.1a15-devlookup.patch
Patch14: arpwatch-2.1a15-lookupiselect.patch
Patch15: arpwatch-2.1a15-lookupiinvalid.patch
Patch16: arpwatch-201301-ethcodes.patch
Patch17: arpwatch-pie.patch
Patch18: arpwatch-aarch64.patch
Patch19: arpwatch-promisc.patch
Patch20: arpwatch-ethernet-address-format.patch
Patch21: arpwatch-zero-source-ip.patch

%description
The arpwatch package contains arpwatch and arpsnmp.  Arpwatch and
arpsnmp are both network monitoring tools.  Both utilities monitor
Ethernet or FDDI network traffic and build databases of Ethernet/IP
address pairs, and can report certain changes via email.

Install the arpwatch package if you need networking monitoring devices
which will automatically keep track of the IP addresses on your
network.

%prep
%setup -q

%patch1 -p1 -b .fhs
%patch2 -p1 -b .arpsnmpman
%patch3 -p1 -b .droproot
%patch4 -p0 -b .droprootman
%patch5 -p1 -b .mailuser
%patch6 -p1 -b .dirman
%patch7 -p1 -b .scripts
%patch8 -p1 -b .nolocalpcap
%patch9 -p1 -b .bogon
%patch10 -p1 -b .extraman
%patch11 -p1 -b .exitcode
%patch12 -p1 -b .dropgroup
%patch13 -p1 -b .devlookup
%patch14 -p1 -b .iselect
%patch15 -p1 -b .iinval
%patch16 -p1 -b .ethcode
%patch17 -p1 -b .pie
%patch18 -p1 -b .aarch64
%patch19 -p1 -b .promisc
%patch20 -p1 -b .ethernet-address
%patch21 -p1 -b .zero-source-ip

%build
%configure
make ARPDIR=%{_vararpwatch}

%install

mkdir -p $RPM_BUILD_ROOT%{_mandir}/man8
mkdir -p $RPM_BUILD_ROOT%{_sbindir}
mkdir -p $RPM_BUILD_ROOT%{_vararpwatch}
mkdir -p $RPM_BUILD_ROOT%{_unitdir}
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
make DESTDIR=$RPM_BUILD_ROOT install install-man

# prepare awk scripts
perl -pi -e "s/\'/\'\\\'\'/g" *.awk

# and embed them
for i in arp2ethers massagevendor massagevendor-old; do
	cp -f $i $RPM_BUILD_ROOT%{_sbindir}
	for j in *.awk; do
		sed "s/-f\ *\(\<$j\>\)/\'\1\n\' /g" \
			< $RPM_BUILD_ROOT%{_sbindir}/$i \
			| sed "s/$j\$//;tx;b;:x;r$j" \
			> $RPM_BUILD_ROOT%{_sbindir}/$i.x
		mv -f $RPM_BUILD_ROOT%{_sbindir}/$i{.x,}
	done
	chmod 755 $RPM_BUILD_ROOT%{_sbindir}/$i
done

install -p -m644 *.dat $RPM_BUILD_ROOT%{_vararpwatch}
install -p -m644 %{SOURCE1} $RPM_BUILD_ROOT%{_unitdir}/arpwatch@.service
install -p -m644 %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/arpwatch
install -p -m644 %{SOURCE3} $RPM_BUILD_ROOT%{_vararpwatch}/ethercodes.dat.bz2
bzip2 -df $RPM_BUILD_ROOT%{_vararpwatch}/ethercodes.dat.bz2

rm -f $RPM_BUILD_ROOT%{_sbindir}/massagevendor-old
rm -f $RPM_BUILD_ROOT%{_vararpwatch}/arp.dat

%pre
if ! getent group arpwatch &> /dev/null; then
	getent group pcap 2> /dev/null | grep -q 77 &&
		/usr/sbin/groupmod -n arpwatch pcap 2> /dev/null ||
		/usr/sbin/groupadd -g 77 arpwatch 2> /dev/null
fi
if ! getent passwd arpwatch &> /dev/null; then
	getent passwd pcap 2> /dev/null | grep -q 77 &&
		/usr/sbin/usermod -l arpwatch -g 77 \
			-d %{_vararpwatch} pcap 2> /dev/null ||
		/usr/sbin/useradd -u 77 -g 77 -s /sbin/nologin \
			-M -r -d %{_vararpwatch} arpwatch 2> /dev/null
fi
:

%files
%doc README CHANGES arpfetch
%{_sbindir}/arpwatch
%{_sbindir}/arpsnmp
%{_sbindir}/arp2ethers
%{_sbindir}/massagevendor
%{_mandir}/man8/*.8*
%{_unitdir}/arpwatch@.service
%config(noreplace) %{_sysconfdir}/sysconfig/arpwatch
%attr(1775,-,arpwatch) %dir %{_vararpwatch}
%attr(0644,-,arpwatch) %verify(not md5 size mtime) %config(noreplace) %{_vararpwatch}/ethercodes.dat

%changelog
* Fri Aug 11 2017 ClearFoundation <developer@clearfoundation.com> - 14:2.1a15-36
- Added support for multiple NICs

* Wed Mar 22 2017 Jan Synáček <jsynacek@redhat.com> - 14:2.1a15-36
- refix: arpwatch detects flip flop of 0.0.0.0 for multiple DHCP Clients (#1408894)

* Wed Mar 22 2017 Jan Synáček <jsynacek@redhat.com> - 14:2.1a15-35
- arpwatch detects flip flop of 0.0.0.0 for multiple DHCP Clients (#1408894)

* Tue Mar 21 2017 Jan Synáček <jsynacek@redhat.com> - 14:2.1a15-34
- MAC addresses are not shown properly (#1368523)

* Mon Apr 18 2016 Jan Synáček <jsynacek@redhat.com> - 14:2.1a15-33
- fix typo in arpwatch-promisc.patch (#1291722)

* Thu Mar  3 2016 Jan Synáček <jsynacek@redhat.com> - 14:2.1a15-32
- fix FTBFS (#1313890)

* Wed Mar  2 2016 Jan Synáček <jsynacek@redhat.com> - 14:2.1a15-31
- add -p option that disables promiscuous mode (#1291722)

* Fri Jan 24 2014 Daniel Mach <dmach@redhat.com> - 14:2.1a15-30
- Mass rebuild 2014-01-24

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 14:2.1a15-29
- Mass rebuild 2013-12-27

* Tue Apr 23 2013 Jan Synáček <jsynacek@redhat.com> 14:2.1a15-28
- harden the package (#954336)
- support aarch64 (#925027)

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 14:2.1a15-27
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Thu Jan 17 2013 Ales Ledvinka <aledvink@redhat.com> - 14:2.1a15-26
- fix permissions related to collected database
- update ethcodes defaults to current public IEEE OUI-32

* Mon Oct 15 2012 Ales Ledvinka <aledvink@redhat.com> - 14:2.1a15-25
- fix -i with invalid interface specified (#842660)

* Mon Oct 15 2012 Ales Ledvinka <aledvink@redhat.com> - 14:2.1a15-24
- fix devlookup to start with -i interface specified (#842660)

* Wed Aug 22 2012 Jan Synáček <jsynacek@redhat.com> - 14:2.1a15-23
- Add system-rpm macros (#850032)

* Tue Jul 24 2012 Jan Synáček <jsynacek@redhat.com> - 14:2.1a15-22
- add devlookup patch: search for suitable default interface, if -i is not
  specified (#842660)

* Thu Jul 19 2012 Jan Synáček <jsynacek@redhat.com> - 14:2.1a15-21
- make spec slightly more fedora-review-friendly

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 14:2.1a15-21
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu May 31 2012 Aleš Ledvinka <aledvink@redhat.com> 14:2.1a15-20
- fix supplementary group list (#825328) (CVE-2012-2653)

* Thu Jan 19 2012 Jan Synáček <jsynacek@redhat.com> 14:2.1a15-19
- Turn on PrivateTmp=true in service file (#782477)

* Thu Jan 05 2012 Jan Synáček <jsynacek@redhat.com> 14:2.1a15-18
- Rebuilt for GCC 4.7

* Fri Jul 08 2011 Miroslav Lichvar <mlichvar@redhat.com> 14:2.1a15-17
- exit with zero error code (#699285)
- change service type to forking (#699285)

* Thu Jul 07 2011 Miroslav Lichvar <mlichvar@redhat.com> 14:2.1a15-16
- replace SysV init script with systemd service (#699285)
- update ethercodes.dat

* Mon Mar 28 2011 Miroslav Lichvar <mlichvar@redhat.com> 14:2.1a15-15
- update ethercodes.dat (#690948)

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 14:2.1a15-14
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Tue Mar 30 2010 Miroslav Lichvar <mlichvar@redhat.com> 14:2.1a15-13
- update ethercodes.dat (#577552)
- mark ethercodes.dat as noreplace
- fix init script LSB compliance
- include Debian arp2ethers and massagevendor man pages (#526160)
- don't include massagevendor-old script anymore

* Wed Sep 02 2009 Miroslav Lichvar <mlichvar@redhat.com> 14:2.1a15-12
- update ethercodes.dat

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 14:2.1a15-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Feb 23 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 14:2.1a15-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Tue Sep 16 2008 Miroslav Lichvar <mlichvar@redhat.com> 14:2.1a15-9
- update ethercodes.dat (#462364)

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 14:2.1a15-8
- Autorebuild for GCC 4.3

* Wed Aug 22 2007 Miroslav Lichvar <mlichvar@redhat.com> 14:2.1a15-7
- rebuild

* Thu Aug 09 2007 Miroslav Lichvar <mlichvar@redhat.com> 14:2.1a15-6
- improve init script (#246869)
- allow -n 0/32 to disable reporting bogons from 0.0.0.0 (#244606)
- update license tag
- update ethercodes.dat

* Wed Jun 13 2007 Miroslav Lichvar <mlichvar@redhat.com> 14:2.1a15-5
- update ethercodes.dat

* Thu May 24 2007 Miroslav Lichvar <mlichvar@redhat.com> 14:2.1a15-4
- fix return codes in init script (#237781)

* Mon Jan 15 2007 Miroslav Lichvar <mlichvar@redhat.com> 14:2.1a15-3
- rename pcap user to arpwatch

* Tue Nov 28 2006 Miroslav Lichvar <mlichvar@redhat.com> 14:2.1a15-2
- split from tcpdump package (#193657)
- update to 2.1a15
- clean up files in /var
- force linking with system libpcap
