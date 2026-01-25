# Publishing Guide for @srulyt/agent-packs

This guide explains how to publish new versions of the `@srulyt/agent-packs` npm package.

## Prerequisites

### One-Time Setup on npm (REQUIRED)

You **must** configure **Trusted Publishing** on npm to allow GitHub Actions to publish without tokens:

1. Go to: https://www.npmjs.com/package/@srulyt/agent-packs/access
2. Look for **"Publishing access"** section
3. Click **"Configure trusted publishers"** or **"Link GitHub repository"**
4. Click **"Add trusted publisher"**
5. Fill in the form:
   - **Provider**: GitHub Actions
   - **Repository owner**: `srulyt`
   - **Repository name**: `srulys-agent-packs`
   - **Workflow filename**: `publish-installer.yml`
   - **Environment**: (leave empty)
6. Click **"Add"** or **"Save"**

✅ Once configured, you'll see the trusted publisher listed on the package access page.

**This setup enables OIDC authentication** - GitHub Actions proves its identity to npm without using any tokens. This is the most secure publishing method.

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