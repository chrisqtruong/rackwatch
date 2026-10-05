# Launch steps

About 15 minutes. Do them in order.

## 0. Give Rackwatch its own repository

This session could not create a GitHub repository, so Rackwatch arrived as the `rackwatch/` folder in the Bankrolled pull request. Move it out first:

1. Go to https://github.com/new. Owner **chrisqtruong**, name **rackwatch**, **Public**. Leave "Add a README", .gitignore and license **unchecked**. Click **Create repository**.
2. On your computer:
   ```bash
   git clone https://github.com/chrisqtruong/bankrolled && cd bankrolled
   git fetch origin claude/friendly-curie-trafef && git checkout claude/friendly-curie-trafef
   git subtree split -P rackwatch -b rackwatch-only
   git push https://github.com/chrisqtruong/rackwatch rackwatch-only:main
   ```
   The new repo now has the full site, data and the Wire workflow at its root, with history.
3. You can then delete the `rackwatch/` folder from the Bankrolled pull request (the kit fixes and `tracker-kit/examples/tech-power.json` stay).

All remaining steps are in **github.com/chrisqtruong/rackwatch**.

## 1. Turn on GitHub Pages

1. **Settings** (top tab) → **Pages** (left sidebar).
2. Under "Build and deployment", Source: **Deploy from a branch**.
3. Branch: **main**, folder: **/docs**. Click **Save**.
4. Wait 1 to 2 minutes, reload. The page shows "Your site is live at https://chrisqtruong.github.io/rackwatch/".

## 2. Let the Wire workflow push

1. **Settings** → **Actions** → **General**.
2. "Actions permissions": **Allow all actions and reusable workflows** (the default).
3. Scroll to "Workflow permissions": choose **Read and write permissions**. Click **Save**.

## 3. Start the Wire and confirm it is running

1. **Actions** tab. If GitHub asks, click **I understand my workflows, go ahead and enable them**.
2. Click **Wire** in the left list → **Run workflow** (right) → **Run workflow**.
3. After about a minute the run shows a green check. Open it → **poll** → "Poll feeds" prints `changed=true new=N polled=M`.
4. Click the **Code** tab: the latest commit is "Wire 2026-…Z" by wire-bot, touching `docs/wire.json`.
5. Open the site: the header says "Wire updated X min ago" with a green dot, and the Wire tab lists headlines.
6. From then on, the **Actions** tab shows a new Wire run every 5 to 15 minutes (GitHub delays scheduled runs when busy). Runs with nothing new end green without a commit; that is normal.
7. Source health: open `docs/wire-status.json` on the site. Any source with `"ok": false` shows its error. To switch one off, set `"on": false` for it in `wire-sources.json`.

Note: GitHub pauses scheduled workflows in a repository with no activity for 60 days. The hourly routine's commits keep it active; if the routine stops, re-enable the Wire on the Actions tab.

## 4. Turn on Discussions and giscus comments

1. **Settings** → **General** → scroll to "Features" → tick **Discussions**.
2. Install the giscus app: open https://github.com/apps/giscus → **Install** (or **Configure**) → **Only select repositories** → pick **rackwatch** → **Install**.
3. Open https://giscus.app. In "Repository" type `chrisqtruong/rackwatch`; it should say "Success! This repository meets all of the above criteria."
4. "Page ↔ Discussions Mapping": choose **Discussion title contains a specific term** (the page passes "post <id>" for each post).
5. "Discussion Category": choose **Announcements** (only you and giscus can start threads; anyone signed in can reply). Tick **Only search for discussions in this category**.
6. Scroll to "Enable giscus". In the script shown, copy the two values:
   - `data-repo-id="R_…"`
   - `data-category-id="DIC_…"`
7. In the repo, edit `tracker.config.json` → `"giscus"`: replace `GISCUS_REPO_ID` and `GISCUS_CATEGORY_ID` with those values. Do the same in `docs/config.json` (or run `python3 scripts/sync_config.py`). Commit to main.
8. Reload the site: each post now has a **Discuss** button. Until step 7 is done, the button is hidden.

## 5. Create the scheduled verification task

1. Open https://claude.ai/code → **Routines** (left sidebar; in Claude Code you can also type `/schedule`). Click **New routine**.
2. Name: **Rackwatch hourly check**.
3. Prompt: paste everything below the line in `ROUTINE-PROMPT.md`.
4. Repository: **chrisqtruong/rackwatch**. Allow it to push to **main** (the routine commits directly, like Bankrolled's).
5. Schedule: **Hourly** (the shortest interval the scheduler allows; pick a lower interval only if your plan offers one). Connectors: add **Firecrawl** if it is available to you; many sources are only readable through it.
6. Save, then click **Run now** once.
7. Check: a commit "Update 2026-… HH:MM" appears, `reports/<today>.md` has a "Check at HH:MM ET" section, and the site header says "Verified feed updated X min ago".

## 6. Final checks

- Open https://chrisqtruong.github.io/rackwatch/#p-2026-09-25-tiktok-settles-alabama-youthsafety-suit-for-at (or any permalink from a report): the page scrolls to that post.
- The **Actions** tab shows a green "Check data" run for the last push (it runs `scripts/validate.py`).
- Add Rackwatch to your site's project list if you want it there. The only link between Rackwatch and Bankrolled is the footer line.
