# GitHub Contribution Mirror

This repository automatically mirrors my GitHub contribution activity from my work account [nmcgrady](https://github.com/nmcgrady) to my personal profile.

## How It Works

Every day at 8AM UTC (2AM CST), a GitHub Actions workflow runs a Python script that:

1. **Fetches Contribution Data**: Uses GitHub's GraphQL API to retrieve contribution counts from my work account (`@nmcgrady`)
2. **Creates Mirror Commits**: Generates commits in this repository with timestamps matching the contribution dates
3. **Tracks State**: Maintains a `contributions.json` file to track sync progress

## Technical Details

- **Language**: Python 3.11+
- **Dependencies**: GitPython, requests
- **API**: GitHub GraphQL API v4
- **Automation**: GitHub Actions (daily cron job)
- **Data Storage**: JSON file for tracking sync state

## Repository Structure

- `sync_contributions.py` - Main synchronization script
- `contributions.json` - Tracks contribution data and sync state
- `.github/workflows/sync-contributions.yml` - GitHub Actions workflow
- `requirements.txt` - Python dependencies

## Why This Approach?

I maintain separate GitHub accounts for personal and work activities to keep my professional and personal development work clearly separated. However, I want my personal GitHub profile to serve as the comprehensive record of all my development activity.

By using separate accounts:

- **Professional separation**: Work contributions stay on the work account
- **Personal branding**: My personal profile shows my complete development journey
- **Privacy boundaries**: Work-specific code and projects remain separate

## Transparency and Verification

Making this synchronization code public serves three important purposes:

1. **Accountability**: Anyone can verify that my personal contribution graph accurately reflects contributions from my other accounts
2. **Trust**: The code demonstrates that I'm not artificially inflating my contribution counts - every commit corresponds to real development work done elsewhere
3. **Open source**: Others can learn from and potentially adapt this approach for their own needs

## Purpose

This setup allows me to maintain a consistent contribution graph across multiple GitHub accounts while respecting platform guidelines and maintaining complete transparency about my development activity.
