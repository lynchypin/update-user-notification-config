# PagerDuty Bulk Notification Rule Updater

A command-line tool to bulk update notification rules for multiple PagerDuty users simultaneously. This script allows administrators to standardize notification configurations across teams or the entire organization.

## Features

- Update notification rules for all users, specific users, or users within specific teams
- Choose to replace existing rules or add new ones alongside them
- Configure different notification methods for high and low urgency incidents
- Set custom delays for each notification method
- Supports Email, SMS, Phone, and Push notification methods

## Requirements

### Python Version
- Python 3.6 or higher

### Dependencies
Install the required package using pip:

```bash
pip install requests
```

Or create a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# OR
.\venv\Scripts\activate   # On Windows

pip install requests
```

### PagerDuty API Key
You need a PagerDuty API key with the following permissions:
- **Read access** to Users, Teams, Contact Methods, and Notification Rules
- **Write access** to Notification Rules (create/delete)

To create an API key:
1. Log in to your PagerDuty account
2. Navigate to **Integrations** > **API Access Keys**
3. Click **Create New API Key**
4. Give it a descriptive name and select appropriate permissions
5. Copy and securely store the generated key

## How to Use

### 1. Run the Script

```bash
python bulk_update_pagerduty_notification_rules.py
```

### 2. Enter Your API Key
When prompted, enter your PagerDuty API key. The input is hidden for security.

```
Enter your PagerDuty API key: 
```

### 3. Select User Scope
Choose which users to update:

```
Select user scope:
1. All users
2. Specific users
3. Specific teams
Enter number: 
```

- **All users**: Updates every user in your PagerDuty account
- **Specific users**: Shows a list of users to select from (comma-separated)
- **Specific teams**: Shows a list of teams; all users in selected teams will be updated

### 4. Choose Replace or Add Mode

```
Do you want to REPLACE all existing notification rules? (Otherwise, new rules will be added) (y/n): 
```

- **Yes (y)**: Deletes all existing notification rules before adding new ones
- **No (n)**: Keeps existing rules and adds new ones

### 5. Configure Notification Methods
For each urgency level (high and low), select which notification methods to use:

```
Select notification methods for HIGH urgency:
Choose methods for high urgency:
1. Email
2. SMS
3. Phone
4. Push
Enter comma-separated numbers (e.g. 1,3): 
```

### 6. Set Notification Delays
For each selected method, specify the delay in minutes (0 for immediate):

```
Enter delay in minutes for Push (high urgency, 0 for immediate): 0
Enter delay in minutes for SMS (high urgency, 0 for immediate): 5
```

### 7. Review Progress
The script will process each user and display progress:

```
Updating user: John Doe
Deleted existing notification rules.
Added Push rule (high, 0 min delay).
Added SMS rule (high, 5 min delay).
Added Email rule (low, 15 min delay).
```

## Example Configuration

A common enterprise configuration might be:

| Urgency | Method | Delay |
|---------|--------|-------|
| High | Push | 0 min (immediate) |
| High | SMS | 5 min |
| High | Phone | 10 min |
| Low | Email | 0 min (immediate) |

## Security Considerations

- **API Key Handling**: The script uses `getpass` to securely prompt for the API key without displaying it on screen
- **HTTPS Only**: All API communications use HTTPS encryption
- **No Credential Storage**: The API key is never written to disk or logged
- **Minimal Permissions**: Use an API key with only the required permissions

## Troubleshooting

### Common Issues

**"User does not have X contact method, skipping"**
- The user hasn't configured that contact method in their PagerDuty profile
- They need to add it manually in PagerDuty before rules can be created for it

**HTTP 401 Unauthorized**
- Your API key is invalid or expired
- Generate a new API key from PagerDuty

**HTTP 403 Forbidden**
- Your API key lacks the required permissions
- Ensure the key has read/write access to notification rules

**HTTP 429 Too Many Requests**
- You've hit PagerDuty's rate limit
- Wait a few minutes and try again with fewer users

## License

See the [LICENSE](LICENSE) file for details.
