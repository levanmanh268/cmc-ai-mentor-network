# Security Policy

## Secrets

Never commit API keys, tokens, passwords, or private credentials to this repository.

Use a local `.env` file and keep only placeholders in `.env.example`.

## Credential exposure response

A Groq API credential was previously committed to this public repository. Removing it from the latest files does not invalidate copies that may still exist in Git history.

The repository owner should immediately:

1. Revoke or rotate the exposed Groq API key in the Groq console.
2. Put the replacement key only in a local `.env` file.
3. Never paste a live credential into issues, commits, pull requests, screenshots, or chat logs.
4. Consider rewriting Git history if the repository must no longer contain the old secret.

## Reporting

For classroom use, report a suspected vulnerability through a private message to the project leader instead of posting live secrets in a public issue.
