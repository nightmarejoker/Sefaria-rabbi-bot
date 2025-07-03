# How to Upload Your Discord Bot to GitHub

## Method 1: Using GitHub Web Interface (Easiest)

### Step 1: Create a GitHub Repository
1. Go to [github.com](https://github.com) and sign in (or create an account)
2. Click the green "New" button or go to [github.com/new](https://github.com/new)
3. Fill in repository details:
   - **Repository name**: `sefaria-discord-bot` (or any name you prefer)
   - **Description**: "Discord bot for accessing Jewish texts from Sefaria"
   - **Visibility**: Choose Public or Private
   - **Initialize**: Leave unchecked (we'll upload existing code)
4. Click "Create repository"

### Step 2: Download Your Code from Replit
1. In Replit, click the three dots menu (⋮) next to your project name
2. Select "Download as ZIP"
3. Extract the ZIP file on your computer

### Step 3: Upload Files to GitHub
1. On your new GitHub repository page, click "uploading an existing file"
2. Drag and drop these files from your extracted folder:
   - `main.py`
   - `Procfile`
   - `pyproject.toml`
   - `README.md`
   - `.gitignore`
   - `.env.example`
   - The entire `bot/` folder
3. Write a commit message: "Initial commit: Sefaria Discord Bot"
4. Click "Commit changes"

## Method 2: Using Git Commands (Advanced)

If you're comfortable with command line:

```bash
# Download and extract your Replit project first

# Initialize git repository
git init
git add .
git commit -m "Initial commit: Sefaria Discord Bot"

# Connect to GitHub (replace with your repository URL)
git remote add origin https://github.com/yourusername/sefaria-discord-bot.git
git branch -M main
git push -u origin main
```

## Method 3: Using Replit's GitHub Integration

1. In Replit, go to the "Version Control" tab (git icon on left sidebar)
2. Click "Create a Git repository"
3. Connect to GitHub when prompted
4. Create a new repository or connect to existing one
5. Commit and push your changes

## Files to Include

Make sure these files are uploaded:
- ✅ `main.py` - Main application
- ✅ `bot/` folder - All bot code
- ✅ `Procfile` - For deployment
- ✅ `pyproject.toml` - Dependencies
- ✅ `README.md` - Documentation
- ✅ `.gitignore` - Ignore sensitive files
- ✅ `.env.example` - Environment template

## Files to NEVER Upload

These files contain secrets and should never be uploaded:
- ❌ `.env` - Contains your actual tokens
- ❌ `sefaria_bot.log` - Log files
- ❌ `.replit` - Replit-specific config

## After Upload

1. Your repository will be available at: `https://github.com/yourusername/sefaria-discord-bot`
2. You can now deploy to Heroku, Railway, or other platforms using this GitHub repository
3. Remember to set environment variables on your hosting platform:
   - `DISCORD_TOKEN`
   - `OPENAI_API_KEY`

## Next Steps

Once uploaded to GitHub, you can:
1. Deploy to Heroku using GitHub integration
2. Set up automatic deployments
3. Collaborate with others
4. Track changes and versions