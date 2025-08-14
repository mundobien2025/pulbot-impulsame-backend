# Impulsame Backend

AWS SAM application for Impulsame microfinance platform.

## 🚀 Features

- **Serverless Architecture**: AWS Lambda + API Gateway
- **Multi-Environment**: Automatic deployment to dev/main environments
- **Database Integration**: MySQL with environment-specific credentials
- **File Storage**: S3 bucket with CloudFront-ready configuration
- **CI/CD Pipeline**: GitHub Actions with automatic changelog generation
- **CORS Support**: Configured for React frontend integration

## 📁 Project Structure

```
pulbot-impulsame-backend/
├── .github/workflows/          # GitHub Actions workflows
├── lambdas/                    # Lambda functions
│   └── users-register-post/    # User registration endpoint
├── layers/                     # Lambda layers (auto-generated)
├── template.yaml              # SAM template
├── samconfig.toml             # SAM configuration
├── package.json               # Version and changelog management
├── CHANGELOG.md               # Auto-generated changelog
└── README.md                  # This file
```

## 🛠️ Development

### Prerequisites

- AWS CLI configured
- AWS SAM CLI installed
- Python 3.13
- Git

### Local Development

```bash
# Build the application
sam build

# Start local API
sam local start-api

# Run tests
python -m pytest tests/ -v
```

### Deployment

Deployment is automatic via GitHub Actions:

- **Push to `dev` branch** → Deploys to development environment
- **Push to `main` branch** → Deploys to production environment + creates release

### Commit Convention

This project uses [Conventional Commits](https://www.conventionalcommits.org/) for automatic changelog generation:

```bash
# Feature
git commit -m "feat(users): add user registration endpoint"

# Bug fix  
git commit -m "fix(auth): resolve token validation issue"

# Documentation
git commit -m "docs(readme): update deployment instructions"

# Refactor
git commit -m "refactor(lambda): optimize database connection handling"

# CI/CD changes
git commit -m "ci(deploy): add automatic stack cleanup"

# Performance improvements
git commit -m "perf(lambda): reduce cold start time"
```

### Commit Types

- `feat:` ✨ New features
- `fix:` 🐛 Bug fixes
- `docs:` 📚 Documentation
- `style:` 💄 Code style (formatting, etc.)
- `refactor:` ♻️ Code refactoring
- `perf:` ⚡ Performance improvements
- `test:` 🧪 Tests
- `build:` 🏗️ Build system changes
- `ci:` 👷 CI/CD changes
- `chore:` 🔧 Maintenance tasks

## 🌍 Environments

### Development (`dev`)
- **API**: `https://[api-id].execute-api.us-east-1.amazonaws.com/dev/`
- **S3 Bucket**: `dev-impulsame-user-documents`
- **CloudFront**: `dev-impulsame-user-documents.pulbot.store`

### Production (`main`)
- **API**: `https://[api-id].execute-api.us-east-1.amazonaws.com/main/`
- **S3 Bucket**: `main-impulsame-user-documents`
- **CloudFront**: `main-impulsame-user-documents.pulbot.store`

## 📋 API Endpoints

### User Registration
```
POST /users/register
Content-Type: application/json

{
  "email": "user@example.com",
  "full_name": "John Doe",
  "ci": "V-12345678",
  "phone1": "+584141234567",
  "id_file": { "data": "base64...", "content_type": "application/pdf" },
  "rif_file": { "data": "base64...", "content_type": "application/pdf" }
}
```

## 🔧 Configuration

Environment variables are managed through GitHub Secrets:

- `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`
- `DEV_DB_HOST` / `DEV_DB_USER` / `DEV_DB_PASS` / `DEV_DB_NAME`
- `MAIN_DB_HOST` / `MAIN_DB_USER` / `MAIN_DB_PASS` / `MAIN_DB_NAME`

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed list of changes in each release.

## 🤝 Contributing

1. Create a feature branch from `dev`
2. Make your changes using conventional commits
3. Create a Pull Request to `dev`
4. After review and merge, changes will be automatically deployed

## 📄 License

MIT License - see LICENSE file for details.
