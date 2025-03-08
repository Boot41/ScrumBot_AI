import requests
import json
from typing import Dict, List, Tuple, Optional

class JiraAPI:
    def __init__(self, email: str, api_key: str, server_url: str):
        self.email = email
        self.api_key = api_key
        self.server_url = server_url
        self.auth = (email, api_key)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def get_issue_details(self, issue_key: str) -> Optional[Dict]:
        """Get details of a JIRA issue."""
        url = f"{self.server_url}/rest/api/3/issue/{issue_key}"
        try:
            response = requests.get(url, auth=self.auth, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None

    def create_issue(self, project: str, summary: str, description: str, issue_type: str = "Story") -> str:
        """Create a new JIRA issue."""
        url = f"{self.server_url}/rest/api/3/issue"
        data = {
            "fields": {
                "project": {"key": project},
                "summary": summary,
                "description": description,
                "issuetype": {"name": issue_type}
            }
        }
        try:
            response = requests.post(url, json=data, auth=self.auth, headers=self.headers)
            if response.status_code == 201:
                return response.json()["key"]
            return None
        except Exception:
            return None

    def get_transitions(self, issue_key: str) -> Optional[Dict]:
        """Get available transitions for an issue."""
        url = f"{self.server_url}/rest/api/3/issue/{issue_key}/transitions"
        try:
            response = requests.get(url, auth=self.auth, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None

    def update_issue_status(self, issue_key: str, status: str) -> Tuple[bool, str]:
        """Update the status of a JIRA issue."""
        # Get issue details first
        issue = self.get_issue_details(issue_key)
        if not issue:
            return False, "Could not get issue details"

        # Get available transitions
        transitions = self.get_transitions(issue_key)
        if not transitions:
            return False, "Could not get transitions"

        # Find the transition ID for the target status
        transition_id = None
        for transition in transitions["transitions"]:
            if transition["name"].lower() == status.lower():
                transition_id = transition["id"]
                break

        if not transition_id:
            return False, f"No transition found for status: {status}"

        # Perform the transition
        url = f"{self.server_url}/rest/api/3/issue/{issue_key}/transitions"
        data = {
            "transition": {"id": transition_id}
        }
        try:
            response = requests.post(url, json=data, auth=self.auth, headers=self.headers)
            return response.status_code == 204, "Status updated successfully"
        except Exception as e:
            return False, str(e)

    def create_blocker(self, issue_key: str, description: str) -> Tuple[bool, str]:
        """Create a blocker for a JIRA issue."""
        # Get issue details first
        issue = self.get_issue_details(issue_key)
        if not issue:
            return False, "Could not get issue details"

        # Create a new issue for the blocker
        project = issue_key.split("-")[0]
        summary = f"Blocker for {issue_key}: {description[:50]}"
        blocker_key = self.create_issue(project, summary, description, "Blocker")
        if not blocker_key:
            return False, "Failed to create blocker issue"

        # Link the blocker to the original issue
        url = f"{self.server_url}/rest/api/3/issueLink"
        data = {
            "type": {"name": "Blocks"},
            "inwardIssue": {"key": blocker_key},
            "outwardIssue": {"key": issue_key}
        }
        try:
            response = requests.post(url, json=data, auth=self.auth, headers=self.headers)
            if response.status_code == 201:
                return True, blocker_key
            return False, "Failed to link blocker issue"
        except Exception:
            return False, "Failed to link blocker issue"

    def get_current_sprint_id(self) -> Optional[int]:
        """Get the ID of the current active sprint."""
        url = f"{self.server_url}/rest/agile/1.0/sprint/active"
        try:
            response = requests.get(url, auth=self.auth, headers=self.headers)
            if response.status_code == 200:
                sprints = response.json()["values"]
                if sprints:
                    return sprints[0]["id"]
            return None
        except Exception:
            return None

    def get_project_summary(self) -> Dict:
        """Get a summary of project issues."""
        try:
            # Get all epics
            epics_url = f"{self.server_url}/rest/api/3/search?jql=issuetype=Epic"
            epics_response = requests.get(epics_url, auth=self.auth, headers=self.headers)
            epics = []
            if epics_response.status_code == 200:
                for epic in epics_response.json()["issues"]:
                    epics.append({
                        "key": epic["key"],
                        "summary": epic["fields"]["summary"],
                        "status": epic["fields"]["status"]["name"]
                    })

            # Get all stories
            stories_url = f"{self.server_url}/rest/api/3/search?jql=issuetype=Story"
            stories_response = requests.get(stories_url, auth=self.auth, headers=self.headers)
            stories = []
            if stories_response.status_code == 200:
                for story in stories_response.json()["issues"]:
                    stories.append({
                        "key": story["key"],
                        "summary": story["fields"]["summary"],
                        "status": story["fields"]["status"]["name"]
                    })

            return {
                "epics": epics,
                "stories": stories,
                "total_issues": len(epics) + len(stories)
            }
        except Exception as e:
            raise Exception(f"Failed to fetch project summary: {str(e)}")
