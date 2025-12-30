# Working with Network Drives and External Storage

The file-organizer tool works with any mounted filesystem, including:
- External USB drives
- Network-attached storage (NAS)
- Mapped network drives (Windows)
- Mounted network shares (macOS/Linux)
- Cloud storage mounted as local drives (Dropbox, OneDrive, Google Drive, etc.)

## Basic Usage

Simply provide the path to your mounted drive:

```bash
# External USB drive (macOS)
file-organizer organize filetype /Volumes/MyExternalDrive

# Network drive (Windows)
file-organizer organize filetype "\\server\share\Documents"

# Network mount (Linux/macOS)
file-organizer organize filetype /mnt/nas/documents
```

## Network Drive Requirements

### Authentication

**Important:** The file-organizer tool operates at the filesystem level and requires that network drives are **already mounted and authenticated** before running the tool.

#### macOS/Linux

Mount network drives using standard methods:

```bash
# SMB/CIFS mount
sudo mount -t smbfs //username@server/share /mnt/nas

# Or add to /etc/fstab for automatic mounting
//server/share /mnt/nas smbfs username=user,password=pass,uid=1000,gid=1000 0 0

# NFS mount
sudo mount -t nfs server:/path /mnt/nas
```

#### Windows

Map network drives through File Explorer or command line:

```powershell
# Map network drive
net use Z: \\server\share /persistent:yes

# Or map with credentials
net use Z: \\server\share /user:username password /persistent:yes
```

Then use the mapped drive:

```bash
file-organizer organize filetype Z:\Documents
```

### Permissions

Ensure you have:
- **Read access** to scan and analyze files
- **Write access** to move/organize files (unless using `--dry-run` mode)

## Checking Path Accessibility

The tool automatically checks if paths are accessible. You can also check manually:

```python
from pathlib import Path
from file_organizer.utils.mounts import get_path_info, validate_path_for_operations

path = Path("/Volumes/MyDrive")

# Get detailed information
info = get_path_info(path)
print(f"Network path: {info['is_network']}")
print(f"Read-only: {info['is_readonly']}")
print(f"Free space: {info.get('filesystem_info', {}).get('free_space', 'Unknown')}")

# Validate for operations
is_valid, error = validate_path_for_operations(path, require_write=True)
if not is_valid:
    print(f"Error: {error}")
```

## Best Practices

### 1. Test with Dry-Run First

Always test network operations in dry-run mode first:

```bash
file-organizer preview filetype /Volumes/NetworkDrive
file-organizer organize filetype /Volumes/NetworkDrive --dry-run
```

### 2. Monitor Network Connectivity

Network interruptions can cause operations to fail:
- Use transaction logs to track operations
- Keep network connection stable during organization
- Consider organizing during low-traffic periods

### 3. Handle Large Operations

Network operations are slower than local operations:
- Consider organizing in smaller batches
- Use the `--target-folder` option to organize specific directories
- Monitor progress and be patient with large operations

### 4. Transaction Logs and Rollback

All operations are logged. If something goes wrong:

```bash
# Rollback operations
file-organizer rollback organization_transaction_log.json
```

**Important:** Rollback requires the same network path to be accessible. Make sure you can access the drive before attempting rollback.

## Cloud Storage

### Dropbox, OneDrive, Google Drive

These services typically mount as local drives:

**macOS:**
```bash
# Dropbox
file-organizer organize filetype ~/Dropbox/Documents

# OneDrive (if synced locally)
file-organizer organize filetype ~/OneDrive/Documents
```

**Windows:**
```bash
# Dropbox
file-organizer organize filetype "C:\Users\Username\Dropbox\Documents"

# OneDrive
file-organizer organize filetype "C:\Users\Username\OneDrive\Documents"
```

**Note:** Be careful with cloud storage as changes may sync automatically. Use `--dry-run` first!

## Troubleshooting

### "Path does not exist"

- Verify the drive is mounted: `ls /Volumes/` (macOS) or check File Explorer (Windows)
- Check path spelling and case sensitivity (Linux/macOS are case-sensitive)
- Ensure you have permission to access the path

### "Permission denied"

- Verify you have read/write permissions on the network share
- Check file system permissions: `ls -la /path/to/drive` (macOS/Linux)
- Ensure network credentials are valid

### "Path is read-only"

- Some network drives may be mounted read-only
- Check mount options: `mount | grep /path/to/drive`
- Remount with write permissions if needed

### Slow Performance

- Network operations are inherently slower than local
- Consider organizing during off-peak hours
- Organize smaller subdirectories separately using `--target-folder`
- Check network bandwidth and latency

### Connection Interrupted

- If connection drops during operation, check transaction log
- Rollback may be needed if operation was incomplete
- Reconnect and verify file integrity before continuing

## Example: Organizing Network Drive

```bash
# 1. Mount network drive (if not already mounted)
sudo mount -t smbfs //user@server/documents /mnt/nas-docs

# 2. Verify it's accessible
ls /mnt/nas-docs

# 3. Preview what would be organized
file-organizer preview filetype /mnt/nas-docs

# 4. Run with dry-run first
file-organizer organize filetype /mnt/nas-docs --dry-run

# 5. If everything looks good, run for real
file-organizer organize filetype /mnt/nas-docs

# 6. Generate index
file-organizer index /mnt/nas-docs
```

## Security Considerations

- **Credentials**: Never hardcode credentials in scripts. Use system keychain or mount commands with proper permissions
- **Sensitive Data**: Be cautious organizing drives containing sensitive information
- **Audit Logs**: Transaction logs contain file paths - secure them appropriately
- **Network Security**: Ensure network connections use encrypted protocols (SMB3, NFSv4 with Kerberos, etc.) when possible

## Platform-Specific Notes

### macOS

- Network volumes appear in `/Volumes/`
- Use Finder to mount SMB shares (they'll appear in `/Volumes/`)
- Check mounted volumes: `ls /Volumes/`

### Linux

- Network mounts typically in `/mnt/` or `/media/`
- Use `/etc/fstab` for automatic mounting
- Check mounted filesystems: `mount | grep network`

### Windows

- Network drives mapped to drive letters (Z:, Y:, etc.)
- Check mapped drives: `net use`
- UNC paths work: `\\server\share\path`

