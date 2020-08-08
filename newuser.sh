#!/bin/bash

until [[ $CLIENT =~ ^[a-zA-Z0-9_]+$ ]]; do
    read -rp "User name: " -e CLIENT
done


until [[ $PASSWD != '' ]]; do
    read -rp "Password: " -e -s PASSWD
done

useradd -s /usr/sbin/nologin "$CLIENT"
passwd $CLIENT
su -c "google-authenticator -t -d -r3 -R30 -f -l 'OpenVPN Server' -s /etc/openvpn/gauth/${CLIENT}" - gauth
echo "User $CLIENT added."
python3 totp.py $CLIENT
exit 0