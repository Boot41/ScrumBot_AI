# ScrumBot AI

An AI-powered Scrum assistant that helps automate daily standup meetings and Jira task management.

## Setup

1. Clone the repository:
```bash
git clone https://github.com/Boot41/ScrumBot_AI.git
cd ScrumBot_AI
```

2. Set up environment variables:
```bash
cd server
cp .env.example .env
```

3. Edit the `.env` file with your credentials:
- `JIRA_EMAIL`: Your Jira account email
- `JIRA_API_KEY`: Your Jira API key (generate from https://id.atlassian.com/manage-profile/security/api-tokens)
- `JIRA_SERVER_URL`: Your Jira server URL (e.g., https://your-domain.atlassian.net)
- `GROQ_API_KEY`: Your Groq API key for AI services
- `DEEPGRAM_API_KEY`: Your Deepgram API key for speech services

4. Start the application:
```bash
docker-compose up --build
```

The application will be available at http://localhost:8000.

## Features

- Automated daily standup meetings
- Voice interaction with AI assistant
- Jira task management integration
- Real-time task status updates
- Natural language processing for task updates

## Security Note

Never commit your `.env` file or any API keys to the repository. The `.env` file is gitignored for security.
