# Security Policy for Sefaria Discord Bot

## Overview
This document outlines the security practices and considerations for the Sefaria Discord Bot project.

## Security Measures Implemented

### 1. Environment Variable Management
- **Discord Token**: Stored in `DISCORD_TOKEN` environment variable
- **OpenAI API Key**: Stored in `OPENAI_API_KEY` environment variable  
- **NLI API Key**: Can be overridden with `NLI_API_KEY` environment variable
- **No hardcoded credentials** in source code (except fallback guest key for NLI)

### 2. Access Control
- **Admin Commands**: Restricted to users with administrator permissions
- **Guild-specific Settings**: Auto-reply can be controlled per Discord server
- **Permission Checks**: Implemented for sensitive operations

### 3. Rate Limiting
- **API Rate Limits**: Implemented across all external API clients
- **Request Throttling**: 1-second delays between Sefaria API requests
- **Session Management**: Proper connection pooling and cleanup

### 4. Error Handling
- **Sensitive Data**: No API keys or tokens exposed in error messages
- **Graceful Degradation**: Bot continues operating if individual APIs fail
- **Logging**: Structured logging without credential exposure

### 5. Input Validation
- **Command Parameters**: Basic validation on user inputs
- **SQL Injection Prevention**: No direct database queries (API-based only)
- **Content Filtering**: Discord's built-in content policies applied

## Security Best Practices

### Environment Setup
```bash
# Never commit these files
.env
.env.local
.env.production

# Use strong, unique tokens
DISCORD_TOKEN=your_actual_discord_bot_token
OPENAI_API_KEY=your_actual_openai_api_key
```

### Deployment Security
- Use environment variables for all secrets
- Enable SSL/TLS for web endpoints
- Run with minimal required permissions
- Regular security updates for dependencies

### Code Security
- No hardcoded credentials
- Proper error handling without information leakage  
- Rate limiting to prevent abuse
- Input sanitization for user commands

## Potential Security Considerations

### 1. API Dependencies
- **Sefaria API**: Public API, no authentication required
- **Hebcal API**: Public API, no authentication required
- **OpenAI API**: Requires API key, usage limits apply
- **NLI API**: Uses guest key by default, can be upgraded

### 2. Discord Permissions
The bot requests these permissions:
- Read message history
- Send messages  
- Use slash commands
- Add reactions
- Send direct messages

### 3. Data Handling
- **No Data Storage**: Bot doesn't store user messages or personal data
- **Temporary Processing**: Messages processed in memory only
- **API Responses**: Cached temporarily for rate limiting only

## Reporting Security Issues

If you discover a security vulnerability:

1. **Do NOT** create a public GitHub issue
2. Contact the maintainers directly
3. Include detailed information about the vulnerability
4. Allow reasonable time for fixes before public disclosure

## Security Checklist for Deployment

- [ ] All API keys stored in environment variables
- [ ] `.env` files excluded from version control
- [ ] SSL/TLS enabled for web endpoints
- [ ] Bot permissions minimized to required only
- [ ] Rate limiting enabled for all APIs
- [ ] Error handling doesn't expose sensitive data
- [ ] Dependencies updated to latest secure versions
- [ ] Monitoring and logging configured

## Regular Security Maintenance

- **Monthly**: Review and update dependencies
- **Quarterly**: Audit API key usage and permissions
- **Annually**: Review all security practices and update documentation

## Compliance Notes

This bot:
- Doesn't collect or store personal user data
- Uses only public APIs for Jewish text content
- Follows Discord's Terms of Service and Community Guidelines
- Respects rate limits of all external services

---

**Last Updated**: July 3, 2025
**Security Review**: Completed - Critical issues resolved