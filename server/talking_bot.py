import os
from dotenv import load_dotenv
import json
import asyncio
import aiohttp
import requests
import nltk
from playsound import playsound
import tempfile
import traceback
import re
import sounddevice as sd
import numpy as np
from nltk.tokenize import word_tokenize
import wave
from datetime import datetime
from typing import Dict, List, Optional, Any
from jira import JIRA
import groq

# Load environment variables
load_dotenv()

# Get environment variables
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_KEY = os.getenv("JIRA_API_KEY")
JIRA_BASE_URL = "https://think41-team21.atlassian.net"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize Groq client
groq_client = groq.AsyncGroq(
    api_key=GROQ_API_KEY
)

# Download NLTK data
nltk.download('punkt')

class ScrumStatus:
    TODO = "To Do"
    IN_PROGRESS = "In Progress"
    DONE = "Done"
    BLOCKED = "Blocked"

class JiraAPI:
    def __init__(self, server_url, email, api_key):
        """Initialize the Jira API client
        
        Args:
            server_url (str): Jira server URL (e.g. https://your-domain.atlassian.net)
            email (str): Jira account email
            api_key (str): Jira API key
        """
        # Ensure server_url doesn't end with a slash
        self.server_url = server_url.rstrip('/')
        self.email = email
        self.api_key = api_key
        self.auth = (email, api_key)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        print(f"[DEBUG] Initialized Jira API with server URL: {server_url}")

    def get_account_id(self, email):
        """Get the account ID for a user by email"""
        print(f"[DEBUG] Getting account ID for email: {email}")
        try:
            url = f"{self.server_url}/rest/api/3/user/search?query={email}"
            print(f"[DEBUG] URL: {url}")
            print(f"[DEBUG] Headers: {self.headers}")
            print(f"[DEBUG] Auth: {self.auth}")
            
            response = requests.get(url, headers=self.headers, auth=self.auth)
            print(f"[DEBUG] Response status: {response.status_code}")
            print(f"[DEBUG] Response content: {response.text}")
            
            if response.status_code == 200:
                users = response.json()
                if users:
                    for user in users:
                        if user.get('emailAddress') == email:
                            account_id = user['accountId']
                            print(f"[DEBUG] Found account ID: {account_id}")
                            return account_id
            print("[DEBUG] No account ID found")
            return None
        except Exception as e:
            print(f"[ERROR] Error getting account ID: {str(e)}")
            traceback.print_exc()
            return None

    def get_account_id(self, username):
        """Get the account ID for a username"""
        print(f"[DEBUG] Getting account ID for username: {username}")
        try:
            url = f"{self.server_url}/rest/api/3/user/search?query={username}"
            print(f"[DEBUG] URL: {url}")
            print(f"[DEBUG] Headers: {self.headers}")
            print(f"[DEBUG] Auth: {self.auth}")
            
            response = requests.get(url, headers=self.headers, auth=self.auth)
            print(f"[DEBUG] Response status: {response.status_code}")
            print(f"[DEBUG] Response content: {response.text}")
            
            if response.status_code == 200:
                users = response.json()
                if users:
                    account_id = users[0]['accountId']
                    print(f"[DEBUG] Found account ID: {account_id}")
                    return account_id
            print("[DEBUG] No account ID found")
            return None
        except Exception as e:
            print(f"[ERROR] Error getting account ID: {str(e)}")
            traceback.print_exc()
            return None
        
    def get_todo_tasks(self, assignee):
        """Get TODO tasks for the given assignee"""
        print("[DEBUG] Fetching TODO tasks...")
        print(f"[DEBUG] Server URL: {self.server_url}")
        print(f"[DEBUG] Headers: {self.headers}")
        
        url = f"{self.server_url}/rest/api/3/search"
        
        # First get the account ID
        account_id = self.get_account_id(assignee)
        if not account_id:
            print("[ERROR] Could not find account ID")
            return []
            
        print(f"[DEBUG] Found account ID: {account_id}")
        
        try:
            payload = {
                "jql": f'project = {os.getenv("JIRA_PROJECT_KEY")} AND status = "To Do" AND assignee = "{account_id}"',
                "fields": ["summary", "status", "assignee"]
            }
            print(f"[DEBUG] Request payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(
                url,
                headers=self.headers,
                auth=self.auth,
                json=payload
            )
            print(f"[DEBUG] Response status: {response.status_code}")
            print(f"[DEBUG] Response content: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                tasks = []
                for issue in data.get('issues', []):
                    task = {
                        'key': issue['key'],
                        'summary': issue['fields']['summary'],
                        'status': issue['fields']['status']['name']
                    }
                    tasks.append(task)
                print(f"[DEBUG] Found {len(tasks)} TODO tasks")
                return tasks
            else:
                print(f"[ERROR] Failed to fetch TODO tasks: {response.status_code}")
                return []
        except Exception as e:
            print(f"[ERROR] Error fetching TODO tasks: {str(e)}")
            traceback.print_exc()
            return []
        
    def create_issue(self, project, summary, description, issue_type):
        """Create a new issue in Jira
        
        Args:
            project (str): Project key (e.g., 'SCRUM')
            summary (str): Issue title/summary
            description (str): Detailed description of the issue
            issue_type (str): Type of issue (e.g., 'Task', 'Bug', 'Story')
            
        Returns:
            tuple: (success, message) where success is a boolean and message contains
                   either the created issue key or error message
        """
        print(f"\n[DEBUG] Creating issue with parameters:")
        print(f"Project: {project}")
        print(f"Summary: {summary}")
        print(f"Description: {description}")
        print(f"Issue Type: {issue_type}")
        try:
            # First, get the issue type ID
            issuetypes_url = f"{self.server_url}/rest/api/3/issuetype"
            print(f"\n[DEBUG] Fetching issue types from: {issuetypes_url}")
            issuetypes_response = requests.get(
                issuetypes_url,
                headers=self.headers,
                auth=self.auth
            )
            
            print(f"[DEBUG] Issue types response status: {issuetypes_response.status_code}")
            print(f"[DEBUG] Issue types response: {issuetypes_response.text}")
            
            if issuetypes_response.status_code != 200:
                return False, f"Failed to get issue types: {issuetypes_response.text}"
                
            issuetypes = issuetypes_response.json()
            print(f"\n[DEBUG] Available issue types:")
            for t in issuetypes:
                print(f"  - {t['name']} (ID: {t['id']})")
                
            print(f"\n[DEBUG] Looking for issue type: {issue_type}")
            issuetype_id = next((t["id"] for t in issuetypes if t["name"].lower() == issue_type.lower()), None)
            print(f"[DEBUG] Found issue type ID: {issuetype_id}")
            
            if not issuetype_id:
                return False, f"Issue type '{issue_type}' not found. Available types: {', '.join(t['name'] for t in issuetypes)}"
            
            create_url = f"{self.server_url}/rest/api/3/issue"
            
            # Format description in Atlassian Document Format
            description_adf = {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": description
                            }
                        ]
                    }
                ]
            }
            
            # Prepare the request payload
            payload = {
                "fields": {
                    "project": {
                        "key": project
                    },
                    "summary": summary,
                    "description": description_adf,
                    "issuetype": {
                        "id": issuetype_id
                    }
                }
            }
            
            print(f"\n[DEBUG] Creating issue with payload: {payload}")
            print(f"[DEBUG] Using URL: {create_url}")
            print(f"[DEBUG] Headers: {self.headers}")
            
            response = requests.post(
                create_url,
                headers=self.headers,
                auth=self.auth,
                json=payload
            )
            
            print(f"[DEBUG] Create issue response status: {response.status_code}")
            print(f"[DEBUG] Create issue response: {response.text}")
            
            if response.status_code == 201:
                data = response.json()
                return True, f"Created issue {data['key']}"
            else:
                return False, f"Failed to create issue: {response.text}"
                
        except Exception as e:
            print(f"[ERROR] Failed to create issue: {e}")
            traceback.print_exc()
            return False, str(e)
        
    def create_issue(self, project, summary, description, issue_type, assignee=None, epic_key=None):
        """Create a new issue in Jira"""
        try:
            create_url = f"{self.server_url}/rest/api/3/issue"
            
            issue_data = {
                "fields": {
                    "project": {"key": project},
                    "summary": summary,
                    "description": {
                        "type": "doc",
                        "version": 1,
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": description
                                    }
                                ]
                            }
                        ]
                    },
                    "issuetype": {"name": issue_type}
                }
            }
            
            if assignee:
                issue_data["fields"]["assignee"] = {"name": assignee}
                
            # If this is a story and epic is provided, link it to the epic
            if issue_type.lower() == "story" and epic_key:
                issue_data["fields"]["customfield_10014"] = epic_key  # Epic link field
            
            response = requests.post(
                create_url,
                headers=self.headers,
                auth=self.auth,
                json=issue_data
            )
            
            if response.status_code == 201:
                issue_key = response.json()["key"]
                print(f"[DEBUG] Created issue: {issue_key}")
                return True, issue_key
            else:
                print(f"[ERROR] Failed to create issue: {response.text}")
                return False, f"API Error: {response.text}"
                
        except Exception as e:
            print(f"[ERROR] Error creating issue: {str(e)}")
            return False, str(e)

    def get_epics(self, project_key):
        """Get list of epics in the project"""
        try:
            # Search for epics using JQL
            search_url = f"{self.server_url}/rest/api/3/search"
            jql = f'project = {project_key} AND issuetype = Epic ORDER BY created DESC'
            
            response = requests.post(
                search_url,
                headers=self.headers,
                auth=self.auth,
                json={
                    "jql": jql,
                    "fields": ["summary", "customfield_10014"]  # Epic Name field
                }
            )
            
            if response.status_code == 200:
                epics = response.json()["issues"]
                return True, epics
            else:
                print(f"[ERROR] Failed to get epics: {response.text}")
                return False, []
                
        except Exception as e:
            print(f"[ERROR] Error getting epics: {str(e)}")
            return False, []

    def get_project_summary(self, project_key="SCRUM"):
        """Get a comprehensive project summary including epics, stories, and tasks."""
        try:
            # Get project details
            project_url = f"{self.server_url}/rest/api/2/project/{project_key}"
            project_response = requests.get(project_url, headers=self.headers, auth=self.auth)
            project_data = project_response.json()
            
            # Get all epics
            epic_jql = f'project = {project_key} AND issuetype = Epic ORDER BY created DESC'
            epics_url = f"{self.server_url}/rest/api/2/search"
            epics_response = requests.get(
                epics_url,
                headers=self.headers,
                auth=self.auth,
                params={"jql": epic_jql, "maxResults": 100}
            )
            epics_data = epics_response.json()
            print(f"\n[DEBUG] Found {len(epics_data.get('issues', []))} epics")
            
            # Prepare summary data
            summary = {
                "projectName": project_data.get("name"),
                "projectKey": project_key,
                "lastUpdated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "epics": []
            }
            
            # Process each epic
            for epic in epics_data.get("issues", []):
                epic_key = epic.get("key")
                epic_fields = epic.get("fields", {})
                print(f"\n[DEBUG] Processing epic {epic_key}: {epic_fields.get('summary')}")
                
                # Get stories under this epic
                stories_jql = f'project = {project_key} AND issuetype = Story AND "Epic Link" ~ "{epic_key}"'
                print(f"[DEBUG] Stories JQL: {stories_jql}")
                
                stories_response = requests.get(
                    f"{self.server_url}/rest/api/2/search",
                    headers=self.headers,
                    auth=self.auth,
                    params={
                        "jql": stories_jql,
                        "maxResults": 100,
                        "fields": ["summary", "status", "assignee", "priority", "updated", "customfield_10014", "issuetype"]
                    }
                )
                
                if stories_response.status_code != 200:
                    print(f"[ERROR] Error getting stories: {stories_response.text}")
                    continue
                    
                stories_data = stories_response.json()
                print(f"[DEBUG] Found {len(stories_data.get('issues', []))} stories for epic {epic_key}")
                
                # Process stories
                stories = []
                for story in stories_data.get("issues", []):
                    story_fields = story.get("fields", {})
                    assignee = story_fields.get("assignee", {})
                    
                    stories.append({
                        "key": story.get("key"),
                        "summary": story_fields.get("summary"),
                        "status": story_fields.get("status", {}).get("name"),
                        "assignee": assignee.get("displayName") if assignee else "Unassigned",
                        "priority": story_fields.get("priority", {}).get("name"),
                        "updated": story_fields.get("updated")
                    })
                
                # Add epic to summary
                epic_assignee = epic_fields.get("assignee", {})
                summary["epics"].append({
                    "key": epic_key,
                    "summary": epic_fields.get("summary"),
                    "status": epic_fields.get("status", {}).get("name"),
                    "assignee": epic_assignee.get("displayName") if epic_assignee else "Unassigned",
                    "progress": {
                        "total": len(stories),
                        "completed": len([s for s in stories if s["status"] == "Done"])
                    },
                    "stories": stories
                })
            
            print("\n[DEBUG] Final summary:", summary)
            return summary
        except Exception as e:
            print(f"[ERROR] Error getting project summary: {str(e)}")
            traceback.print_exc()
            return None

    def issue_exists(self, issue_key):
        """Check if an issue exists"""
        url = f"{self.server_url}/rest/api/3/issue/{issue_key}"
        try:
            print(f"[DEBUG] Checking if issue exists: {issue_key}")
            print(f"[DEBUG] URL: {url}")
            response = requests.get(url, headers=self.headers, auth=self.auth)
            print(f"[DEBUG] Response status: {response.status_code}")
            if response.status_code == 200:
                print(f"[DEBUG] Issue {issue_key} exists")
                return True
            else:
                print(f"[DEBUG] Issue {issue_key} does not exist")
                return False
        except Exception as e:
            print(f"[ERROR] Error checking issue existence: {str(e)}")
            traceback.print_exc()
            return False

    def get_issue_assignee(self, issue_key):
        """Get the assignee of an issue"""
        url = f"{self.server_url}/rest/api/3/issue/{issue_key}"
        response = requests.get(url, headers=self.headers, auth=self.auth)
        
        if response.status_code == 200:
            data = response.json()
            assignee = data.get("fields", {}).get("assignee", {})
            if assignee:
                return {
                    "accountId": assignee.get("accountId"),
                    "displayName": assignee.get("displayName")
                }
        return None

    def get_current_sprint_id(self):
        """Get the ID of the current active sprint"""
        try:
            board_url = f"{self.server_url}/rest/agile/1.0/board"
            boards = requests.get(
                board_url,
                headers=self.headers,
                auth=self.auth
            ).json()["values"]
            
            if not boards:
                return None
                
            board_id = boards[0]["id"]  # Use the first board
            
            # Get active sprints for this board
            sprints_url = f"{self.server_url}/rest/agile/1.0/board/{board_id}/sprint?state=active"
            sprints = requests.get(
                sprints_url,
                headers=self.headers,
                auth=self.auth
            ).json()["values"]
            
            if sprints:
                return sprints[0]["id"]  # Return the ID of the first active sprint
            return None
            
        except Exception as e:
            print(f"Error getting current sprint: {str(e)}")
            return None

    def create_blocker(self, issue_key, description):
        """Create a blocker relationship for the issue"""
        try:
            print(f"\n[DEBUG] Starting blocker creation for issue: {issue_key}")
            
            # First get the issue details to ensure it exists
            issue = self.get_issue_details(issue_key)
            if not issue:
                print(f"[ERROR] Could not find issue {issue_key}")
                return False, f"Could not find issue {issue_key}"

            print(f"[DEBUG] Found issue {issue_key}: {json.dumps(issue, indent=2)}")

            # Get the current sprint ID
            sprint_id = self.get_current_sprint_id()
            if not sprint_id:
                print("[WARNING] Could not determine current sprint ID")

            # Create a new issue for the blocker
            create_url = f"{self.server_url}/rest/api/3/issue"
            project_key = issue_key.split('-')[0]
            
            # Get assignee info for better formatting
            assignee_name = "Unassigned"
            if issue["fields"].get("assignee"):
                assignee_name = issue["fields"]["assignee"].get("displayName", "Unassigned")
            
            # Format the description with markdown
            formatted_description = f"""🚫 **Blocker Created for {issue_key}**  
- **Issue:** {description}  
- **Impact:** Blocking progress on {issue_key}  
- **Assigned To:** {assignee_name}  
- **Created On:** {datetime.now().strftime('%Y-%m-%d')}  

Please update this ticket with:
1. Root cause analysis
2. Proposed solution
3. Estimated time to resolution"""

            issue_data = {
                "fields": {
                    "project": {"key": project_key},
                    "summary": f"Blocker for {issue_key}: {description[:50]}{'...' if len(description) > 50 else ''}",
                    "description": {
                        "type": "doc",
                        "version": 1,
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": formatted_description
                                    }
                                ]
                            }
                        ]
                    },
                    "issuetype": {"name": "Task"},
                    "labels": ["blocked", "blocker"]
                }
            }
            
            # Add sprint if available
            if sprint_id:
                issue_data["fields"]["customfield_10020"] = sprint_id
            
            # Copy assignee if available
            if issue["fields"].get("assignee"):
                issue_data["fields"]["assignee"] = issue["fields"]["assignee"]
            
            print(f"[DEBUG] Sending create request with data: {json.dumps(issue_data, indent=2)}")
            
            create_response = requests.post(
                create_url,
                headers=self.headers,
                auth=self.auth,
                json=issue_data
            )
            
            print(f"[DEBUG] Create response status: {create_response.status_code}")
            print(f"[DEBUG] Create response body: {create_response.text}")
            
            if create_response.status_code != 201:
                print(f"[ERROR] Failed to create blocker issue: {create_response.text}")
                return False, "Failed to create blocker issue"
            
            blocker_key = create_response.json()["key"]
            
            # Create the "is blocked by" relationship
            link_url = f"{self.server_url}/rest/api/3/issueLink"
            link_data = {
                "type": {
                    "name": "Blocks"
                },
                "inwardIssue": {
                    "key": issue_key
                },
                "outwardIssue": {
                    "key": blocker_key
                }
            }
            
            print(f"[DEBUG] Sending link request with data: {json.dumps(link_data, indent=2)}")
            
            link_response = requests.post(
                link_url,
                headers=self.headers,
                auth=self.auth,
                json=link_data
            )
            
            print(f"[DEBUG] Link response status: {link_response.status_code}")
            print(f"[DEBUG] Link response body: {link_response.text}")
            
            if link_response.status_code != 201:
                print(f"[ERROR] Failed to create issue link: {link_response.text}")
            
            # Create a structured comment on the blocked issue
            comment_url = f"{self.server_url}/rest/api/3/issue/{issue_key}/comment"
            comment_text = f"""🚫 **Blocker Created:** [{blocker_key}]({self.server_url}/browse/{blocker_key})  
- **Issue:** {description}  
- **Created On:** {datetime.now().strftime('%Y-%m-%d')}  
- **Status:** Blocked  

This issue is blocked. Progress will resume once the blocker is resolved."""

            comment_data = {
                "body": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": comment_text
                                }
                            ]
                        }
                    ]
                }
            }
            
            print(f"[DEBUG] Sending comment request with data: {json.dumps(comment_data, indent=2)}")
            
            comment_response = requests.post(
                comment_url,
                headers=self.headers,
                auth=self.auth,
                json=comment_data
            )
            
            print(f"[DEBUG] Comment response status: {comment_response.status_code}")
            print(f"[DEBUG] Comment response body: {comment_response.text}")
            
            if comment_response.status_code != 201:
                print(f"[ERROR] Failed to add blocker comment: {comment_response.text}")
            
            # Update the blocked issue with the blocked label
            update_url = f"{self.server_url}/rest/api/3/issue/{issue_key}"
            update_data = {
                "fields": {
                    "labels": ["blocked"]
                }
            }
            
            update_response = requests.put(
                update_url,
                headers=self.headers,
                auth=self.auth,
                json=update_data
            )
            
            if update_response.status_code != 204:
                print(f"Failed to update issue with blocked label: {update_response.text}")
            
            return True, f"Created blocker {blocker_key} and linked it to {issue_key}"
            
        except Exception as e:
            print(f"Error creating blocker: {str(e)}")
            return False, f"Error creating blocker: {str(e)}"

    def test_connection(self):
        """Test the connection to Jira"""
        try:
            response = requests.get(
                f"{self.server_url}/rest/api/3/myself",
                headers=self.headers,
                auth=self.auth
            )
            if response.status_code == 200:
                print("[DEBUG] Successfully connected to Jira")
                print(f"[DEBUG] User info: {response.text}")
                return True
            else:
                print(f"[ERROR] Failed to connect to Jira. Status: {response.status_code}")
                print(f"[ERROR] Response: {response.text}")
                return False
        except Exception as e:
            print(f"[ERROR] Failed to connect to Jira: {e}")
            return False

    def get_issue_details(self, issue_key):
        """Get issue details including current status"""
        print(f"\n[DEBUG] Getting details for {issue_key}...")
        url = f"{self.server_url}/rest/api/3/issue/{issue_key}"
        try:
            print(f"[DEBUG] Using URL: {url}")
            response = requests.get(url, headers=self.headers, auth=self.auth)
            print(f"[DEBUG] Response status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                current_status = data['fields']['status']['name']
                print(f"[DEBUG] Current status: {current_status}")
                return data
            else:
                print(f"[ERROR] Failed to get issue: {response.status_code}")
                return None
        except Exception as e:
            print(f"[ERROR] Error getting issue details: {str(e)}")
            return None

    def update_issue_status(self, issue_key, target_status):
        """Update issue status using transition ID"""
        print(f"\n[DEBUG] Updating {issue_key} to {target_status}...")
        
        # Get current issue details
        issue = self.get_issue_details(issue_key)
        if not issue:
            return False, "Could not get issue details"
            
        current_status = issue['fields']['status']['name']
        if current_status == target_status:
            print(f"[DEBUG] Issue already in {target_status} status")
            return True, f"Issue already in {target_status} status"
        
        # Get transition ID
        transition_id = None
        response = requests.get(
            f"{self.server_url}/rest/api/3/issue/{issue_key}/transitions",
            headers=self.headers,
            auth=self.auth
        )
        if response.status_code == 200:
            transitions = response.json()["transitions"]
            for t in transitions:
                if t['name'] == target_status:
                    transition_id = t['id']
                    break
        
        if not transition_id:
            print(f"[ERROR] Invalid target status: {target_status}")
            return False, f"Invalid target status: {target_status}"
        
        # Execute the transition
        url = f"{self.server_url}/rest/api/3/issue/{issue_key}/transitions"
        payload = {
            "transition": {
                "id": transition_id
            }
        }
        
        try:
            print(f"[DEBUG] Sending transition request with data: {json.dumps(payload, indent=2)}")
            response = requests.post(url, headers=self.headers, auth=self.auth, json=payload)
            print(f"[DEBUG] Transition response status: {response.status_code}")
            if response.status_code == 204:
                print(f"[DEBUG] Successfully moved {issue_key} to {target_status}")
                return True, f"Updated {issue_key} to {target_status}"
            else:
                print(f"[ERROR] Failed to update status: {response.status_code}")
                if response.text:
                    print(f"Response: {response.text}")
                return False, f"Failed to update status: {response.status_code}"
        except Exception as e:
            print(f"[ERROR] Error updating status: {str(e)}")
            return False, f"Error updating status: {str(e)}"

class ScrumBot:
    def __init__(self, jira):
        self.jira = jira
        self.server_url = JIRA_BASE_URL
        self.auth = (JIRA_EMAIL, JIRA_API_KEY)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        self.current_state = "greeting"
        self.new_issue_data = {}  # Store new issue details
        self.scrum_data = {
            "yesterday": None,
            "today": None,
            "blockers": []
        }
        self.issue_creation_data = {
            "summary": None,
            "description": None,
            "issue_type": None,
            "priority": None,
            "assignee": None
        }
        self.issue_creation_state = None  # Track which field we're collecting
        self.username = "meghanathink41"  # Default username for getting tasks
        
    def get_todo_tasks(self, assignee):
        """Get TODO tasks for the given assignee"""
        print("[DEBUG] Fetching TODO tasks...")
        print(f"[DEBUG] Server URL: {self.server_url}")
        print(f"[DEBUG] Headers: {self.headers}")
        
        url = f"{self.server_url}/rest/api/3/search"
        
        # First get the account ID
        account_id = self.jira.get_account_id(assignee)
        if not account_id:
            print("[ERROR] Could not find account ID")
            return []
            
        print(f"[DEBUG] Found account ID: {account_id}")
        
        try:
            payload = {
                "jql": f'project = {os.getenv("JIRA_PROJECT_KEY")} AND status = "To Do" AND assignee = "{account_id}"',
                "fields": ["summary", "status", "assignee"]
            }
            print(f"[DEBUG] Request payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(
                url,
                headers=self.headers,
                auth=self.auth,
                json=payload
            )
            print(f"[DEBUG] Response status: {response.status_code}")
            print(f"[DEBUG] Response content: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                tasks = []
                for issue in data.get('issues', []):
                    task = {
                        'key': issue['key'],
                        'summary': issue['fields']['summary'],
                        'status': issue['fields']['status']['name']
                    }
                    tasks.append(task)
                print(f"[DEBUG] Found {len(tasks)} TODO tasks")
                return tasks
            else:
                print(f"[ERROR] Failed to fetch TODO tasks: {response.status_code}")
                return []
        except Exception as e:
            print(f"[ERROR] Error fetching TODO tasks: {str(e)}")
            traceback.print_exc()
            return []
        
    def start_conversation(self):
        """Start a new conversation with the bot
        
        Returns:
            dict: Contains message and speech_segments
        """
        self.current_state = "greeting"
        tasks = self.get_todo_tasks(self.username)
        
        if tasks:
            task_list = []
            for task in tasks:
                task_line = f"- {task['key']}: {task['summary']} ({task['status']})"
                task_list.append(task_line)
            
            tasks_text = "\n".join(task_list)
            message = f"Hi! I'm your Scrum Assistant. Let's start your daily standup.\n\nYour TODO tasks:\n{tasks_text}\n\nWhat did you work on yesterday?"
        else:
            message = "Hi! I'm your Scrum Assistant. Let's start your daily standup.\n\nYou don't have any TODO tasks assigned to you.\n\nWhat did you work on yesterday?"
        
        return {
            "message": message,
            "speech_segments": message.split('\n')
        }

    def extract_jira_key(self, text):
        """Extract Jira issue key from text."""
        try:
            print(f"\n[DEBUG] Extracting Jira key from: {text}")
            
            # Convert text to lowercase for processing
            text = text.lower()
            
            # First try to find number words
            number_mapping = {
                'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5',
                'six': '6', 'seven': '7', 'eight': '8', 'nine': '9', 'ten': '10',
                'eleven': '11', 'twelve': '12', 'thirteen': '13', 'fourteen': '14',
                'fifteen': '15', 'sixteen': '16', 'seventeen': '17', 'eighteen': '18',
                'nineteen': '19', 'twenty': '20'
            }
            
            # Replace number words with digits
            for word, digit in number_mapping.items():
                text = re.sub(r'\b' + word + r'\b', digit, text)
            
            print(f"[DEBUG] Text after number word replacement: {text}")
            
            # Now try to find exact matches like "scrum-7" or "scrum 7"
            patterns = [
                r'(?i)scrum[-\s]?(\d+)',  # Matches: scrum-7, scrum7, scrum 7
                r'(?i)think_41[-\s]?scrum[-\s]?(\d+)',  # Matches: think_41-scrum-7
                r'(?i)scrum\s+issue\s+(\d+)',  # Matches: scrum issue 7
                r'(?i)ticket\s+(\d+)',  # Matches: ticket 7
                r'(?i)issue\s+(\d+)'  # Matches: issue 7
            ]
            
            for pattern in patterns:
                print(f"[DEBUG] Trying pattern: {pattern}")
                matches = re.findall(pattern, text)
                print(f"[DEBUG] Pattern matches: {matches}")
                if matches:
                    key = f"{os.getenv('JIRA_PROJECT_KEY')}-{matches[0]}"
                    print(f"[DEBUG] Found key using pattern: {key}")
                    # Verify this issue exists in Jira
                    if self.jira.issue_exists(key):
                        print(f"[DEBUG] Verified issue exists in Jira: {key}")
                        return key
                    else:
                        print(f"[DEBUG] Issue does not exist in Jira: {key}")
            
            print("[DEBUG] No Jira key found")
            return None
            
        except Exception as e:
            print(f"[ERROR] Error extracting Jira key: {str(e)}")
            traceback.print_exc()
            return None

    def determine_status(self, text):
        """Determine task status based on user's response"""
        text = text.lower()
        print(f"\n[DEBUG] Analyzing status from text: {text}")
        
        # Check for completion words
        if any(word in text for word in ['completed', 'finished', 'done', 'complete']):
            print("[DEBUG] Detected status: Done")
            return ScrumStatus.DONE
            
        # Check for in-progress words
        elif any(word in text for word in ['working', 'started', 'progress', 'continuing', 'doing']):
            print("[DEBUG] Detected status: In Progress")
            return ScrumStatus.IN_PROGRESS
            
        # Check for blocked words
        elif any(word in text for word in ['blocked', 'blocking', 'blocker']):
            print("[DEBUG] Detected status: Blocked")
            return ScrumStatus.BLOCKED
            
        print("[DEBUG] Default status: To Do")
        return ScrumStatus.TODO

    def process_response(self, text):
        """Process user response based on current state."""
        try:
            print(f"\n[DEBUG] Processing response in state: {self.current_state}")
            print(f"[DEBUG] User text: {text}")
            
            # Normalize text for easier processing
            text = text.lower().strip()
            
            # Only extract Jira keys in relevant states
            issue_key = None
            if self.current_state in ["greeting", "today", "blocker_details"]:
                issue_key = self.extract_jira_key(text)
                print(f"[DEBUG] Extracted issue key: {issue_key}")
            
            if self.current_state == "greeting":
                # Extract Jira key and update status for yesterday's work
                if issue_key:
                    print(f"[DEBUG] Found Jira issue for yesterday: {issue_key}")
                    status = self.determine_status(text)
                    print(f"[DEBUG] Determined status: {status}")
                    success, message = self.jira.update_issue_status(issue_key, status)
                    if not success:
                        print(f"[ERROR] Failed to update status: {message}")
                    else:
                        print(f"[DEBUG] Successfully updated {issue_key} to {status}")
                
                self.scrum_data["yesterday"] = text
                self.current_state = "today"
                return "What will you be working on today?"
            
            elif self.current_state == "today":
                # Extract Jira key and update status for today's work
                if issue_key:
                    print(f"[DEBUG] Found Jira issue for today: {issue_key}")
                    status = self.determine_status(text)
                    if not status:
                        status = ScrumStatus.IN_PROGRESS  # Default to in progress for today's tasks
                    print(f"[DEBUG] Setting status to: {status}")
                    success, message = self.jira.update_issue_status(issue_key, status)
                    if not success:
                        print(f"[ERROR] Failed to update status: {message}")
                    else:
                        print(f"[DEBUG] Successfully updated {issue_key} to {status}")
                
                self.scrum_data["today"] = text
                self.current_state = "blockers"
                return "Do you have any blockers? (yes/no)"
            
            elif self.current_state == "blockers":
                # Simplified blocker state handling
                if text in ["no", "nope", "none", "no blockers"]:
                    self.current_state = "ask_create_issue"
                    return "Would you like to create any new issues/tickets? (yes/no)"
                elif text in ["yes", "yeah", "yep", "i do"]:
                    self.current_state = "blocker_details"
                    return "Please describe your blockers. If this is blocking a specific task, mention the task number (e.g., SCRUM-7 is blocked because...):"
                else:
                    return "Please answer with yes or no. Do you have any blockers?"
            
            elif self.current_state == "blocker_details":
                # Handle blocker details and create blocker issue if needed
                if issue_key:
                    print(f"[DEBUG] Found blocked Jira issue: {issue_key}")
                    success, message = self.jira.update_issue_status(issue_key, ScrumStatus.BLOCKED)
                    if not success:
                        print(f"[ERROR] Failed to update status to blocked: {message}")
                    else:
                        success, message = self.jira.create_blocker(issue_key, text)
                        if not success:
                            print(f"[ERROR] Failed to create blocker: {message}")
                
                self.scrum_data["blockers"].append(text)
                self.current_state = "more_blockers"
                return "Do you have any other blockers? (yes/no)"
            
            elif self.current_state == "more_blockers":
                if text in ["no", "nope", "none"]:
                    self.current_state = "ask_create_issue"
                    return "Would you like to create any new issues/tickets? (yes/no)"
                elif text in ["yes", "yeah", "yep", "i do"]:
                    self.current_state = "blocker_details"
                    return "Please describe your additional blockers:"
                else:
                    return "Please answer with yes or no. Do you have any other blockers?"
            
            elif self.current_state == "ask_create_issue":
                if text in ["yes", "y", "yeah", "sure"]:
                    # Reset issue creation data
                    self.issue_creation_data = {
                        "summary": None,
                        "description": None,
                        "issue_type": None,
                        "priority": None,
                        "assignee": None
                    }
                    self.issue_creation_state = "summary"
                    self.current_state = "issue_creation"
                    return "Let's create a new issue. What should be the summary (title) of the issue?"
                else:
                    # Show the TODO tasks again before ending
                    tasks = self.get_todo_tasks(self.username)
                    if tasks:
                        task_list = []
                        for task in tasks:
                            task_line = f"{task['key']}: {task['summary']} ({task['status']})"
                            task_list.append(task_line)
                        tasks_text = "\n".join(task_list)
                        return f"You have {len(tasks)} TODO task(s):\n{tasks_text}"
                    else:
                        return "You don't have any TODO tasks."
            
            return "I didn't understand that. Please try again."
            
        except Exception as e:
            print(f"[ERROR] Error in process_response: {str(e)}")
            traceback.print_exc()
            return "Sorry, I encountered an error. Please try again."

    def generate_summary(self):
        """Generate a natural, conversational standup summary that feels like a friendly chat."""
        try:
            # Get todo tasks for the user
            todo_tasks = self.get_todo_tasks(self.username)
            
            # Prepare summary parts
            summary_parts = []
            
            # Add todo tasks to summary if any exist
            if todo_tasks:
                task_list = [f"{task['key']}: {task['summary']} ({task['status']})" for task in todo_tasks]
                summary_parts.append(f"You have {len(todo_tasks)} TODO task(s):\n" + "\n".join(task_list))
            else:
                summary_parts.append("You currently have no TODO tasks assigned.")
            
            # If no specific work mentioned, add a generic prompt
            if not self.scrum_data.get("today"):
                summary_parts.append("Would you like to discuss your tasks or work for today?")
            
            # Combine summary parts
            full_summary = "\n\n".join(summary_parts)
            
            return full_summary
        
        except Exception as e:
            print(f"[ERROR] Error generating summary: {str(e)}")
            traceback.print_exc()
            return "I'm ready for your standup. What would you like to discuss?"

async def recognize_speech(audio_file_path=None):
    """Capture microphone input and send it to Deepgram for STT using v3 API."""
    print("\n[DEBUG] Processing audio...")
    
    try:
        # If audio file is provided, use it directly
        if audio_file_path:
            print(f"[DEBUG] Using provided audio file: {audio_file_path}")
            
            # Send the WAV file to Deepgram
            url = "https://api.deepgram.com/v1/listen?model=general"
            headers = {
                "Authorization": f"Token {os.getenv('DEEPGRAM_API_KEY')}",
                "Content-Type": "audio/wav"
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, data=open(audio_file_path, "rb")) as response:
                    print("Deepgram Response:", response.status)
                    if response.status == 200:
                        data = await response.json()
                        print("Deepgram JSON Response:", json.dumps(data, indent=2))
                        transcript = data["results"]["channels"][0]["alternatives"][0]["transcript"]
                        print(f"[DEBUG] User: {transcript}")
                        return transcript
                    else:
                        error_text = await response.text()
                        print(f"[ERROR] Error in STT: {error_text}")
                        return "Sorry, I couldn't understand."
        
        # If no audio file provided, use microphone input
        print("\n[DEBUG] Checking audio setup...")
        
        # List and select audio device
        devices = sd.query_devices()
        print("\n[DEBUG] Available audio devices:")
        for i, device in enumerate(devices):
            print(f"{i}: {device['name']} (inputs: {device['max_input_channels']}, outputs: {device['max_output_channels']})")
        
        # Find the pulse audio device
        input_device = None
        for i, device in enumerate(devices):
            if device['name'] == 'pulse' and device['max_input_channels'] > 0:
                input_device = i
                print(f"\n[DEBUG] Selected input device {i}: {device['name']}")
                break
        
        if input_device is None:
            # Fallback to first device with inputs
            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    input_device = i
                    print(f"\n[DEBUG] Selected input device {i}: {device['name']}")
                    break
        
        if input_device is None:
            print("[ERROR] No input devices found!")
            return "No microphone detected"

        audio_data = []
        audio_detected = False
        silence_counter = 0
        max_silence_frames = 15  # Reduced to about 1 second of silence
        recording_started = False
        total_silence_time = 0

        def callback(indata, frames, time, status):
            if status:
                print(f"[DEBUG] Status: {status}", flush=True)
            
            # Calculate volume level
            volume_norm = np.linalg.norm(indata) * 10
            
            # Detect speech
            nonlocal audio_detected, silence_counter, recording_started, total_silence_time
            if volume_norm > 0.05:  # Lower threshold for better sensitivity
                if not recording_started:
                    print("\n[DEBUG] Speech detected, recording...", flush=True)
                    recording_started = True
                audio_detected = True
                silence_counter = 0
                total_silence_time = 0
            elif recording_started:
                silence_counter += 1
                total_silence_time += frames / 16000  # Convert frames to seconds
            
            # Only append data once recording has started
            if recording_started:
                audio_data.append(indata.copy())
                
                # Update progress less frequently (every 4 frames)
                if len(audio_data) % 4 == 0:
                    level = min(int(volume_norm * 10), 20)  # Limit bar length
                    meter = '█' * level + '░' * (20 - level)
                    duration = len(audio_data) * frames / 16000  # Convert to seconds
                    print(f"\r[DEBUG] Recording: {meter} {duration:.1f}s {'🎤' if level > 2 else '🔇'}", end='', flush=True)

        print("\n[DEBUG] Waiting for speech... (speak to begin)")
        print("(Recording will stop automatically after 10 seconds)")
        
        with sd.InputStream(
            device=input_device,
            samplerate=16000,
            channels=1,
            dtype="int16",
            callback=callback,
            blocksize=4000
        ):
            # Record for exactly 10 seconds after speech is detected
            while True:
                await asyncio.sleep(0.1)
                if recording_started:
                    duration = len(audio_data) * 4000 / 16000  # Current duration in seconds
                    if duration >= 10:  # Stop after 10 seconds
                        print(f"\n\n[DEBUG] Recording complete! Duration: {duration:.1f}s")
                        break
                elif len(audio_data) > 300:  # Timeout if no speech detected
                    print("\n\n[DEBUG] No speech detected, timing out...")
                    break

        if not audio_data:
            print("[ERROR] No audio data captured!")
            return "Sorry, I couldn't capture any audio."
        
        if not audio_detected:
            print("[ERROR] No speech detected. Please check your microphone!")
            return "Sorry, I couldn't detect any speech."

        # Convert to NumPy array
        audio_np = np.concatenate(audio_data, axis=0)
        
        # Print audio statistics for debugging
        print(f"\n[DEBUG] Audio stats - Max: {np.max(np.abs(audio_np))}, Mean: {np.mean(np.abs(audio_np))}")
        print("[DEBUG] Processing audio...")
        
        # Save as WAV file
        temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        with wave.open(temp_wav.name, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit audio
            wf.setframerate(16000)
            wf.writeframes(audio_np.tobytes())

        # Send the WAV file to Deepgram
        url = "https://api.deepgram.com/v1/listen?model=general"
        headers = {
            "Authorization": f"Token {os.getenv('DEEPGRAM_API_KEY')}",
            "Content-Type": "audio/wav"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=open(temp_wav.name, "rb")) as response:
                print("Deepgram Response:", response.status)
                if response.status == 200:
                    data = await response.json()
                    print("Deepgram JSON Response:", json.dumps(data, indent=2))
                    transcript = data["results"]["channels"][0]["alternatives"][0]["transcript"]
                    print(f"[DEBUG] User: {transcript}")
                    return transcript
                else:
                    error_text = await response.text()
                    print(f"[ERROR] Error in STT: {error_text}")
                    return "Sorry, I couldn't understand."
    except Exception as e:
        print(f"[ERROR] Error in speech recognition: {e}")
        return f"Sorry, there was an error: {str(e)}"

async def ask_groq(question):
    """Send user input to Groq Llama or Mixtral and return the AI response."""
    response = await groq_client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[
            {"role": "system", "content": "You are a helpful Scrum assistant. Help extract key information about tasks, status updates, and blockers from the user's input."},
            {"role": "user", "content": question}
        ],
        temperature=0.7
    )
    reply = response.choices[0].message.content
    print(f"[DEBUG] Groq: {reply}")
    return reply

async def speak_text(text):
    """Convert text to speech using Deepgram's TTS API."""
    try:
        print(f"\n[DEBUG] Converting to speech: {text}")
        
        if not os.getenv('DEEPGRAM_API_KEY'):
            print("[ERROR] DEEPGRAM_API_KEY is not set!")
            return None
            
        print(f"[DEBUG] Using Deepgram API Key: {os.getenv('DEEPGRAM_API_KEY')[:5]}...")
        
        # Specify WAV format in the URL
        url = "https://api.deepgram.com/v1/speak?model=aura-asteria-en&encoding=linear16&container=wav"
        headers = {
            "Authorization": f"Token {os.getenv('DEEPGRAM_API_KEY')}",
            "Content-Type": "application/json"
        }
        payload = {
            "text": text
        }
        
        print("[DEBUG] Making request to Deepgram...")
        print("Headers:", {k: v[:10] + '...' if k == 'Authorization' else v for k, v in headers.items()})
        print("Payload:", json.dumps(payload, indent=2))
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                print(f"[DEBUG] Deepgram response status: {response.status}")
                if response.status == 200:
                    audio_data = await response.read()
                    print(f"[DEBUG] Received {len(audio_data)} bytes of audio data")
                    return audio_data
                else:
                    error_text = await response.text()
                    print(f"[ERROR] Error in TTS: {error_text}")
                    return None
    except Exception as e:
        print(f"[ERROR] Error in text-to-speech: {e}")
        traceback.print_exc()
        return None

async def main():
    """Main function to run the bot."""
    try:
        print("\n[DEBUG] Bot: Playing response...")
        
        # Test Jira connection first
        jira = JiraAPI(JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_KEY)
        if not jira.test_connection():
            print("[ERROR] Failed to connect to Jira. Please check your credentials.")
            return
            
        # Test with SCRUM-11
        print("\n[DEBUG] Testing with SCRUM-11...")
        details = jira.get_issue_details("SCRUM-11")
        if details:
            print(f"[DEBUG] Current status: {details['fields']['status']['name']}")
            print("[DEBUG] Available transitions:")
            response = requests.get(
                f"{jira.server_url}/rest/agile/1.0/board",
                headers=jira.headers,
                auth=jira.auth
            )
            if response.status_code == 200:
                boards = response.json()["values"]
                if boards:
                    board_id = boards[0]["id"]  # Use the first board
                    
                    # Get active sprints for this board
                    sprints_url = f"{jira.server_url}/rest/agile/1.0/board/{board_id}/sprint?state=active"
                    sprints = requests.get(
                        sprints_url,
                        headers=jira.headers,
                        auth=jira.auth
                    )
                    if sprints.status_code == 200:
                        sprints = sprints.json()["values"]
                        if sprints:
                            sprint_id = sprints[0]["id"]
                            response = requests.get(
                                f"{jira.server_url}/rest/agile/1.0/sprint/{sprint_id}/issue",
                                headers=jira.headers,
                                auth=jira.auth
                            )
                            if response.status_code == 200:
                                issues = response.json()["issues"]
                                for issue in issues:
                                    print(f"- {issue['key']}: {issue['fields']['summary']}")

        bot = ScrumBot(jira)
        
        # Start with greeting state
        response = bot.process_response("greeting")
        print(f"\n[DEBUG] Bot: {response}")
        await speak_text(response)

        while bot.current_state != "summary":
            # Get speech input
            text = await recognize_speech()
            if not text:
                print("\n[ERROR] No speech detected, please try again")
                continue
            
            print(f"\n[DEBUG] You: {text}")
            
            # Process the response
            response = bot.process_response(text)
            print(f"\n[DEBUG] Bot: {response}")
            await speak_text(response)

    except Exception as e:
        print(f"\n[ERROR] Error in main loop: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())