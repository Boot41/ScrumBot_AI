import re
from typing import Dict, List, Optional
from .jira_api import JiraAPI

class ScrumBot:
    def __init__(self, jira_api: JiraAPI):
        self.jira = jira_api
        self.current_state = "greeting"
        self.scrum_data = {
            "yesterday": "",
            "today": "",
            "blockers": []
        }
        self.status_keywords = {
            "done": ["finished", "completed", "done"],
            "in progress": ["working", "started", "in progress"],
            "to do": ["planning", "will start", "todo", "to do"],
            "blocked": ["blocked", "stuck", "waiting"]
        }

    def extract_jira_key(self, text: str) -> Optional[str]:
        """Extract JIRA issue key from text."""
        pattern = r'([A-Z]+-\d+)'
        match = re.search(pattern, text)
        return match.group(1) if match else None

    def determine_status(self, text: str) -> str:
        """Determine issue status from text."""
        text = text.lower()
        for status, keywords in self.status_keywords.items():
            if any(keyword in text for keyword in keywords):
                return status.title()
        return "To Do"  # Default status

    def process_response(self, response: str) -> str:
        """Process user response and update bot state."""
        if not response:
            return "I didn't catch that. Could you please repeat?"

        response = response.strip()
        if self.current_state == "greeting":
            self.current_state = "yesterday"
            return "What did you work on yesterday?"

        elif self.current_state == "yesterday":
            self.scrum_data["yesterday"] = response
            self.current_state = "today"
            return "What will you be working on today?"

        elif self.current_state == "today":
            self.scrum_data["today"] = response
            self.current_state = "blockers"
            return "Do you have any blockers? (yes/no)"

        elif self.current_state == "blockers":
            if response.lower() == "yes":
                self.current_state = "blocker_details"
                return "Please describe your blocker."
            elif response.lower() == "no":
                self.current_state = "summary"
                return self.generate_summary()
            else:
                return "Please answer with 'yes' or 'no'."

        elif self.current_state == "blocker_details":
            issue_key = self.extract_jira_key(response)
            if issue_key:
                # Update issue status and create blocker
                self.jira.update_issue_status(issue_key, "Blocked")
                success, blocker_key = self.jira.create_blocker(issue_key, response)
                if success:
                    self.scrum_data["blockers"].append(response)

            self.current_state = "more_blockers"
            return "Do you have any other blockers? (yes/no)"

        elif self.current_state == "more_blockers":
            if response.lower() == "yes":
                self.current_state = "blocker_details"
                return "Please describe your next blocker."
            elif response.lower() == "no":
                self.current_state = "summary"
                return self.generate_summary()
            else:
                return "Please answer with 'yes' or 'no'."

        elif self.current_state == "summary":
            self.current_state = "greeting"  # Reset for next standup
            return "Is there anything else you'd like to discuss?"

        return "I'm not sure how to handle that response. Let's start over with your standup. What did you work on yesterday?"

    def generate_summary(self) -> str:
        """Generate a summary of the standup."""
        yesterday_issues = self.extract_jira_key(self.scrum_data["yesterday"])
        today_issues = self.extract_jira_key(self.scrum_data["today"])
        
        summary = "Hello! "
        
        if yesterday_issues:
            summary += f"It's great to see that you wrapped up {yesterday_issues} nicely. "
        else:
            summary += "It's great to see that you wrapped up yesterday's work smoothly. "
        
        if today_issues:
            summary += f"Now you're all set to tackle {today_issues} today. "
        else:
            summary += "That's some terrific progress you've made! "
        
        if self.scrum_data["blockers"]:
            summary += "I see there are some blockers we need to address. I'll make sure the team is aware of them. "
        else:
            summary += "And it's fantastic that you don't have any blockers! "
        
        summary += "Keep up the great work!"
        return summary

    def reset_state(self) -> None:
        """Reset bot state and data."""
        self.current_state = "greeting"
        self.scrum_data = {
            "yesterday": "",
            "today": "",
            "blockers": []
        }
