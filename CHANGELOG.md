# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial AWS SAM template with Lambda functions
- API Gateway with CORS configuration 
- S3 bucket for user documents with CloudFront-ready configuration
- GitHub Actions CI/CD pipeline
- Environment-based deployment (dev/main)
- Automatic changelog generation

### Changed
- Lambda runtime upgraded to Python 3.13
- Database credentials management via environment variables

### Fixed
- S3 bucket ARN reference in IAM policies
- CloudFormation stack rollback handling

## [0.1.0] - 2025-08-14

### Added
- Initial project setup
