# WGHA Automatic Word Updates

This GitHub repository automatically updates the used Wordle words daily.

## How It Works

1. **GitHub Actions** runs scheduled workflows at 1:00 AM and 4:30 AM UTC (backup)
2. **Python script** (`update-used-words.py`) fetches latest used words from multiple sources
3. **Daily page scraping** ensures latest words are captured even when the archive is slow to update
4. **Auto-commits** the updated `used-words.json` file
5. **Pushover notifications** alert you to successes and failures
6. **Your iOS app** fetches this file when launched

## Setup Instructions

### 1. Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `wgha-data` (or any name)
3. Public or Private (both work)
4. ✅ Check "Add a README file"
5. Click "Create repository"

### 2. Upload These Files

Upload to your new repo:
```
wgha-data/
├── .github/
│   └── workflows/
│       └── update-words.yml
├── update-used-words.py
├── requirements.txt
├── used-words.json (copy from ios-data/)
└── README.md (this file)
```

**How to upload:**
- Drag and drop files on GitHub website, OR
- Clone repo and push files via git

### 3. Enable GitHub Actions

1. Go to your repo → **Settings** → **Actions** → **General**
2. Under "Workflow permissions":
   - ✅ Select "Read and write permissions"
   - ✅ Check "Allow GitHub Actions to create and approve pull requests"
3. Click **Save**

### 4. Test the Workflow

1. Go to **Actions** tab in your repo
2. Click "Update Wordle Used Words" workflow
3. Click **Run workflow** → **Run workflow** (green button)
4. Wait ~30 seconds
5. Check that `used-words.json` was updated (check commit history)

### 5. Get the Raw URL

1. Click on `used-words.json` in your repo
2. Click the **Raw** button
3. Copy the URL (example):
   ```
   https://raw.githubusercontent.com/YOUR-USERNAME/wgha-data/main/used-words.json
   ```

### 6. Update iOS App

Edit `ios-app/Services/UsedWordsUpdater.swift` line 14:

```swift
private let serverURL = "https://raw.githubusercontent.com/YOUR-USERNAME/wgha-data/main/used-words.json"
```

Replace `YOUR-USERNAME` with your GitHub username.

### 7. Build and Test App

1. Build app in Xcode (Cmd+R)
2. Open **Settings** (gear icon)
3. Tap **Check for Updates**
4. Should show current time for "Last updated"

## Schedule

- **Primary:** Daily at 1:00 AM UTC (~2:00 AM London)
- **Backup:** Daily at 4:30 AM UTC (~5:30 AM London)
- **Updates:** Only commits if new words are found
- **Commits:** Automatic with timestamp

The backup run catches any words missed if the primary run happens before Rock Paper Shotgun updates their page.

To change the schedule, edit `.github/workflows/update-words.yml`:
```yaml
schedule:
  - cron: '0 1 * * *'    # Primary: 1:00 AM UTC
  - cron: '30 4 * * *'   # Backup: 4:30 AM UTC
```

## Pushover Notifications

The workflow sends Pushover notifications for monitoring:

| Event | Priority | Message |
|-------|----------|---------|
| Words added | -2 (silent) | "Added X new words: WORD1 WORD2..." |
| No changes | -2 (silent) | "No new words added" |
| Failure | 0 (normal) | Error details with link to logs |

### Setup Pushover

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret** and add:
   - `PUSHOVER_USER_KEY` - Your Pushover user key
   - `PUSHOVER_API_TOKEN` - Your Pushover API token

### Test Notifications

To test that Pushover is working:

1. Go to **Actions** tab → **Update Wordle Used Words**
2. Click **Run workflow** → **Run workflow**
3. Wait ~30 seconds for completion
4. Check your Pushover app for notification:
   - If words were added: "Added X new words: ..."
   - If no changes: "No new words added"

To test failure notifications, you can temporarily break the script (e.g., change the URL) and run the workflow.

## Data Sources

The script tries these sources in order:

1. **Rock Paper Shotgun** (primary) - Most reliable, manually curated
   - Also scrapes individual daily hint pages for latest words (archive can be slow to update)
2. **NYT Wordle** (backup) - Direct from source code
3. **Wordle Archive** (fallback) - Community-maintained

If all fail, it keeps the existing word list.

## Monitoring

### Check if it's working:

1. **Pushover notifications** - Receive daily updates on new words or failures
2. **View Actions tab** - See all workflow runs
3. **Check commit history** - Should see daily commits
4. **App Settings** - Shows "Last updated" time

### If updates stop:

1. Go to **Actions** tab
2. Check latest workflow run
3. Click on it to see logs
4. Look for error messages

Common issues:
- Website structure changed (update script)
- Rate limiting (rare, GitHub Actions has good IP reputation)
- Authentication needed (unlikely for these sources)

## Manual Update

If automatic updates fail, you can manually update:

1. Edit `used-words.json` directly on GitHub
2. Or run script locally:
   ```bash
   pip install -r requirements.txt
   python update-used-words.py
   git add used-words.json
   git commit -m "Manual update"
   git push
   ```

## Backup Strategy

The script has multiple fallbacks:
1. Primary source fails → Try backup sources
2. All sources fail → Keep existing words
3. Invalid data → Skip update

Your app also has fallbacks:
1. Server unreachable → Use cached words
2. No cache → Use bundled words

## Privacy & Security

- ✅ No API keys needed
- ✅ No personal data collected
- ✅ Public data sources only
- ✅ Version controlled (can rollback)

## Cost

**FREE** ✅
- GitHub Actions: Free for public repos, 2000 min/month for private
- This workflow uses ~1 minute per day = 30 min/month
- Well under free tier limits

## Troubleshooting

### "Workflow not running automatically"
- Check Settings → Actions → Enable workflows
- Verify cron schedule syntax
- Wait up to 24 hours for first run

### "Permission denied when pushing"
- Settings → Actions → Enable write permissions

### "Script finds no words"
- Websites may have changed structure
- Update the scraping logic in `update-used-words.py`

### "App shows old data"
- Check GitHub repo has latest commit
- Verify URL in app matches GitHub raw URL
- Clear app and reinstall

## Contact

Questions? mail@robertpowell.com

---

**Status:** 🟢 Active
**Last Updated:** 2026-01-04
