#!/usr/bin/env python3

import os
import sys
import json
from datetime import datetime, timedelta, time as time_obj, timezone
from git import Repo
import requests
from typing import Dict

# My work GitHub: https://github.com/nmcgrady
WORK_GITHUB_USERNAME = 'nmcgrady'
PERSONAL_GITHUB_TOKEN = os.getenv('PERSONAL_GITHUB_TOKEN', '')
REPO_PATH = '.'
DAYS_BACK = 1 

def get_work_account_contributions_graphql(username: str, token: str, days_back: int = None) -> Dict:
    contributions = {}
    end_date = datetime.now()
    
    if days_back:
        start_date = end_date - timedelta(days=days_back)
        from_date = start_date.strftime('%Y-%m-%dT00:00:00Z')
    else:
        start_date = end_date - timedelta(days=365)
        from_date = start_date.strftime('%Y-%m-%dT00:00:00Z')
    
    to_date = end_date.strftime('%Y-%m-%dT23:59:59Z')
    
    query = """
    query($username: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $username) {
        contributionsCollection(from: $from, to: $to) {
          contributionCalendar {
            weeks {
              contributionDays {
                date
                contributionCount
              }
            }
          }
        }
      }
    }
    """
    
    headers = {
        'Authorization': f'bearer {token}',
        'Content-Type': 'application/json',
        'User-Agent': 'ContributionSync/1.0'
    }
    
    variables = {
        'username': username,
        'from': from_date,
        'to': to_date
    }
    
    try:
        response = requests.post(
            'https://api.github.com/graphql',
            headers=headers,
            json={'query': query, 'variables': variables},
            timeout=30
        )
        
        if response.status_code != 200:
            return contributions
        
        data = response.json()
        
        if 'errors' in data:
            return contributions
        
        if 'data' not in data or not data['data']['user']:
            return contributions
        
        calendar = data['data']['user']['contributionsCollection']['contributionCalendar']
        for week in calendar.get('weeks', []):
            for day in week.get('contributionDays', []):
                date_str = day.get('date', '')
                count = day.get('contributionCount', 0)
                
                if date_str and count > 0:
                    date_obj = datetime.fromisoformat(date_str).date()
                    contributions[date_obj] = count

        return contributions
        
    except Exception:
        return contributions

def get_existing_commits(repo):
    existing_commits = {}
    
    for commit in repo.iter_commits('HEAD'):
        commit_date = commit.committed_datetime.date()
        if commit_date not in existing_commits:
            existing_commits[commit_date] = 0
        existing_commits[commit_date] += 1
    
    return existing_commits

def create_commits_for_date(repo, date, count):
    data_file = 'contributions.json'
    
    data = {}
    if os.path.exists(data_file):
        try:
            with open(data_file, 'r') as f:
                content = f.read()
                json_end = content.find('\n#')
                if json_end != -1:
                    content = content[:json_end]
                data = json.loads(content) if content.strip() else {}
        except (json.JSONDecodeError, ValueError):
            data = {}
    
    date_str = date.isoformat()
    if date_str not in data:
        data[date_str] = 0
    data[date_str] = max(data[date_str], count)
    
    # Calculate time interval to distribute commits evenly throughout the day
    total_seconds = 24 * 60 * 60  # 24 hours in seconds
    interval_seconds = total_seconds // count if count > 0 else 0
    
    for i in range(count):
        data['_last_sync'] = f"{date_str}_{i+1}"
        
        with open(data_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        repo.index.add([data_file])
        
        # Distribute commits evenly throughout the day
        seconds_since_midnight = i * interval_seconds
        hours = seconds_since_midnight // 3600
        minutes = (seconds_since_midnight % 3600) // 60
        seconds = seconds_since_midnight % 60
        
        commit_time = datetime.combine(date, time_obj(hour=hours, minute=minutes, second=seconds)).replace(tzinfo=timezone.utc)
        repo.index.commit(
            f'Sync contribution for {date_str}',
            author_date=commit_time,
            commit_date=commit_time
        )

def main():
    if not PERSONAL_GITHUB_TOKEN:
        sys.exit(1)
    
    repo = Repo(REPO_PATH)
    
    existing_commits = get_existing_commits(repo)
    
    work_contributions = get_work_account_contributions_graphql(WORK_GITHUB_USERNAME, PERSONAL_GITHUB_TOKEN, DAYS_BACK)
    
    new_commits = 0
    for date, target_count in work_contributions.items():
        existing_count = existing_commits.get(date, 0)
        needed_count = max(0, target_count - existing_count)
        
        if needed_count > 0:
            create_commits_for_date(repo, date, needed_count)
            new_commits += needed_count
    

if __name__ == '__main__':
    main()
