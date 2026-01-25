# Publishing Guide for @srulyt/agent-packs

This guide explains how to publish new versions of the `@srulyt/agent-packs` npm package.

## Prerequisites

### One-Time Setup: Create NPM_TOKEN Secret (REQUIRED)

You **must** add an npm access token to GitHub Secrets for automated publishing:

#### Step 1: Create a Granular Access Token on npm

1. Go to: https://www.npmjs.com/settings/srulyt/tokens
2. Click **"Generate New Token"**
3. Select **"Granular Access Token"** (more secure than Classic tokens)
4. Fill in:
   - **Token name**: `GitHub Actions - agent-packs`
   - **Expiration**: 365 days (or your preference)
   - **Packages and scopes**: Select **"Only select packages"** → choose `@srulyt/agent-packs`
   - **Permissions**: **Read and Write**
5. Click **"Generate Token"**
6. **Copy the token** (starts with `npm_...`) - you won't see it again!

#### Step 2: Add Token to GitHub Secrets

1. Go to: https://github.com/srulyt/srulys-agent-packs/settings/secrets/actions
2. Click **"New repository secret"**
3. **Name**: `NPM_TOKEN`
4. **Value**: Paste the token from Step 1
5. Click **"Add secret"**

✅ Once added, the workflow can publish to npm using this token.

**Security**: The Granular Access Token is scoped to only `@srulyt/agent-packs` and will expire after 1 year. Renew before expiration.

## How to Publish a New Version

### Step 1: Update Version in package.json

```bash
cd installer
npm version patch  # or minor, or major
```

This updates `package.json` and creates a git commit.

### Step 2: Push the Version Tag

```bash
git push origin main
git push origin --tags
```

The workflow automatically triggers when a tag starting with `v` is pushed (e.g., `v1.0.1`).

### Step 3: Monitor the Workflow

1. Go to: https://github.com/srulyt/srulys-agent-packs/actions
2. Watch the "Publish @srulyt/agent-packs to npm" workflow
3. If successful, the new version will be on npm in ~2 minutes

## Version Bump Types

```bash
npm version patch   # 1.0.0 → 1.0.1 (bug fixes)
npm version minor   # 1.0.0 → 1.1.0 (new features, backward compatible)
npm version major   # 1.0.0 → 2.0.0 (breaking changes)
```

## Manual Publishing (Emergency Only)

If GitHub Actions fails, you can publish manually:

```bash
cd installer
npm run build
npm publish --access public
```

## Workflow Details

- **Trigger**: Pushing a git tag like `v1.0.0`
- **Authentication**: OIDC/Trusted Publishing (no tokens needed)
- **Provenance**: Automatically generates provenance attestations
- **Access**: Published as public package

## Troubleshooting

### "npm ERR! 403 Forbidden - PUT https://registry.npmjs.org/@srulyt%2fagent-packs"

**Cause**: Trusted Publishing not configured on npm.

**Solution**: Follow the "One-Time Setup on npm" section above.

### "npm ERR! You must verify your email to publish packages"

**Cause**: Your npm email is not verified.

**Solution**: 
1. Go to https://www.npmjs.com/settings/srulyt/profile
2. Verify your email address

### Workflow runs but doesn't publish

**Cause**: The tag format doesn't match `v*`.

**Solution**: Ensure your tag starts with `v` (e.g., `v1.0.0`, not `1.0.0`).

## Security

This workflow uses:
- ✅ **Trusted Publishing (OIDC)** - No long-lived tokens
- ✅ **Provenance attestations** - Cryptographically verifiable build info
- ✅ **Minimal permissions** - Only what's needed for publishing
- ✅ **Public access** - Package is publicly available

## Package URL

After publishing, the package is available at:
- **npm**: https://www.npmjs.com/package/@srulyt/agent-packs
- **Install**: `npx @srulyt/agent-packs install <pack-name>`