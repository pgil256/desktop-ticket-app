# Desktop Ticket App

A PyQt6 desktop client for looking up SharePoint inventory and submitting support tickets. Microsoft sign-in opens in the browser. The app uses the permissions of the signed-in account.

## Setup

Install the dependencies in a Python virtual environment. The desktop window has been tested with Python 3.12 on Windows.

```sh
python -m pip install -r requirements.txt
```

Use a Microsoft Entra desktop application registered for the tenant that owns the site. Configure its mobile and desktop redirect URI as `http://localhost`. The application needs delegated SharePoint access to the intended site and the user needs permission to read inventory and submit tickets. [Microsoft’s desktop application configuration guide](https://learn.microsoft.com/en-us/entra/identity-platform/scenario-desktop-app-configuration).

| Environment variable | Value |
| --- | --- |
| `SHAREPOINT_SITE_URL` | HTTPS address of the SharePoint site |
| `SHAREPOINT_TENANT_ID` | Tenant ID or tenant domain |
| `SHAREPOINT_CLIENT_ID` | Application (client) ID of the registered desktop app |

The client expects `Inventory` and `Tickets` lists with the columns used in `sharepoint_utils.py`. Start the desktop app and select **Sign in with Microsoft**.

```sh
python main.py
```
