# GitHub Actions Docker Build & Deploy Workflow

This directory contains the GitHub Actions workflow for building, pushing Docker images, and automatically deploying to VPS.

## Workflow: `docker-build.yml`

### Triggers

The workflow runs on:
- **Push** to `main`, `master`, or `develop` branches
- **Tags** matching `v*.*.*` (e.g., `v1.0.0`)
- **Pull requests** targeting `main`, `master`, or `develop` branches

### Features

- **Multi-platform builds**: Supports both `linux/amd64` and `linux/arm64` architectures
- **Build caching**: Uses GitHub Actions cache for faster subsequent builds
- **Automatic tagging**: Generates appropriate tags based on branch, tag, or commit SHA
- **Push to Docker Hub**: Automatically pushes images to `docker.io/nxhdev2002/fbbot`
- **Automatic VPS Deployment**: Deploys to VPS via SSH and Docker Compose on push to `main` branch

### Image Tags

The workflow generates the following tags:

| Event | Tags Generated |
|-------|----------------|
| Push to main/master | `latest`, `main`/`master`, `<commit-sha>` |
| Push to develop | `develop`, `<commit-sha>` |
| Tag `v1.2.3` | `v1.2.3`, `1.2`, `1`, `latest` |
| Pull Request | `pr-<number>`, `<commit-sha>` |

### Configuration

#### Environment Variables

You can modify these in the workflow file:

```yaml
env:
  DOCKER_IMAGE_NAME: fbbot           # Image name
  REGISTRY: docker.io                # Container registry
```

The final image will be: `docker.io/nxhdev2002/fbbot`

### Pulling the Image

After a successful build, pull the image using:

```bash
# From Docker Hub
docker pull nxhdev2002/fbbot:latest

# Or with a specific tag
docker pull nxhdev2002/fbbot:v1.0.0
```

### Running the Container

```bash
docker run -d \
  --name fbchat-bot \
  -e RIOT_API_KEY=your_riot_api_key \
  -e GEMINI_API_KEY=your_gemini_api_key \
  -e AI_PROVIDER=gemini \
  -v $(pwd)/logs:/app/logs \
  nxhdev2002/fbbot:latest
```

## VPS Deployment

### Deployment Overview

The workflow automatically deploys to VPS when:
- Code is pushed to the `main` branch
- The build job completes successfully

### Secrets Required

Add the following secrets in your GitHub repository settings (`Settings > Secrets and variables > Actions`):

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `DOCKER_USERNAME` | Docker Hub username | `nxhdev2002` |
| `DOCKER_PASSWORD` | Docker Hub password or access token | `dckr_pat_xxxxx` |
| `VAULT_ADDR` | HashiCorp Vault server URL | `https://vault.example.com` |
| `VAULT_TOKEN` | HashiCorp Vault authentication token | `hvs.xxxxxx` |
| `VAULT_SECRET_PATH` | Path to VPS credentials in Vault | `secret/data/vps/fbbot` |

### HashiCorp Vault Setup

The workflow retrieves VPS credentials from HashiCorp Vault using the KV secrets engine.

#### Vault Secret Structure

Your Vault secret at the specified path should contain the following data:

```json
{
  "host": "74.81.54.33",
  "password": "your_vps_password",
  "path": "~/fbbot",
  "port": "22",
  "user": "root"
}
```

**Important:** The `password` field is used for SSH password authentication to connect to your VPS.

#### Setting up Vault Secret

Using Vault CLI:

```bash
# Enable KV secrets engine (if not already enabled)
vault secrets enable -path=secret kv-v2

# Write the VPS credentials
vault kv put secret/vps/fbbot \
  host=74.81.54.33 \
  password=xxx \
  path="~/fbbot" \
  port=22 \
  user=root
```


#### Creating Vault Token

Create a token with appropriate permissions:

```bash
# Create a token with read access to the secret path
vault token create -policy=vps-read-policy
```

Example policy (`vps-read-policy.hcl`):

```hcl
path "secret/data/vps/fbbot" {
  capabilities = ["read"]
}
```

Apply the policy:

```bash
vault policy write vps-read-policy vps-read-policy.hcl
```

### Deployment Process

1. **Build & Push**: Docker image is built and pushed to Docker Hub
2. **Vault Authentication**: Retrieves VPS credentials from HashiCorp Vault
3. **SSH Connection**: Connects to VPS using password authentication
4. **Directory Setup**: Creates deployment directory if it doesn't exist
5. **Copy Files**: Copies `docker-compose.yml` to VPS
6. **Environment Setup**: Creates `.env` file from template if it doesn't exist
7. **Deploy**: Runs `docker-compose pull && docker-compose up -d`
8. **Verify**: Shows recent logs to verify deployment

### VPS Password Authentication

The workflow uses password authentication retrieved from Vault to connect to your VPS. Ensure that:

1. The VPS allows SSH password authentication (not just key-based)
2. The password stored in Vault is correct
3. The VPS user has sudo privileges to run Docker commands

To enable password authentication on your VPS (if disabled):

```bash
# Edit SSH config
sudo nano /etc/ssh/sshd_config

# Set these values:
PasswordAuthentication yes
PermitRootLogin yes

# Restart SSH service
sudo systemctl restart sshd
```

### Manual Deployment

To manually deploy to VPS:

```bash
# Copy files to VPS
scp docker-compose.yml root@your-vps-ip:~/fbbot/

# SSH into VPS
ssh root@your-vps-ip

# Navigate to deployment directory
cd ~/fbbot

# Pull latest image and deploy
docker-compose pull
docker-compose up -d

# View logs
docker-compose logs -f
```

### Permissions

The workflow requires the following permissions:
- `contents: read` - To checkout the repository

### Troubleshooting

#### Build fails with "permission denied"

Ensure `DOCKER_USERNAME` and `DOCKER_PASSWORD` secrets are set correctly in repository settings.

#### Image not found after push

Check that the image name is correct: `docker.io/nxhdev2002/fbbot`

#### Deployment fails with SSH error

- Verify the password stored in Vault is correct
- Ensure VPS allows password authentication (not just key-based)
- Check that VPS firewall allows SSH on the specified port
- Verify the VPS user has proper permissions

#### Vault authentication fails

- Verify `VAULT_ADDR` is correct and accessible
- Ensure `VAULT_TOKEN` is valid and has read permissions
- Check that `VAULT_SECRET_PATH` points to the correct secret
- Verify the Vault secret contains all required fields (host, port, user, path, password)

#### Multi-platform build issues

If you encounter issues with ARM64 builds, you can remove the `platforms` parameter to build only for AMD64:
```yaml
platforms: linux/amd64
```

#### Docker Compose fails on VPS

- Ensure Docker and Docker Compose are installed on VPS
- Check that the VPS has enough disk space
- Verify the `.env` file contains required environment variables

