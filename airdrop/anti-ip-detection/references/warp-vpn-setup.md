# Cloudflare WARP VPN Setup (Free Proxy)

## Overview
Cloudflare WARP = free VPN with unlimited bandwidth, Singapore IP, no account needed.

## Install (Ubuntu 22.04 Jammy)
```bash
# Add repo
curl -fsSL https://pkg.cloudflareclient.com/pubkey.gpg | sudo gpg --dearmor -o /usr/share/keyrings/cloudflare-warp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/cloudflare-warp-archive-keyring.gpg] https://pkg.cloudflareclient.com/ jammy main" | sudo tee /etc/apt/sources.list.d/cloudflare-client.list
sudo apt-get update && sudo apt-get install -y cloudflare-warp
```

## Register (Non-Interactive)
```bash
# warp-cli needs TTY for TOS acceptance — use expect
sudo apt-get install -y expect
expect -c 'spawn warp-cli registration new; expect "Accept"; send "y\r"; expect eof'
```

## Usage
```bash
warp-cli connect      # Connect (IP changes to Cloudflare Singapore)
warp-cli disconnect   # Disconnect (back to VPS IP)
warp-cli status       # Check status
curl ipinfo.io        # Verify IP change
```

## VPN Manager Script
Location: `~/airdrop-agent/scripts/vpn_manager.sh`
```bash
./vpn_manager.sh on       # WARP on
./vpn_manager.sh off      # WARP off
./vpn_manager.sh status   # Check status
./vpn_manager.sh switch   # Reconnect
```

## Pitfalls
- ⚠️ `warp-cli registration new` needs `--accept-tos` but that flag doesn't exist in newer versions — use `expect` instead
- ⚠️ Kernel version mismatch warning is OK — WARP still works
- ⚠️ WARP IP is Cloudflare Singapore — not residential, some sites may detect
- ⚠️ 1 device per free account — can't use on multiple VPS simultaneously
- ⚠️ First connection may take 10-15 seconds to establish

## vs Other Free VPNs
| VPN | Bandwidth | Account? | IP Type | Setup |
|-----|-----------|----------|---------|-------|
| WARP | Unlimited | No | Cloudflare SG | CLI |
| hide.me | 10GB/mo | Yes | Various | App only |
| ProtonVPN | Unlimited | Yes | 3 locations | App only |
