#!/bin/bash
set -e

# Configuration
CT_ID=200
CT_HOSTNAME="plex-troubadour"
CT_PASSWORD="ChangeMe123!" # Ideally fetched from secrets env
STORAGE_ID="local-lvm"
TEMPLATE_URN="debian-12-standard_12.2-1_amd64.tar.zst"
NET_TAG=90 # "Rivendell" VLAN - Trusted Personal Devices
MEDIA_MOUNT_SRC="/mnt/pve/media" # Assuming Proxmox host has media mounted here
MEDIA_MOUNT_DST="/mnt/media"

echo "=== Setting up Plex LXC on Troubadour ==="

# 1. Check if template exists, download if not
pveam update
if ! pveam list local | grep -q "$TEMPLATE_URN"; then
    echo "Downloading Debian template..."
    pveam download local $TEMPLATE_URN
fi

# 2. Create the Container
if pct list | grep -q "$CT_ID"; then
    echo "Container $CT_ID already exists. Skipping creation."
else
    echo "Creating LXC Container $CT_ID..."
    # Privileged container needed for easy hardware passthrough
    pct create $CT_ID /var/lib/vz/template/cache/$TEMPLATE_URN \
        --hostname $CT_HOSTNAME \
        --features nesting=1 \
        --password $CT_PASSWORD \
        --rootfs $STORAGE_ID:8 \
        --net0 name=eth0,bridge=vmbr0,firewall=1,ip=dhcp,tag=$NET_TAG \
        --ostype debian \
        --unprivileged 0 \
        --start 0
fi

# 3. Configure iGPU Passthrough (Intel QuickSync)
# This adds the render node to the LXC config
CONFIG_FILE="/etc/pve/lxc/${CT_ID}.conf"

if ! grep -q "lxc.cgroup2.devices.allow: c 226" "$CONFIG_FILE"; then
    echo "Configuring iGPU passthrough in $CONFIG_FILE..."
    cat <<EOF >> $CONFIG_FILE
# iGPU Passthrough for Plex
lxc.cgroup2.devices.allow: c 226:0 rwm
lxc.cgroup2.devices.allow: c 226:128 rwm
lxc.mount.entry: /dev/dri/renderD128 dev/dri/renderD128 none bind,optional,create=file
EOF
fi

# 4. Bind Mount Media Storage
# This assumes the Proxmox HOST has the NAS mounted at $MEDIA_MOUNT_SRC
# You might need to add a mount command to /etc/fstab on the host first if not present.
if ! grep -q "$MEDIA_MOUNT_DST" "$CONFIG_FILE"; then
    echo "Configuring Bind Mount for Media..."
    cat <<EOF >> $CONFIG_FILE
# Media Mount
mp0: $MEDIA_MOUNT_SRC,mp=$MEDIA_MOUNT_DST
EOF
fi

# 5. Start and Install Plex
echo "Starting Container..."
pct start $CT_ID
sleep 10 # Wait for boot

echo "Installing Plex inside Container..."
pct exec $CT_ID -- bash -c "apt-get update && apt-get install -y curl gnupg"
pct exec $CT_ID -- bash -c "echo 'deb https://downloads.plex.tv/repo/deb public main' | tee /etc/apt/sources.list.d/plexmediaserver.list"
pct exec $CT_ID -- bash -c "curl https://downloads.plex.tv/plex-keys/PlexSign.key | apt-key add -"
pct exec $CT_ID -- bash -c "apt-get update && apt-get install -y plexmediaserver"

echo "=== Plex LXC Setup Complete ==="
echo "Access Plex at http://<IP_OF_CT>:32400/web"
