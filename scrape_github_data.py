import requests
import csv
from config import GITHUB_TOKEN

BASE_URL = "https://api.github.com"
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

def fetch_users(city="Stockholm", min_followers=100, max_users=407):
    users = []
    page = 1
    while len(users) < max_users:
        url = f"{BASE_URL}/search/users?q=location:{city}+followers:>{min_followers}&per_page=100&page={page}"
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            users.extend(data["items"])
            if len(data["items"]) < 100:  # Break if there are no more users
                break
        else:
            print("Error fetching users:", response.status_code, response.text)
            break
        page += 1
    return users[:max_users]  # Return only the requested number of users

def save_users_to_csv(users, filename="users.csv"):
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["login", "name", "company", "location", "email", "hireable", "bio", "public_repos", "followers", "following", "created_at"])
        for user in users:
            user_data = requests.get(f"{BASE_URL}/users/{user['login']}", headers=HEADERS).json()
            if 'message' in user_data:
                print("Error fetching user details:", user_data.get("message"))
                continue
            company = (user_data.get("company", "") or "").strip().lstrip("@").upper()
            writer.writerow([
                user_data["login"], user_data.get("name", ""), company, user_data.get("location", ""),
                user_data.get("email", ""), user_data.get("hireable", ""), user_data.get("bio", ""),
                user_data.get("public_repos", 0), user_data.get("followers", 0), user_data.get("following", 0),
                user_data.get("created_at", "")
            ])

def fetch_and_save_repositories(users, filename="repositories.csv"):
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["login", "full_name", "created_at", "stargazers_count", "watchers_count", "language", "has_projects", "has_wiki", "license_name"])
        for user in users:
            repos_url = f"{BASE_URL}/users/{user['login']}/repos?per_page=500"
            repos = requests.get(repos_url, headers=HEADERS).json()
            if isinstance(repos, dict) and repos.get("message"):
                print("Error fetching repositories for", user['login'], ":", repos.get("message"))
                continue
            for repo in repos:
                license_name = repo["license"]["key"] if repo.get("license") else ""
                writer.writerow([
                    user["login"], repo["full_name"], repo["created_at"], repo["stargazers_count"],
                    repo["watchers_count"], repo["language"], repo["has_projects"], repo["has_wiki"],
                    license_name
                ])

# Run the script
users = fetch_users()
save_users_to_csv(users)
fetch_and_save_repositories(users)