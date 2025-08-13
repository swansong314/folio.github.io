import json
import base64
import os
from github import Github
from github.GithubException import GithubException
import requests

def load_template_file(file_path):
    """Load a file from the bundled portfolio-template directory"""
    template_dir = '/opt/portfolio-template' if os.path.exists('/opt/portfolio-template') else './portfolio-template'
    full_path = os.path.join(template_dir, file_path)
    
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        # Fallback to hardcoded content if template file not found
        return get_fallback_content(file_path)

def get_fallback_content(file_path):
    """Fallback content if template files are not available"""
    fallbacks = {
        '_config.yml': '''title: Your Name
email: your.email@example.com
description: A brief description about yourself
url: "https://username.github.io"
baseurl: ""

# Build settings
markdown: kramdown
theme: minima
plugins:
  - jekyll-feed

# Social links
github_username: username''',
        'index.md': '''---
layout: home
---

# Welcome to My Portfolio

This is a brief introduction about myself and my work.

## Projects

Here are some of my notable projects:

- Project 1: Description of your first project
- Project 2: Description of your second project
- Project 3: Description of your third project''',
        'Gemfile': '''source "https://rubygems.org"

gem "github-pages", group: :jekyll_plugins
gem "jekyll-feed", "~> 0.12"

platforms :mingw, :x64_mingw, :mswin, :jruby do
  gem "tzinfo", ">= 1", "< 3"
  gem "tzinfo-data"
end

gem "wdm", "~> 0.1.1", :platforms => [:mingw, :x64_mingw, :mswin]
gem "http_parser.rb", "~> 0.6.0", :platforms => [:jruby]''',
        '.github/workflows/deploy.yml': '''name: Build and deploy Jekyll site to GitHub Pages

on:
  push:
    branches:
      - main

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Setup Ruby
        uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.1'
          bundler-cache: true
          cache-version: 0
      - name: Setup Pages
        id: pages
        uses: actions/configure-pages@v4
      - name: Build with Jekyll
        run: bundle exec jekyll build --baseurl "${{ steps.pages.outputs.base_path }}"
        env:
          JEKYLL_ENV: production
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4'''
    }
    return fallbacks.get(file_path, '')

def verify_captcha(captcha_token):
    """Verify hCaptcha token"""
    if not captcha_token:
        return False
    
    secret_key = os.environ.get('HCAPTCHA_SECRET_KEY')
    if not secret_key:
        return False
    
    try:
        response = requests.post('https://hcaptcha.com/siteverify', data={
            'secret': secret_key,
            'response': captcha_token
        })
        result = response.json()
        return result.get('success', False)
    except Exception:
        return False

def lambda_handler(event, context):
    # Handle CORS preflight requests
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type, X-Amz-Date, Authorization, X-Api-Key, X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': ''
        }
    
    try:
        # Parse the request body
        if 'body' in event:
            if event.get('isBase64Encoded', False):
                body = base64.b64decode(event['body']).decode('utf-8')
            else:
                body = event['body']
            
            data = json.loads(body)
        else:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({'error': 'Missing request body'})
            }

        # Extract form data
        github_pat = data.get('github_pat')
        name = data.get('name', '')
        email = data.get('email', '')
        bio = data.get('bio', '')
        projects = data.get('projects', '')
        captcha_token = data.get('captcha_token')
        
        # Verify CAPTCHA first
        if not verify_captcha(captcha_token):
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({'error': 'Invalid CAPTCHA. Please try again.'})
            }

        if not github_pat:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({'error': 'GitHub PAT is required'})
            }

        # Authenticate with GitHub
        g = Github(github_pat)
        user = g.get_user()
        username = user.login

        # Create repository name
        repo_name = f"{username}.github.io"

        try:
            # Check if repository already exists
            existing_repo = user.get_repo(repo_name)
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({'error': f'Repository {repo_name} already exists'})
            }
        except GithubException as e:
            if e.status != 404:
                raise e
            # Repository doesn't exist, which is what we want

        # Create new repository
        repo = user.create_repo(
            name=repo_name,
            description=f"Personal portfolio website for {name}",
            homepage=f"https://{repo_name}",
            private=False,
            auto_init=True
        )

        # Load and customize _config.yml from template
        config_content = load_template_file('_config.yml')
        config_content = config_content.replace('Your Name', name)
        config_content = config_content.replace('your.email@example.com', email)
        config_content = config_content.replace('A brief description about yourself', bio)
        config_content = config_content.replace('"https://username.github.io"', f'"https://{repo_name}"')
        config_content = config_content.replace('github_username: username', f'github_username: {username}')

        # Create and commit _config.yml
        repo.create_file(
            "_config.yml",
            "Initial configuration",
            config_content
        )

        # Load and customize index.md from template
        index_content = load_template_file('index.md')
        index_content = index_content.replace('Welcome to My Portfolio', f"Welcome to {name}'s Portfolio")
        index_content = index_content.replace('This is a brief introduction about myself and my work.', bio)
        index_content = index_content.replace('Here are some of my notable projects:\n\n- Project 1: Description of your first project\n- Project 2: Description of your second project\n- Project 3: Description of your third project', projects)

        repo.create_file(
            "index.md",
            "Add homepage content",
            index_content
        )

        # Load GitHub Actions workflow from template
        workflow_content = load_template_file('.github/workflows/deploy.yml')

        # Create .github/workflows directory and workflow file
        repo.create_file(
            ".github/workflows/deploy.yml",
            "Add GitHub Pages deployment workflow",
            workflow_content
        )

        # Load Gemfile from template
        gemfile_content = load_template_file('Gemfile')

        repo.create_file(
            "Gemfile",
            "Add Jekyll dependencies",
            gemfile_content
        )

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({
                'message': 'Portfolio repository created successfully!',
                'repository_url': repo.html_url,
                'pages_url': f"https://{repo_name}"
            })
        }

    except GithubException as e:
        # Enhanced error handling for specific GitHub errors
        if e.status == 401:
            error_message = "Invalid GitHub Personal Access Token. Please check your token and ensure it has the required permissions."
        elif e.status == 403:
            error_message = "GitHub API rate limit exceeded or insufficient permissions. Please try again later."
        elif e.status == 422 and 'name already exists' in str(e.data):
            error_message = f"Repository {data.get('name', 'unknown')}.github.io already exists in your account."
        else:
            error_message = f"GitHub API error: {e.data.get('message', str(e)) if hasattr(e, 'data') and e.data else str(e)}"
        
        return {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({'error': error_message})
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }