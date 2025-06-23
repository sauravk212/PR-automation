# PR Creation Assistant

A web application that helps automate and streamline the pull request creation process for Bitbucket repositories.

## Live Demo
The application is deployed and accessible at: https://pr-automation-test.onrender.com/

## Features

- **Easy PR Creation**: Create pull requests with a simple text input describing your changes
- **Reviewer Selection**: Easily select reviewers from your workspace members with a visual interface
- **Settings Management**: Configure your Bitbucket credentials and repository settings
- **Real-time Feedback**: Get immediate feedback on PR creation status with error handling
- **Responsive Design**: Works seamlessly across different device sizes

## Getting Started

1. Visit the [PR Creation Assistant](https://pr-automation-test.onrender.com/)
2. Configure your Bitbucket settings:
   - Bitbucket Username
   - App Password (Generate from Bitbucket Repository settings → Security → Access Tokens)
   - Workspace Name
   - Repository Slug

3. Once configured, you can:
   - Select reviewers from your workspace members
   - Enter your PR description
   - Create PRs with a single click

## Usage

1. Enter your PR description in the format:
   ```
   Create a PR from <your source branch> to <target branch> titled <PR title here>
   ```
2. Select desired reviewers from the workspace members grid
3. Click "Create Pull Request"
4. Once created, you'll receive a link to view your new PR

## Security

- Credentials are securely stored in MongoDB Atlas
- All connections use TLS encryption
- App passwords are required instead of personal credentials

## Support

For any issues or questions, please create an issue in this repository.