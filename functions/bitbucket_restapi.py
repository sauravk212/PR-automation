import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_credentials():
    """Get credentials from environment variables at runtime"""
    return {
        'username': os.getenv("BITBUCKET_USERNAME"),
        'access_token': os.getenv("BITBUCKET_APP_PASSWORD"),
        'workspace': os.getenv("WORKSPACE"),
        'repo_slug': os.getenv("REPO_SLUG")
    }

def create_pull_request(input_text: str, reviewer_uuids: list = None) -> str:
    # Get fresh credentials
    creds = get_credentials()
    if not all(creds.values()):
        return {"error": "Missing Bitbucket credentials. Please check your settings."}

    # Basic prompt: "Create a PR from feature/login to main titled 'Add login'"
    import re

    match = re.match(
        r".*from\s+(\S+)\s+to\s+(\S+)\s+titled\s+['\"](.+?)['\"]", input_text
    )
    if not match:
        return {
            "error": "Invalid PR description format"
        }

    source_branch, dest_branch, title = match.groups()

    url = f"https://api.bitbucket.org/2.0/repositories/{creds['workspace']}/{creds['repo_slug']}/pullrequests"
    headers = {
        "Authorization": f"Bearer {creds['access_token']}",
        "Content-Type": "application/json",
    }
    
    # Convert reviewer UUIDs to the format expected by Bitbucket API
    reviewers = [{"uuid": uuid} for uuid in (reviewer_uuids or [])]
    
    payload = {
        "title": title,
        "source": {"branch": {"name": source_branch}},
        "destination": {"branch": {"name": dest_branch}},
        "description": f"PR created by agent for {title}.",
        "reviewers": reviewers
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 201:
        return response.json()
    else:
        error_data = response.json()
        # Make Bitbucket error messages more user-friendly
        if 'error' in error_data:
            error_message = error_data['error'].get('fields', {})
            for field_list in error_message.values():
                if any('branch not found' in field for field in field_list):                
                    return {
                    "error": "Branch not found",
                    "details": {
                        "message": "One or both of the branches you specified doesn't exist.",
                        "branches": {
                            "source": source_branch,
                            "destination": dest_branch
                        },
                        "tip": "Please check that both branch names are correct and try again."
                    }
                }
                elif any('already exists' in field for field in field_list):
                    return {
                    "error": "Pull request already exists",
                    "details": {
                        "message": "A pull request between these branches already exists.",
                        "branches": {
                            "source": source_branch,
                            "destination": dest_branch
                        },
                        "tip": "You might want to check existing pull requests or use different branches."
                    }
                }
        
        return {
            "error": "Failed to create PR",
            "details": error_data
        }

def get_workspace_members():
    # Get fresh credentials
    creds = get_credentials()
    if not all(creds.values()):
        return []

    url = f"https://api.bitbucket.org/2.0/repositories/{creds['workspace']}/{creds['repo_slug']}/permissions-config/users"
    headers = {
        "Authorization": f"Bearer {creds['access_token']}",
        "Content-Type": "application/json",
    }
    
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        # Filter out the current user based on username
        users = [
            {
                "display_name": user["user"]["display_name"],
                "uuid": user["user"]["uuid"],
                "permission": user["permission"],
            }
            for user in data.get("values", [])
        ]
        
        return users
    else:
        print(f"❌ Error {response.status_code}: {response.text}")
        return []