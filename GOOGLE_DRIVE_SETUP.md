# Google Drive Setup Guide

This guide covers everything needed to configure the PDF Redactor's Google Drive upload feature, including Google Cloud service account creation and shared drive access.

## Prerequisites

- A Google Cloud project linked to your Google Workspace organization
- Admin access to Google Workspace (admin.google.com)
- Access to Google Cloud Console (console.cloud.google.com)

## 1. Enable the Google Drive API

1. Go to **Google Cloud Console → APIs & Services → Library**
2. Search for **Google Drive API**
3. Click **Enable**

## 2. Create a Service Account

1. Go to **IAM & Admin → Service Accounts**
2. Click **Create Service Account**
3. Give it a name (e.g. `uploader`) and click **Create and Continue**
4. Optionally grant it a role (not strictly required for Drive uploads)
5. Click **Done**

## 3. Create a Service Account Key

> **Note:** Your organization may have the `iam.disableServiceAccountKeyCreation` policy enabled, which blocks key creation. If you see the error *"Service account key creation is disabled"*, follow the steps in **Section 3a** below first.

1. Click on the service account you just created
2. Go to the **Keys** tab
3. Click **Add Key → Create new key → JSON**
4. Save the downloaded JSON file as `credentials.json` in the project root

### 3a. Disabling the Key Creation Restriction (if needed)

This org policy must be modified at the **organization level**, not the project level.

1. Go to **Google Cloud Console**
2. In the **project selector dropdown at the top**, select your **organization** (e.g. `mana-drevostavby.cz`) — not a project
3. Navigate to **IAM & Admin → Organisation Policies**
4. Search for `disableServiceAccountKeyCreation`
5. Click on **Disable service account key creation** (the row with `iam.disableServiceAccountKeyCreation`, type "Managed (legacy)")
6. Click the three dots → **Edit policy**
7. Set enforcement to **Off** (or add a project-level exception)
8. Save

**Required role:** The account editing the policy needs the **Organisation Policy Administrator** role (`roles/orgpolicy.policyAdmin`). To grant it:

1. Stay at the organization level in Cloud Console
2. Go to **IAM & Admin → IAM**
3. Find your admin user and click the edit (pencil) icon
4. Click **Add another role**
5. Search for and select **Organisation Policy Administrator**
6. Save

After disabling the constraint, return to your service account and create the key.

> **Security note:** Consider re-enabling the constraint after creating your key. Service account keys are long-lived credentials and a common source of leaks. For production workloads running on GCP infrastructure, Workload Identity Federation is the preferred alternative.

## 4. Share the Google Drive Folder with the Service Account

The service account is a separate identity — it has no access to your Drive by default.

1. Open Google Drive and navigate to the target folder (or Shared Drive)
2. Click **Share**
3. Paste the service account's email address (found in `credentials.json` as `client_email`, e.g. `uploader@your-project.iam.gserviceaccount.com`)
4. Grant **Editor** (or **Content Manager** for Shared Drives) access
5. Click **Done**

## 5. Configure the Application

Create or edit `config.json` in the project root:

```json
{
  "storage": {
    "type": "google_drive",
    "folder_id": "YOUR_FOLDER_OR_SHARED_DRIVE_ID",
    "credentials_path": "credentials.json"
  },
  "file_naming": {
    "pattern": "{customer_name}.pdf"
  }
}
```

The `folder_id` is the last part of the folder's URL: `https://drive.google.com/drive/folders/THIS_PART`

## 6. Shared Drives — Important Code Requirement

If uploading to a **Shared Drive** (as opposed to a regular folder in someone's My Drive), the API call **must** include `supportsAllDrives=True`:

```python
service.files().create(
    body=file_metadata,
    media_body=media,
    fields="id,name,webViewLink",
    supportsAllDrives=True
).execute()
```

Without this parameter, the API returns a `404: File not found` error even when the service account has access.

## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `Service account key creation is disabled` | Org policy `iam.disableServiceAccountKeyCreation` is active | See Section 3a |
| `Edit policy` button grayed out | Viewing at project level, or missing `orgpolicy.policyAdmin` role | Switch to org level and grant the role (Section 3a) |
| `invalid_grant: account not found` | Service account was deleted or key references a nonexistent account | Check that the service account still exists under IAM → Service Accounts; create a new one if needed |
| `404: File not found: <folder_id>` | Missing `supportsAllDrives=True` or service account not shared on the folder | Add the parameter (Section 6) and verify sharing (Section 4) |
