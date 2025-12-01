#!/usr/bin/env python3

import requests
import json
import sys
import os
from typing import Optional, List, Dict

TAIGA_URL = os.getenv("TAIGA_URL", "http://localhost:9090")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "adsadmin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "lhweave@gmail.com")

class TaigaAutoAssign:
    def __init__(self, base_url: str, username: str, password: str, email: str):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.email = email
        self.token = None
        self.admin_id = None

    def authenticate(self) -> bool:
        print(f"🔐 Authenticating as {self.username}...")

        try:
            response = requests.post(
                f"{self.base_url}/api/v1/auth",
                json={
                    "username": self.username,
                    "password": self.password,
                    "type": "normal"
                },
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                data = response.json()
                self.token = data.get("auth_token")
                self.admin_id = data.get("id")
                print(f"✅ Authentication successful! Admin ID: {self.admin_id}")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False

        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False

    def get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def get_all_projects(self) -> List[Dict]:
        print("\n📋 Fetching all projects...")

        try:
            response = requests.get(
                f"{self.base_url}/api/v1/projects",
                headers=self.get_headers()
            )

            if response.status_code == 200:
                projects = response.json()
                print(f"✅ Found {len(projects)} projects")
                return projects
            else:
                print(f"❌ Failed to fetch projects: {response.status_code}")
                return []

        except Exception as e:
            print(f"❌ Error fetching projects: {str(e)}")
            return []

    def get_project_memberships(self, project_id: int) -> List[Dict]:
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/memberships?project={project_id}",
                headers=self.get_headers()
            )

            if response.status_code == 200:
                return response.json()
            else:
                return []

        except Exception as e:
            print(f"❌ Error fetching memberships: {str(e)}")
            return []

    def is_admin_member(self, project_id: int) -> bool:
        memberships = self.get_project_memberships(project_id)
        return any(m.get("user") == self.admin_id for m in memberships)

    def add_admin_to_project(self, project: Dict) -> bool:
        project_id = project.get("id")
        project_name = project.get("name")

        if self.is_admin_member(project_id):
            print(f"  ⏭️  {project_name} - Admin already a member")
            return True

        roles = project.get("roles", [])
        if not roles:
            print(f"  ❌ {project_name} - No roles available")
            return False

        role_id = None
        for role in roles:
            if role.get("name") in ["Product Owner", "Scrum Master", "Owner"]:
                role_id = role.get("id")
                break

        if not role_id and roles:
            role_id = roles[0].get("id")

        if not role_id:
            print(f"  ❌ {project_name} - Could not find suitable role")
            return False

        try:
            response = requests.post(
                f"{self.base_url}/api/v1/memberships",
                json={
                    "project": project_id,
                    "role": role_id,
                    "username": self.email,
                    "is_admin": True
                },
                headers=self.get_headers()
            )

            if response.status_code == 201:
                print(f"  ✅ {project_name} - Admin added successfully")
                return True
            else:
                print(f"  ❌ {project_name} - Failed: {response.status_code}")
                print(f"     Response: {response.text}")
                return False

        except Exception as e:
            print(f"  ❌ {project_name} - Error: {str(e)}")
            return False

    def process_all_projects(self):
        print("\n🚀 Starting batch processing...\n")

        projects = self.get_all_projects()

        if not projects:
            print("⚠️  No projects found or unable to fetch projects")
            return

        success_count = 0
        skip_count = 0
        fail_count = 0

        for project in projects:
            result = self.add_admin_to_project(project)
            if result:
                if self.is_admin_member(project.get("id")):
                    success_count += 1
                else:
                    skip_count += 1
            else:
                fail_count += 1

        print(f"\n📊 Summary:")
        print(f"   ✅ Successfully added: {success_count}")
        print(f"   ⏭️  Already member: {skip_count}")
        print(f"   ❌ Failed: {fail_count}")
        print(f"   📁 Total projects: {len(projects)}")

def main():
    print("=" * 60)
    print("🎯 Taiga Auto-Assign Admin - Batch Processor")
    print("=" * 60)

    if not ADMIN_PASSWORD:
        print("\n⚠️  Please set ADMIN_PASSWORD environment variable")
        print("   Example: export ADMIN_PASSWORD='your-password'")
        sys.exit(1)

    print(f"\n📝 Configuration:")
    print(f"   URL: {TAIGA_URL}")
    print(f"   Username: {ADMIN_USERNAME}")
    print(f"   Email: {ADMIN_EMAIL}")

    auto_assign = TaigaAutoAssign(TAIGA_URL, ADMIN_USERNAME, ADMIN_PASSWORD, ADMIN_EMAIL)

    if not auto_assign.authenticate():
        print("\n❌ Authentication failed. Please check your credentials.")
        sys.exit(1)

    auto_assign.process_all_projects()

    print("\n✅ Batch processing complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
