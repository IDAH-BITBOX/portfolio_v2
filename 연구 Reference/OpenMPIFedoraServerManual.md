# Cluster Installation Guide with Fedora 34 Workstation

## Install

1. Prepare USB over 8GB
2. On Windows machine, download Fedora Media Writer: https://getfedora.org/fmw/FedoraMediaWriter-win32-latest.exe
3. Make booting USB using Fedora Media Writer
4. Refer to https://www.debugpoint.com/2021/07/install-fedora-34-workstation/#download-create-USB install Fedora on your computer
5. Reboot your computer without USB
6. If you seccess booting, modify your dnf package manager configuration
```shell
max_parallel_downloads=10 >> /etc/dnf/dnf.conf
fastestmirror=True >> /etc/dnf/dnf.conf
```
7. Change your root password
```shell
sudo passwd root
```

## Network Configuration

* In general, Network Manager daemon auto-configure your network service
* If you want to configure network manually
  1. simply click the button on the top right corner of your monitor
  2. click ethernet device you want to set and enter Wired Settings
  3. go to IPv4 tab and check Manual button and set Address, Netmask, Gateway, and DNS

## Download the packages

* As a root user
* In order to change user root, type **su** command  in your terminal and put your root password you set above
```shell
dnf install openssh-server dhcp vim nfs-utils tftp-server # you can add packages what you need
```

### 1. Make NFS root Folder

* NFS : Network File System. Client can save files through NFS without physically attached storages.

```shell
mkdir -p /tftpboot/nfsroot
chmod 777 /tftpboot # for access by NFS.
```

### 2. Download Client OS system

* Client can have different OS version technically
* We use Fedora Server Edition for client here

```shell
dnf group list hidden # you can see the list of groups install
dnf groups install "Fedora Server Edition" --installroot=/tftpboot/nfsroot/ --releasever=34 -y
```

### 3. Download Fedora Boot Images

* Client boot using these files below.

```shell
cd /tftpboot # change directory to /tftpboot
wget https://download.fedoraproject.org/pub/fedora/linux/releases/34/Server/x86_64/os/isolinux/boot.msg
wget https://download.fedoraproject.org/pub/fedora/linux/releases/34/Server/x86_64/os/isolinux/grub.conf
wget https://download.fedoraproject.org/pub/fedora/linux/releases/34/Server/x86_64/os/isolinux/initrd.img
wget https://download.fedoraproject.org/pub/fedora/linux/releases/34/Server/x86_64/os/isolinux/isolinux.bin
wget https://download.fedoraproject.org/pub/fedora/linux/releases/34/Server/x86_64/os/isolinux/isolinux.cfg
wget https://download.fedoraproject.org/pub/fedora/linux/releases/34/Server/x86_64/os/isolinux/ldlinux.c32
wget https://download.fedoraproject.org/pub/fedora/linux/releases/34/Server/x86_64/os/isolinux/libcom32.c32
wget https://download.fedoraproject.org/pub/fedora/linux/releases/34/Server/x86_64/os/isolinux/libutils.c32
wget https://download.fedoraproject.org/pub/fedora/linux/releases/34/Server/x86_64/os/isolinux/memtest
wget https://download.fedoraproject.org/pub/fedora/linux/releases/34/Server/x86_64/os/isolinux/splash.png
wget https://download.fedoraproject.org/pub/fedora/linux/releases/34/Server/x86_64/os/isolinux/vesamenu.c32
wget https://download.fedoraproject.org/pub/fedora/linux/releases/34/Server/x86_64/os/isolinux/vmlinuz
cp /usr/share/syslinux/pxelinux.0 /tftpboot/ # if there is no pxelinux.0 dnf install syslinux
```

### 4. Disable selinux

* selinux : Security-Enhanced Linux. We don't need it.

```shell
vi /etc/selinux/config
```

* Modify file like below.

```yaml
SELINUX=disabled
SELINUXTYPE=targeted
```

### 5. Host Setting

* The hosts(other computers. Client here) allowed to access server.

```shell
vi /etc/hosts.allow
```

* Add lines below.

```yaml
in.tftp:ALL
sshd:ALL
ALL:10.100.1.
```

* Add IP-hostname pairs.

```shell
vi /etc/hosts
```

* Add lines below.

```yaml
192.168.0.42 main.cluster main main
10.100.0.1  main.cluster main main
10.100.1.1  node1.cluster   node1   node01
10.100.1.2  node2.cluster   node2   node02
10.100.1.3  node3.cluster   node3   node03
10.100.1.4  node4.cluster   node4   node04
```

* Copy these files to _/tftpboot/nfsroot/etc/{hosts,hosts.allow}_ for client

```shell
cp /etc/hosts.allow /tftpboot/nfsroot/etc/hosts.allow
cp /etc/hosts /tftpboot/nfsroot/etc/hosts
```

### 6. TFTP Setting

* TFTP : Trivial File Transfer Protocol. We have to change files route to transfer from server to client.

```shell
vi /lib/systemd/system/tftp.service
```

* Change route like below.

```yaml
#ExecStart=/usr/sbin/in.tftpd -s /var/lib/tftpboot
ExecStart=/usr/sbin/in.tftpd -s /tftpboot
```

### 7. NFS Setting

* _/etc/exports_ contains a table of local physical file systems on an NFS server that are accessible to NFS clients.

```shell
vi /etc/exports
```

* Write down like below.

```yaml
#/usr    *(rw,sync,no_root_squash)
/home    *(rw,sync,no_root_squash)
/tftpboot/nfsroot/    10.100.1.1(rw,sync,no_root_squash)
#/tftpboot/nfsroot/    10.100.1.2(rw,sync,no_root_squash)
#/tftpboot/nfsroot/    [new nodes ip address](rw,sync,no_root_squash)
```

* _/tftpboot/nfsroot/etc/fstab_ is a system configuration file which has all available disk partitions including NFS. Client can know how they are to be initialized by NFS.

```shell
vi /tftpboot/nfsroot/etc/fstab
```

* Type below.

```yaml
10.100.0.1:/tftpboot/nfsroot    /    nfs    defaults    0 0
10.100.0.1:/home    /home    nfs    defaults    0 0
#10.100.0.1:/usr    /usr    nfs    defaults    0 0
none    /dev/pts    devpts    gid=5,mode=620    0 0
none    /proc    proc    defaults    0 0
none    /dev/shm    tmpfs    defaults    0 0
none    /sys    sysfs    defaults    0 0
```

### 8. Pxelinux Configuration

* pxelinux : Boot loader for booting from a network server using a network ROM conforming to the Intel PXE(Pre-eXecution Environment) specification.
* In short, client computer boot by images that came from server through lan cable. Then, pxelinux configuration let the client know where the images are by default.

```shell
mkdir /tftpboot/pxelinux.cfg
vi /tftpboot/pxelinux.cfg/default
```

* Type below

```yaml
default dskless
label dskless

kernel vmlinuz
append initrd=initrd.img root=nfs:10.100.0.1:/tftpboot/nfsroot ip=dhcp rw selinux=0  audit=0
```

### 9. DHCP Configuration 
* DHCP : Dynamic Host Configuration Protocol. It is a network management protocol used on IP networks for automatically assigning IP addresses and other communication parameters to devices connected to the network using a client-server architecture.

```shell
vi /etc/dhcp/dhcpd.conf
```

* modify dhcpd.conf like below.

```yaml
#
# DHCP Server Configuration file.
#   see /usr/share/doc/dhcp-server/dhcpd.conf.example
#   see dhcpd.conf(5) man page
#

subnet 10.100.0.0 netmask 255.255.0.0 {
    next-server 10.100.0.1;
    range 10.100.1.1 10.100.255.255;
    ddns-update-style    none;
    default-lease-time    -1;
    max-lease-time    -1;

    option routers  10.100.0.1;
    option subnet-mask      255.255.0.0;
    option broadcast-address        10.100.255.255;
    option log-servers 10.100.0.1;
}
group{
    filename "pxelinux.0";
    use-host-decl-names on;
    host node1 {
        fixed-address 10.100.1.1;
        hardware ethernet 10:7B:44:9F:0C:1E;
    }
    host node2 {
        fixed-address 10.100.1.2;
        hardware ethernet B0:6E:BF:CD:3E:24;
    }
    host node3 {
        fixed-address 10.100.1.3;
        hardware ethernet B0:6E:BF:CD:3F:3A;
    }
    host node4 {
        fixed-address 10.100.1.4;
        hardware ethernet B0:6E:BF:D1:E0:56;
    }
}
```

### 10. Copy User Information

* Client must have a same user information of server.

```shell
cp -a /etc/passwd /tftpboot/nfsroot/etc/ # -a option is for making a copy that is as close to the original as possible
cp -a /etc/shadow /tftpboot/nfsroot/etc/
cp -a /etc/group /tftpboot/nfsroot/etc/
cp -a /etc/gshadow /tftpboot/nfsroot/etc/
```

### 11. Firewall Configurations

* Firewall : Security service that can help protect your network by filtering traffic and blocking outsiders from gaining unauthorized access to the private data on your computer.
* We have to configure the firewall exceptions for necessary services such as tftp, dhcp, nfs, ssh.
* We use clients computer under internal network. So shutdown or remove firewall daemon on the client.

```shell
firewall-cmd --add-service=tftp --perm
firewall-cmd --add-port=69/udp
firewall-cmd --zone public --add-service tftp
firewall-cmd --permanent --zone public --add-service tftp
firewall-cmd --add-service=nfs --perm
firewall-cmd --add-port=111/udp
firewall-cmd --add-port=2049/udp
firewall-cmd --zone public --add-service nfs
firewall-cmd --permanent --zone public --add-service nfs
firewall-cmd --add-service=dhcp --perm
firewall-cmd --add-port=67/udp
firewall-cmd --add-port=68/udp
firewall-cmd --zone public --add-service dhcp
firewall-cmd --permanent --zone public --add-service dhcp
firewall-cmd --reload
```

* Remove firewalld for client

```shell
dnf remove firewalld --installroot=/tftpboot/nfsroot/ -y
```

### 12. Enable Crucial Daemons

* We have to make crucial daemons automatically start on boot.

```shell
systemctl enable nfs-server.service
systemctl enable dhcpd.service
systemctl enable tftp.service
```

### 13. Management of Server
1.  For new user adding
	* login to admin
```shell
sudo adduser -m [user_name]
cp -a /etc/passwd /tftpboot/nfsroot/etc/ # -a option is for making a copy that is as close to the original as possible
cp -a /etc/shadow /tftpboot/nfsroot/etc/
cp -a /etc/group /tftpboot/nfsroot/etc/
cp -a /etc/gshadow /tftpboot/nfsroot/etc/
```
2.  For installing new modules (for front end server)
	* login to admin
```shell
(Easy way)
sudo dnf install [module_name]

or

(Best way)
wget [download link]
tar -xzvf [downloaded file (tar.gz)]
cd [extracted folder]
./configure --prefix=[install root]
sudo make all install
```

3.  For installing new modules (for computing nodes)
	*  login to admin
```shell
(Easy way)
sudo dnf install [module_name] --installroot=/tftpboot/nfsroot/

or

(Best way)
ssh node1
wget [download link]
tar -xzvf [downloaded file (tar.gz)]
cd [extracted folder]
./configure --prefix=[install root]
sudo make all install
```

4. For adding new computing nodes
	* Bios settings
		* (we use lan boot (pxeboot) for each node)
		* make LAN available
		* make PXEBOOT available
		* make fastboot unavailable
		* save and reboot

	* Connect monitor to a new node and check the MAC address of it (it might be good to write down or capture or... etc.)

	* Server setting
		* login to front end server through admin
		* add new node information to /etc/hosts file & copy it to /tftpboot/nfsroot/etc/
		* add new node information to /etc/exports file
		* add new node information to /etc/dhcp/dhcpd.conf file (MAC address is needed)
		* all of connected nodes shutdown..! (Please announce it to all members of laboratory)
		* restart services (nfs-server.service, dhcpd.service, tftp.service)
		


5. Example of Installing openmpi to computing node
(from local computer)
```shell
[local@...]$ ssh [admin]@[front-end server's ip]
## Input passwd of admin ##

[admin@main ~]$ sudo dnf install gcc-c++ -y
[admin@main ~]$ ssh node1
[admin@node1 ~]$ wget https://download.open-mpi.org/release/open-mpi/v4.1/openmpi-4.1.1.tar.gz  
[admin@node1 ~]$ tar -xvf openmpi-4.1.1.tar.gz
[admin@node1 ~]$ cd openmpi-4.1.1
[admin@node1 ~]$ ./configure --prefix=/usr/local
.......pre-installing.......
[admin@node1 ~]$ sudo make all install
.........installing.........
```
