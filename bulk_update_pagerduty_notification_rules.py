import requests
import getpass
import sys

BASE_URL = "https://api.pagerduty.com"
HEADERS = {
    "Accept": "application/vnd.pagerduty+json;version=2",
    "Content-Type": "application/json"
}

def get_api_key():
    # For security, prompt for API key at runtime
    return getpass.getpass("Enter your PagerDuty API key: ")

def get_all_users(api_key):
    users = []
    url = f"{BASE_URL}/users"
    params = {"limit": 100, "offset": 0}
    headers = HEADERS.copy()
    headers["Authorization"] = f"Token token={api_key}"
    while True:
        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()
        data = resp.json()
        users.extend(data["users"])
        if not data.get("more"):
            break
        params["offset"] += params["limit"]
    return users

def get_all_teams(api_key):
    teams = []
    url = f"{BASE_URL}/teams"
    params = {"limit": 100, "offset": 0}
    headers = HEADERS.copy()
    headers["Authorization"] = f"Token token={api_key}"
    while True:
        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()
        data = resp.json()
        teams.extend(data["teams"])
        if not data.get("more"):
            break
        params["offset"] += params["limit"]
    return teams

def get_team_users(api_key, team_id):
    users = []
    url = f"{BASE_URL}/teams/{team_id}/users"
    params = {"limit": 100, "offset": 0}
    headers = HEADERS.copy()
    headers["Authorization"] = f"Token token={api_key}"
    while True:
        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()
        data = resp.json()
        users.extend(data["users"])
        if not data.get("more"):
            break
        params["offset"] += params["limit"]
    return users

def get_user_contact_methods(api_key, user_id):
    url = f"{BASE_URL}/users/{user_id}/contact_methods"
    headers = HEADERS.copy()
    headers["Authorization"] = f"Token token={api_key}"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()["contact_methods"]

def get_user_notification_rules(api_key, user_id):
    url = f"{BASE_URL}/users/{user_id}/notification_rules"
    headers = HEADERS.copy()
    headers["Authorization"] = f"Token token={api_key}"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()["notification_rules"]

def delete_notification_rule(api_key, user_id, rule_id):
    url = f"{BASE_URL}/users/{user_id}/notification_rules/{rule_id}"
    headers = HEADERS.copy()
    headers["Authorization"] = f"Token token={api_key}"
    resp = requests.delete(url, headers=headers)
    resp.raise_for_status()

def create_notification_rule(api_key, user_id, payload):
    url = f"{BASE_URL}/users/{user_id}/notification_rules"
    headers = HEADERS.copy()
    headers["Authorization"] = f"Token token={api_key}"
    resp = requests.post(url, headers=headers, json=payload)
    resp.raise_for_status()
    return resp.json()

def prompt_select(prompt, options, allow_multiple=True):
    print(f"\n{prompt}")
    for idx, opt in enumerate(options):
        print(f"{idx+1}. {opt}")
    if allow_multiple:
        selection = input("Enter comma-separated numbers (e.g. 1,3): ")
        indices = [int(x.strip())-1 for x in selection.split(",") if x.strip().isdigit()]
        return [options[i] for i in indices if 0 <= i < len(options)]
    else:
        selection = input("Enter number: ")
        idx = int(selection.strip())-1
        return options[idx] if 0 <= idx < len(options) else None

def prompt_yes_no(prompt):
    return input(f"{prompt} (y/n): ").strip().lower().startswith("y")

def main():
    print("PagerDuty Bulk Notification Rule Updater\n")
    api_key = get_api_key()
    HEADERS["Authorization"] = f"Token token={api_key}"

    # Step 1: Choose users
    print("\nWhich users do you want to update?")
    user_scope = prompt_select(
        "Select user scope:",
        ["All users", "Specific users", "Specific teams"],
        allow_multiple=False
    )

    users = []
    if user_scope == "All users":
        users = get_all_users(api_key)
    elif user_scope == "Specific users":
        all_users = get_all_users(api_key)
        user_names = [f"{u['name']} ({u['email']})" for u in all_users]
        selected = prompt_select("Select users to update:", user_names)
        users = [u for u in all_users if f"{u['name']} ({u['email']})" in selected]
    elif user_scope == "Specific teams":
        all_teams = get_all_teams(api_key)
        team_names = [f"{t['name']} ({t['id']})" for t in all_teams]
        selected_teams = prompt_select("Select teams to update:", team_names)
        selected_team_ids = [t.split("(")[-1].strip(")") for t in selected_teams]
        users = []
        for team_id in selected_team_ids:
            team_users = get_team_users(api_key, team_id)
            users.extend(team_users)
        # Remove duplicates
        users = {u['id']: u for u in users}.values()
        users = list(users)

    if not users:
        print("No users selected. Exiting.")
        sys.exit(0)

    print(f"\nSelected {len(users)} users.")

    # Step 2: Replace or add rules
    replace = prompt_yes_no("Do you want to REPLACE all existing notification rules? (Otherwise, new rules will be added)")

    # Step 3: Notification methods by urgency
    urgencies = ["high", "low"]
    method_types = {
        "email_contact_method": "Email",
        "sms_contact_method": "SMS",
        "phone_contact_method": "Phone",
        "push_notification_contact_method": "Push"
    }
    urgency_methods = {}
    for urgency in urgencies:
        print(f"\nSelect notification methods for {urgency.upper()} urgency:")
        selected_methods = prompt_select(
            f"Choose methods for {urgency} urgency:",
            list(method_types.values())
        )
        urgency_methods[urgency] = selected_methods

    # Step 4: Prompt for timing for each method
    method_delays = {}
    for urgency in urgencies:
        for method in urgency_methods[urgency]:
            delay = input(f"Enter delay in minutes for {method} ({urgency} urgency, 0 for immediate): ")
            try:
                delay = int(delay)
            except ValueError:
                delay = 0
            method_delays[(urgency, method)] = delay

    # Step 5: For each user, update notification rules
    for user in users:
        user_id = user["id"]
        print(f"\nUpdating user: {user.get('name', user.get('email', user_id))}")
        contact_methods = get_user_contact_methods(api_key, user_id)
        # Map method type to contact method IDs
        method_map = {}
        for cm in contact_methods:
            mtype = method_types.get(cm["type"])
            if mtype:
                method_map.setdefault(mtype, []).append(cm["id"])

        if replace:
            # Delete all existing notification rules
            rules = get_user_notification_rules(api_key, user_id)
            for rule in rules:
                delete_notification_rule(api_key, user_id, rule["id"])
            print("Deleted existing notification rules.")

        # Add new rules
        for urgency in urgencies:
            for method in urgency_methods[urgency]:
                if method not in method_map:
                    print(f"User does not have {method} contact method, skipping.")
                    continue
                for cm_id in method_map[method]:
                    payload = {
                        "notification_rule": {
                            "start_delay_in_minutes": method_delays[(urgency, method)],
                            "contact_method": {
                                "id": cm_id,
                                "type": [k for k, v in method_types.items() if v == method][0]
                            },
                            "urgency": urgency
                        }
                    }
                    try:
                        create_notification_rule(api_key, user_id, payload)
                        print(f"Added {method} rule ({urgency}, {method_delays[(urgency, method)]} min delay).")
                    except Exception as e:
                        print(f"Failed to add rule: {e}")

    print("\nDone!")

if __name__ == "__main__":
    main()
