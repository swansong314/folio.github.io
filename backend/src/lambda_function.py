import json
import base64
import os
import logging
import time
from github import Github
from github.GithubException import GithubException
from github import InputGitTreeElement
import requests

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

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

def generate_config_content(name, email, alt_email, phone1, phone2, bio, links, username, repo_name):
    """Generate Jekyll _config.yml with enhanced user data"""
    config = f"""title: {name}
email: {email}
description: {bio}
url: "https://{repo_name}"
baseurl: ""

# Build settings
markdown: kramdown
theme: minima
plugins:
  - jekyll-feed

# Social links
github_username: {username}"""
    
    # Add alternative email if provided
    if alt_email:
        config += f"\nalt_email: {alt_email}"
    
    # Add phone numbers if provided
    if phone1:
        config += f"\nphone: {phone1}"
    if phone2:
        config += f"\nalt_phone: {phone2}"
    
    # Add professional links
    if links:
        config += "\n\n# Professional Links"
        for link in links:
            if link.get('type') and link.get('url'):
                config += f"\n{link['type']}_url: {link['url']}"
    
    return config

def generate_index_content(name, bio, projects, experience, education, achievements):
    """Generate Jekyll index.md with enhanced user data"""
    content = "---\nlayout: home\n---\n\n"
    
    if bio:
        content += f"{bio}\n\n"
    
    # Projects section
    if projects:
        content += "## Projects\n\n"
        for project in projects:
            if project.get('title'):
                content += f"### {project['title']}\n\n"
                if project.get('description'):
                    content += f"{project['description']}\n\n"
                if project.get('technologies'):
                    content += f"**Technologies:** {project['technologies']}\n\n"
                if project.get('link'):
                    content += f"[View Project]({project['link']})\n\n"
                content += "---\n\n"
    
    # Experience section
    if experience:
        content += "## Experience\n\n"
        for exp in experience:
            if exp.get('title') and exp.get('company'):
                content += f"### {exp['title']} at {exp['company']}\n\n"
                if exp.get('duration'):
                    content += f"**Duration:** {exp['duration']}\n\n"
                if exp.get('description'):
                    content += f"{exp['description']}\n\n"
                content += "---\n\n"
    
    # Education section
    if education:
        content += "## Education\n\n"
        for edu in education:
            if edu.get('qualification') and edu.get('institution'):
                content += f"### {edu['qualification']}\n\n"
                content += f"**Institution:** {edu['institution']}\n\n"
                if edu.get('year'):
                    content += f"**Year:** {edu['year']}\n\n"
                content += "---\n\n"
    
    # Achievements section
    if achievements:
        content += "## Achievements\n\n"
        for achievement in achievements:
            if achievement.get('title'):
                content += f"### {achievement['title']}\n\n"
                if achievement.get('description'):
                    content += f"{achievement['description']}\n\n"
                content += "---\n\n"
    
    return content

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
    # Wrap everything in a try-catch to ensure CORS headers are always returned
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Handle CORS preflight requests
        if event.get('httpMethod') == 'OPTIONS':
            logger.info("Handling OPTIONS request")
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type, X-Amz-Date, Authorization, X-Api-Key, X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': ''
            }
        
        return handle_post_request(event, context)
    
    except Exception as e:
        logger.error(f"Fatal exception in lambda_handler: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }

def handle_post_request(event, context):
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
        alt_email = data.get('altEmail', '')
        phone1 = data.get('phone1', '')
        phone2 = data.get('phone2', '')
        bio = data.get('bio', '')
        links = data.get('links', [])
        projects = data.get('projects', [])
        experience = data.get('experience', [])
        education = data.get('education', [])
        achievements = data.get('achievements', [])
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
        try:
            logger.info("Authenticating with GitHub")
            g = Github(github_pat)
            user = g.get_user()
            username = user.login
            logger.info(f"Successfully authenticated as user: {username}")
        except GithubException as e:
            logger.error(f"GitHub authentication failed: {e.status} - {e.data}")
            if e.status == 401:
                error_message = "Invalid GitHub Personal Access Token. Please check your token."
            elif e.status == 403:
                error_message = "GitHub API rate limit exceeded or insufficient token permissions."
            else:
                error_message = f"GitHub authentication error: {e.data.get('message', str(e)) if hasattr(e, 'data') and e.data else str(e)}"
            
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS'
                },
                'body': json.dumps({'error': error_message})
            }

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

        # Load and customize all template files
        config_content = generate_config_content(name, email, alt_email, phone1, phone2, bio, links, username, repo_name)
        index_content = generate_index_content(name, bio, projects, experience, education, achievements)

        workflow_content = load_template_file('.github/workflows/deploy.yml')
        gemfile_content = load_template_file('Gemfile')

        repo.create_file(
            path='_config.yml',
            message='Add Jekyll config file',
            content=config_content,
            branch='main'
        )
        repo.create_file(
            path='index.md',
            message='Add portfolio index page',
            content=index_content,
            branch='main'
        )
        # OAuth app tokens and personal access tokens (classic) need the repo scope to use this endpoint. 
        # The workflow scope is also required in order to modify files in the .github/workflows directory.
        # repo.create_file(
        #     path='.github/workflows/deploy.yml', 
        #     message='Add GitHub Pages deployment workflow',
        #     content=workflow_content,
        #     branch='main'
        # )
        # not required if the repo is nanmed correctly for a pages build
        repo.create_file(
            path='Gemfile',
            message='Add Gemfile',
            content=gemfile_content,
            branch='main'
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
            logger.error(f"GitHub exception details - Status: {e.status}, Data: {e.data if hasattr(e, 'data') else 'No data'}, Full exception: {str(e)}")
            error_message = f"GitHub API error (status {e.status}): {e.data.get('message', str(e)) if hasattr(e, 'data') and e.data else str(e)}. Full exception: {str(e)} | Data: {e.data if hasattr(e, 'data') else 'No data'}"
        
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
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }