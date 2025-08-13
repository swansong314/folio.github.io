# Setup Guide for Portfolio Generator

This guide will walk you through setting up and using the Portfolio Generator to create your personal GitHub Pages website.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Creating a GitHub Personal Access Token](#creating-a-github-personal-access-token)
- [Setting up hCaptcha](#setting-up-hcaptcha)
- [Deployment Instructions](#deployment-instructions)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before you begin, make sure you have:
- A GitHub account
- AWS CLI configured with appropriate permissions
- AWS SAM CLI installed
- Node.js and npm (for local development)

## Creating a GitHub Personal Access Token

The Portfolio Generator needs a GitHub Personal Access Token (PAT) to create and populate your portfolio repository. Follow these steps:

### Step 1: Navigate to GitHub Settings
1. Log in to your GitHub account
2. Click on your profile picture in the top-right corner
3. Select **Settings** from the dropdown menu

### Step 2: Access Developer Settings
1. Scroll down in the left sidebar and click **Developer settings**
2. Click **Personal access tokens**
3. Select **Tokens (classic)**

### Step 3: Generate New Token
1. Click **Generate new token**
2. Select **Generate new token (classic)**
3. You may be prompted to confirm your password

### Step 4: Configure Token Settings
1. **Note**: Give your token a descriptive name like "Portfolio Generator"
2. **Expiration**: Choose an appropriate expiration time (recommended: 90 days)
3. **Select scopes**: Check the **`repo`** checkbox
   - ✅ **repo** (Full control of private repositories)
     - This includes `repo:status`, `repo_deployment`, `public_repo`, `repo:invite`, and `security_events`

### Step 5: Generate and Copy Token
1. Click **Generate token** at the bottom
2. **IMPORTANT**: Copy the token immediately and store it securely
3. This token will look like: `ghp_xxxxxxxxxxxxxxxxxxxx`

### Security Notes
- ⚠️ **Never share your personal access token publicly**
- ⚠️ **Don't commit tokens to repositories**  
- ⚠️ **Store tokens securely** (password manager recommended)
- ✅ **Set reasonable expiration dates**
- ✅ **Use minimum required permissions**

## Setting up hCaptcha

The Portfolio Generator uses hCaptcha to prevent abuse. Here's how to set it up:

### Step 1: Create hCaptcha Account
1. Go to [hCaptcha.com](https://www.hcaptcha.com/)
2. Click **Sign Up** and create an account
3. Verify your email address

### Step 2: Create a New Site
1. Log in to your hCaptcha dashboard
2. Click **New Site**
3. Enter your domain information:
   - **Site Name**: Portfolio Generator
   - **Hostnames**: Add your frontend domain (e.g., `yourusername.github.io`)
   - For local testing, also add `localhost`

### Step 3: Get Your Keys
1. After creating the site, you'll see:
   - **Site Key** (public): Used in your frontend
   - **Secret Key** (private): Used in your backend Lambda

### Step 4: Configure the Application
1. **Frontend**: Replace `YOUR_HCAPTCHA_SITE_KEY` in `frontend/index.html`
2. **Backend**: Set the `HCAPTCHA_SECRET_KEY` environment variable during deployment

## Deployment Instructions

### Backend Deployment

1. **Configure AWS Credentials**:
   ```bash
   aws configure
   ```

2. **Deploy the Backend**:
   ```bash
   cd backend
   # Copy portfolio template files
   cp -r ../portfolio-template/ ./src/
   # Build and deploy
   sam build
   sam deploy --guided
   ```

3. **During deployment**, you'll be prompted for:
   - Stack name: `portfolio-generator`
   - AWS Region: Choose your preferred region
   - hCaptcha Secret Key: Enter your hCaptcha secret key
   - Confirm other default values

4. **Note the API Gateway URL** from the deployment output

### Frontend Configuration

1. **Update API Endpoint**:
   - Open `frontend/script.js`
   - Replace `YOUR_API_GATEWAY_URL` with your actual API Gateway URL

2. **Update hCaptcha Site Key**:
   - Open `frontend/index.html`
   - Replace `YOUR_HCAPTCHA_SITE_KEY` with your actual site key

### Frontend Deployment (GitHub Pages)

1. **Enable GitHub Pages** for your repository:
   - Go to repository Settings → Pages
   - Set source to "GitHub Actions"

2. **Push changes** to trigger automatic deployment

## Usage

### Using the Portfolio Generator

1. **Open the Frontend**: Navigate to your deployed frontend URL
2. **Fill out the form**:
   - **Name**: Your full name
   - **Email**: Your contact email
   - **Bio**: Brief description about yourself
   - **Projects**: List your projects and achievements
   - **GitHub PAT**: Your personal access token
3. **Complete CAPTCHA**: Solve the hCaptcha challenge
4. **Click "Generate Portfolio"**: Wait for the process to complete
5. **Success**: You'll receive links to your new repository and live website

### What Gets Created

The generator creates a `username.github.io` repository with:
- Jekyll-powered portfolio website
- Customized content from your form input
- GitHub Actions workflow for automatic deployment
- Professional styling and responsive design

## Troubleshooting

### Common Issues

#### "Invalid GitHub Personal Access Token"
- **Solution**: Check that your token has `repo` permissions
- **Solution**: Verify the token hasn't expired
- **Solution**: Make sure you copied the entire token correctly

#### "Repository already exists"
- **Issue**: You already have a `username.github.io` repository
- **Solution**: Delete the existing repository or use a different GitHub account

#### "Invalid CAPTCHA"
- **Solution**: Complete the hCaptcha challenge
- **Solution**: Check that the site key is configured correctly
- **Solution**: Ensure your domain is added to hCaptcha site settings

#### "GitHub API rate limit exceeded"
- **Issue**: Too many API requests
- **Solution**: Wait a few minutes and try again
- **Solution**: The API has throttling built-in to prevent this

#### Website not deploying
- **Issue**: GitHub Pages not building
- **Solution**: Check the Actions tab in your repository for build errors
- **Solution**: Ensure GitHub Pages is enabled in repository settings
- **Solution**: Wait 5-10 minutes for initial deployment

### Getting Help

If you encounter issues:
1. Check the browser console for JavaScript errors
2. Review the Lambda function logs in AWS CloudWatch
3. Verify all configuration steps were completed
4. Check GitHub repository Actions tab for deployment status

## Security Best Practices

1. **Regularly rotate** your GitHub PAT
2. **Use environment variables** for sensitive data
3. **Monitor** your AWS usage and costs
4. **Set up CloudWatch alarms** for unusual activity
5. **Review** generated repositories before sharing publicly

## Cost Considerations

- **AWS Lambda**: Usually free under AWS Free Tier limits
- **API Gateway**: Pay per request (very low cost for personal use)  
- **GitHub Pages**: Free for public repositories
- **hCaptcha**: Free tier available

Expected monthly cost for typical usage: **$0-5 USD**