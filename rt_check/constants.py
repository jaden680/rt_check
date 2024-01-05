import os
from dotenv import load_dotenv

load_dotenv()

#Jira
JIRA_URL = "https://croquis.atlassian.net"
PROJECT_KEY = "APP"
REQUEST_VERSION_NAME = "검증 계획 요청"
NOT_RELEASED_VERSION_NAME = "앱 배포 없는 과제"

#Auth
USER_NAME = os.getenv("USER_NAME")
API_TOKEN = os.getenv("API_TOKEN")

#Git
TICKET_FILTER = os.getenv("TICKET_FILTER")