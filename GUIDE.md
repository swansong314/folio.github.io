# How to Create Your GitHub Personal Access Token

To create your portfolio website, you'll need a GitHub Personal Access Token (PAT). Don't worry - this is completely safe and your token is never stored by our system.

## What is a Personal Access Token?

A Personal Access Token is like a secure password that allows the Portfolio Generator to create a new repository in your GitHub account. **Your token is used only once during the portfolio creation process and is never saved or stored anywhere.**

## Step-by-Step Instructions

### 1. Go to GitHub Settings
- Log in to your GitHub account at [github.com](https://github.com)
- Click on your profile picture in the top-right corner
- Select **"Settings"** from the dropdown menu

### 2. Navigate to Developer Settings
- Scroll down in the left sidebar
- Click **"Developer settings"** (near the bottom)
- Click **"Personal access tokens"**
- Select **"Tokens (classic)"**

### 3. Create New Token
- Click the **"Generate new token"** button
- Choose **"Generate new token (classic)"**
- You may need to enter your GitHub password for security

### 4. Configure Your Token
Fill out the token creation form:

**Token Name:** 
- Enter something descriptive like "Portfolio Generator"

**Expiration:**
- Choose "30 days" or "90 days" (recommended for security)

**Permissions (Important!):**
- ✅ Check **"repo"** - This gives permission to create public repositories
- ❌ Leave all other boxes unchecked (not needed)

### 5. Generate and Copy Your Token
- Click **"Generate token"** at the bottom
- **IMMEDIATELY COPY THE TOKEN** - it looks like `ghp_xxxxxxxxxxxxxxxxxxxx`
- ⚠️ **Important**: You can only see this token once! If you lose it, you'll need to create a new one

## Security & Privacy

### Your Token is Safe
- ✅ **Never stored**: Your token is only used during portfolio creation and immediately discarded
- ✅ **Secure transmission**: All communication is encrypted (HTTPS)
- ✅ **Minimal permissions**: Only has access to create public repositories
- ✅ **Time-limited**: You can set an expiration date on your token

### Best Practices
- 🔒 **Don't share your token** with anyone else
- 🔒 **Don't post it online** or in emails
- 🔒 **Copy it directly** from GitHub to the form (don't save it in a text file)
- 🔒 **Delete expired tokens** from your GitHub settings

## What Happens During Portfolio Creation?

1. **Verification**: We verify your token is valid
2. **Repository Creation**: We create a new `yourusername.github.io` repository
3. **Content Addition**: We populate it with your personalized portfolio content
4. **Cleanup**: Your token is immediately discarded from memory

**That's it!** Within minutes, you'll have a beautiful portfolio website live at `https://yourusername.github.io`

## Troubleshooting

### "Invalid token" error?
- Make sure you copied the entire token (starts with `ghp_`)
- Check that you selected the **"repo"** permission
- Verify the token hasn't expired

### "Repository already exists" error?
- You already have a `yourusername.github.io` repository
- Either delete the existing one or use a different GitHub account

## Need Help?

If you run into any issues, the most common problem is not selecting the "repo" permission when creating your token. Just create a new token and make sure to check that box!

---

*Remember: Your Personal Access Token is never stored or saved by the Portfolio Generator. It's used once to create your portfolio and then immediately discarded for your security.*