# VPN Setup for VPS

## Cloudflare WARP (Recommended)

### Install
```bash
curl -fsSL https://pkg.cloudflareclient.com/install.sh | sudo bash
```

### Usage
```bash
warp-cli register        # Register device
warp-cli connect         # Connect VPN
warp-cli disconnect      # Disconnect
warp-cli status          # Check status
curl ipinfo.io           # Verify IP changed
```

### Pitfalls
- WARP changes IP but keeps same region (no geo-switching)
- May conflict with existing WireGuard configs
- Need to disable before reboot: `warp-cli disconnect`

## hide.me Free VPN

### Get WireGuard Config
1. Buka https://hide.me/en/account
2. Create Free Account (email + password)
3. Menu WireGuard → Generate Config
4. Pilih lokasi: Singapore (recommended untuk Indonesia)
5. Download .conf file

### Setup di VPS
```bash
# Install WireGuard
apt-get install -y wireguard

# Import config
cp hide-me.conf /etc/wireguard/wg0.conf
chmod 600 /etc/wireguard/wg0.conf

# Connect
wg-quick up wg0

# Verify
curl ipinfo.io

# Disconnect
wg-quick down wg0
```

### Lokasi Recommended
| Lokasi | Speed | Untuk |
|--------|-------|-------|
| Singapore | ⚡⚡⚡ | Default, paling cepat |
| Canada | ⚡⚡ | Oracle Cloud Montreal |
| US East | ⚡⚡ | Umum |

## ProtonVPN Free

### Limitasi
- Tidak ada WireGuard config untuk CLI
- Hanya bisa pakai app (Android/iOS/Windows/Mac)
- 3 lokasi: US, Japan, Netherlands
- Unlimited bandwidth

### Alternatif untuk VPS
ProtonVPN tidak support CLI/WireGuard untuk free tier. Pakai Cloudflare WARP atau hide.me.

## VPN Manager Script

Lokasi: `~/airdrop-agent/scripts/vpn_manager.sh`

```bash
./scripts/vpn_manager.sh on      # Nyalakan VPN
./scripts/vpn_manager.sh off     # Matikan VPN
./scripts/vpn_manager.sh status  # Cek status
./scripts/vpn_manager.sh switch  # Ganti IP (reconnect)
```
