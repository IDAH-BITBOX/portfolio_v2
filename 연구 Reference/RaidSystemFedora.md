## Data Server Construction

Reference Link : [Mirror your System Drive using Software RAID - Fedora Magazine](https://fedoramagazine.org/mirror-your-system-drive-using-software-raid/)

[RAID 구성 : 네이버 블로그 (naver.com)](https://m.blog.naver.com/PostView.naver?isHttpsRedirect=true&blogId=rpg2003a&logNo=221175567274)

### 0. Must know your hard disk info.

    $ su
    # fdisk -l

* check the hard disk's MAC address and mount point (/dev/[mount point])

* ! Caution ! : we will use raid 1 (mirroring), so the available spaces of 2 hard disks must be same.
* In this paper, we use 2 hard disks of 8TB .
* Fedora version : 35 (installed in AHCI mode hard disk of 500GB)

### 1. Partition Settings
#### 1) Basic hard disk to store data partition setting

    # MY_DISK_1=/dev/sdb
    # sgdisk --zap-all $MY_DISK_1
    # sgdisk -n 0:0+1MiB -t 0:ef02 -c 0:grub_1 $MY_DISK_1
    # sgdisk -n 0:0+1GiB -t 0:ea00 -c 0:boot_1 $MY_DISK_1
    # sgdisk -n 0:0+4GiB -t 0:fd00 -c 0:swap_1 $MY_DISK_1
    # sgdisk -n 0:0:0 -t 0:fd00 -c 0:root_1 $MY_DISK_1

#### 2) Mirroring hard disk partition setting

    # MY_DISK_2=/dev/sda
    # sgdisk -n 0:0+1MiB -t 0:ef02 -c 0:grub_2 $MY_DISK_2
    # sgdisk -n 0:0+1GiB -t 0:ea00 -c 0:boot_2 $MY_DISK_2
    # sgdisk -n 0:0+4GiB -t 0:fd00 -c 0:swap_2 $MY_DISK_2
    # sgdisk -n 0:0:0 -t 0:fd00 -c 0:root_2 $MY_DISK_2

### 2. Create RAID Device for storing hard disk
#### 1) Create RAID of Basic hard disk to store data 

    # mdadm --create /dev/md/boot --homehost=any --metadata=1.0 --level=1 --raid-devices=2 /dev/disk/by-partlabel/boot_1 missing
    # mdadm --create /dev/md/swap --homehost=any --metadata=1.0 --level=1 --raid-devices=2 /dev/disk/by-partlabel/swap_1 missing
    # mdadm --create /dev/md/root --homehost=any --metadata=1.0 --level=1 --raid-devices=2 /dev/disk/by-partlabel/root_1 missing
    # dracut -f --add mdraid --add-drivers xfs

#### 2) Format the RAID device

    # mkfs -t vfat /dev/md/boot
    # mkswap /dev/md/swap
    # mkfs -t xfs /dev/md/root

#### 3) Reboot

    # reboot

### 3. Mount point settings

    # mkdir /newroot
    # dnf group list hidden
    # dnf groups install "Fedora Server Edition" --installroot=/newroot/ --releasever=35 -y
    # rm -rf /newroot/boot/*
    
    # mount /dev/md/root /newroot
    # mount /dev/md/boot /newroot/boot
    # shopt -s dotglob
    # mv /newroot/boot/efi/EFI/* /newroot/boot/efi
    # rmdir /newroot/boot/efi/EFI
    # ln -sfr /newroot/boot/efi/fedora/grub.cfg /newroot/etc/grub2-efi.cfg
    # umount /newroot

    # touch /newroot/etc/fstab
    # vi /newroot/etc/fstab
    /dev/md/root / xfs defaults 0 0
    /dev/md/boot /boot vfat defaults 0 0
    /dev/md/swap swap swap defaults 0 0

### 4. Check the partitions

    # parted /dev/sdb unit MiB print
    # parted /dev/sda unit MiB print

### 5. Create RAID Device for mirroring hard disk

    # mdadm --manage /dev/md/boot --add /dev/disk/by-partlabel/boot_2
    # mdadm --manage /dev/md/swap --add /dev/disk/by-partlabel/swap_2
    # mdadm --manage /dev/md/root --add /dev/disk/by-partlabel/root_2


### 6. Test Your RAID Devices

