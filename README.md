# Portfolio Generator

An automated tool that enables users to generate, deploy, and host a personal portfolio website on GitHub Pages by simply filling out a form. The project uses a serverless backend on AWS with infrastructure managed as code (IaC).

## Project Structure

```
portfolio-generator/
├── .gitignore
├── README.md
├── backend/
│   ├── src/
│   │   └── lambda_function.py
│   ├── template.yaml
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   └── script.js
└── portfolio-template/
    ├── _config.yml
    ├── index.md
    ├── Gemfile
    └── .github/
        └── workflows/
            └── deploy.yml
```

## Technology Stack

- **Frontend**: Static HTML, CSS, JavaScript
- **Hosting (Frontend Tool)**: GitHub Pages
- **Backend**: AWS Lambda (Python 3.9+)
- **API**: AWS API Gateway (HTTP API)
- **IaC**: AWS SAM (Serverless Application Model)
- **CI/CD**: GitHub Actions
- **Portfolio Template**: Jekyll (due to its native GitHub Pages support)

## How It Works

1. **User Input**: Users fill out a simple web form with their name, email, bio, projects, and GitHub Personal Access Token
2. **API Call**: The form submits data to an AWS API Gateway endpoint
3. **Lambda Processing**: The Lambda function:
   - Authenticates with GitHub using the provided PAT
   - Creates a new `username.github.io` repository
   - Populates it with Jekyll configuration and content
   - Sets up GitHub Actions for automatic deployment
4. **GitHub Pages**: The repository is automatically deployed to GitHub Pages

## Deployment Instructions

### Prerequisites

- AWS CLI configured with appropriate permissions
- AWS SAM CLI installed
- Python 3.9+ installed

### Backend Deployment

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Build the SAM application:
   ```bash
   sam build
   ```

3. Deploy the application:
   ```bash
   sam deploy --guided
   ```

4. Note the API Gateway endpoint URL from the output

### Frontend Configuration

1. Open `frontend/script.js`
2. Replace `YOUR_API_GATEWAY_URL` with the actual API Gateway endpoint URL from the deployment
3. Open `frontend/index.html` in a web browser to test the application

## Usage

1. Open `frontend/index.html` in your web browser
2. Fill out the form with your information:
   - **Name**: Your full name
   - **Email**: Your email address
   - **Bio**: Brief description about yourself
   - **Projects**: List of your projects or achievements
   - **GitHub PAT**: Your GitHub Personal Access Token (with `repo` scope)
3. Click "Generate Portfolio"
4. Wait for the confirmation with links to your new repository and website

## GitHub Personal Access Token Setup

1. Go to [GitHub Settings → Personal access tokens](https://github.com/settings/tokens/new)
2. Click "Generate new token (classic)"
3. Give it a descriptive name
4. Select the **"repo"** scope (full control of private repositories)
5. Click "Generate token"
6. Copy the token and use it in the form

## Features

- **Automated Repository Creation**: Creates a new `username.github.io` repository
- **Jekyll Integration**: Uses Jekyll with GitHub Pages for easy styling and deployment
- **GitHub Actions**: Automatic deployment workflow setup
- **Customizable Content**: Populates the site with user-provided information
- **Error Handling**: Comprehensive error handling for common issues

## Security Notes

- GitHub PAT is only used for the API call and is not stored
- All repositories created are public (required for free GitHub Pages)
- CORS is enabled for cross-origin requests

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).