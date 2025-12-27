# Git Quick Reference for Manège

Simple commands for updating your GitHub repository.

## Every Time You Make Changes

### 1. Check what changed
```bash
cd /home/florine/manege
git status
```

### 2. See exactly what changed
```bash
git diff
```

### 3. Add all changes
```bash
git add .
```

### 4. Commit with a message
```bash
git commit -m "Brief description of what you changed"
```

### 5. Push to GitHub
```bash
git push
```

---

## Common Workflows

### After a coding session with Claude:
```bash
cd /home/florine/manege
git add .
git commit -m "Add focus stacking feature"
git push
```

### After fixing a bug:
```bash
git add .
git commit -m "Fix turntable homing issue"
git push
```

### After updating documentation:
```bash
git add .
git commit -m "Update README with new features"
git push
```

---

## Viewing History

### See recent commits
```bash
git log --oneline
```

### See what changed in last commit
```bash
git show
```

---

## Going Back in Time

### Undo changes before commit (careful!)
```bash
git checkout -- filename.py
```

### See old version without changing anything
```bash
git log --oneline           # Find commit hash
git show abc123:app/app.py  # View old version
```

---

## Working with Claude Code

When Claude Code helps you:

1. Make changes to your code
2. When done with session:
   ```bash
   git add .
   git commit -m "Session YYYY-MM-DD: [what we did]"
   git push
   ```

Example commit messages:
- "Session 2025-12-27: Add HDR capture mode"
- "Session 2025-12-28: Fix ESP32 WiFi reconnection"
- "Session 2025-12-29: Improve focus stacking algorithm"

---

## Safety Rules ⚠️

✅ **DO:**
- Commit often (every significant change)
- Write clear commit messages
- Push to GitHub regularly

❌ **DON'T:**
- Commit config.py or config.h (git will ignore them automatically)
- Commit photos or large files
- Force push (--force) unless you know what you're doing

---

## Check Repository Status Anytime

**On web:** https://github.com/fitaine/manege

**On Pi:**
```bash
cd /home/florine/manege
git status
git log --oneline -5  # Last 5 commits
```

---

## Troubleshooting

### "Nothing to commit"
Good! No changes since last commit.

### "Your branch is ahead"
You have local commits not pushed yet. Run: `git push`

### "Conflict" when pushing
Someone else changed the same file. Contact Claude for help!

### Forgot to commit before making more changes
No problem! Just commit now with all changes together.

---

**Remember:** Git is your friend! It's hard to lose work with git. When in doubt, ask Claude! 😊
