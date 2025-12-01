#!/usr/bin/env python3

import requests
import json
import sys
import os

TAIGA_URL = os.getenv("TAIGA_URL", "http://localhost:9090")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "adsadmin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")

def authenticate(base_url, username, password):
    try:
        response = requests.post(
            f"{base_url}/api/v1/auth",
            json={
                "username": username,
                "password": password,
                "type": "normal"
            },
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            data = response.json()
            return data.get("auth_token"), data.get("id")
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return None, None

    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return None, None

def get_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def verify_admin_in_projects(base_url, token, admin_id):
    print("\n📋 Checking admin membership in all projects...")

    try:
        response = requests.get(
            f"{base_url}/api/v1/projects",
            headers=get_headers(token)
        )

        if response.status_code != 200:
            print(f"❌ Failed to fetch projects: {response.status_code}")
            return False

        projects = response.json()
        total = len(projects)
        member_count = 0
        not_member = []

        for project in projects:
            memberships_response = requests.get(
                f"{base_url}/api/v1/memberships?project={project['id']}",
                headers=get_headers(token)
            )

            if memberships_response.status_code == 200:
                memberships = memberships_response.json()
                is_member = any(m.get("user") == admin_id for m in memberships)

                if is_member:
                    member_count += 1
                else:
                    not_member.append(project['name'])

        print(f"\n✅ Admin is member of {member_count}/{total} projects")

        if not_member:
            print(f"\n⚠️  Projects where admin is NOT a member:")
            for name in not_member:
                print(f"   - {name}")
            return False
        else:
            print("✅ Admin is a member of ALL projects!")
            return True

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("🔍 Taiga Auto-Assign Verification")
    print("=" * 60)

    if not ADMIN_PASSWORD:
        print("\n⚠️  Please set ADMIN_PASSWORD environment variable")
        print("   Example: export ADMIN_PASSWORD='your-password'")
        sys.exit(1)

    print(f"\n📝 Configuration:")
    print(f"   URL: {TAIGA_URL}")
    print(f"   Username: {ADMIN_USERNAME}")

    token, admin_id = authenticate(TAIGA_URL, ADMIN_USERNAME, ADMIN_PASSWORD)

    if not token:
        print("\n❌ Authentication failed. Please check your credentials.")
        sys.exit(1)

    print(f"✅ Authenticated! Admin ID: {admin_id}")

    all_good = verify_admin_in_projects(TAIGA_URL, token, admin_id)

    print("\n" + "=" * 60)
    if all_good:
        print("✅ Verification PASSED - Auto-assign is working correctly!")
    else:
        print("⚠️  Verification INCOMPLETE - Some issues found")
        print("\n💡 Try running: ./taiga-manage.sh add_admin_to_all_projects")
    print("=" * 60)

    sys.exit(0 if all_good else 1)

if __name__ == "__main__":
    main()
