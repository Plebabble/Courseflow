# Assignment Planner

On Windows, double-click `Launch Planner.pyw` to open the planner in its own desktop window. The first launch prepares its private Python environment and may take a few minutes; it needs an internet connection to download the required packages. Later launches open directly. No browser tab or command window is needed.

The launcher requires Python 3.10 or newer and the Microsoft Edge WebView2 Runtime.

If startup fails, check `planner_launcher.log` and `planner_startup.log` in this folder for details.

Keep `assignments.json` and, if you use calendar scheduling, `calendar.ics` in this folder. The app saves assignments, course settings, appearance choices, and lecture-task progress to `assignments.json`.

These local planner files contain personal information and are excluded from GitHub by `.gitignore`, along with exported backups, CSV files, logs, secrets, and the local Python environment. Each person who downloads the app uses their own local planner data.

The sidebar shows estimated free time for each day. Estimates use calendar busy time across the full day and reserve eight hours for sleep; when no calendar is imported, the estimate is 16 hours. Scheduling distributes assignment work in proportion to each day's available hours. The Today tab shows your assignments and class tasks for the day.

Use the **Courses** tab to add, rename, recolor, and remove course/category labels, set meeting days, and export backups. Course names, colors, meeting days, lecture-prep timing, and lecture-review timing save automatically when edited. For each course, choose no lecture prep or schedule it from the same day through 14 days before class. Set lecture notes review for the same day through 14 days after class. The separate **Appearance** tab includes Beige, Forest green, Mint, Pink, Dark mode, Autumn, Lavender, Ocean, Peach, Buttercup, Berry, Slate, Terracotta, and Monochrome presets, plus controls to customize each color individually, including dropdowns, hover highlights, and progress bars. Assignment lists are grouped under collapsed **Current assignments** and **Completed assignments** sections.

When creating an assignment, turn on **This assignment repeats** to set up a series of assignments together. Give each occurrence its own name and due date. Each start date defaults to the previous occurrence's due date (the first starts today), and every start date remains editable.

The **Class & Test Prep** tab has a central topic manager: choose a course and its class date to add, rename, or delete topics. Topic dates must fall on one of the course's configured meeting days. Color-coded course dropdowns below it show each course's saved topics and class dates. Set course meeting days, prep timing, and review timing in the **Courses** tab. The **Today** tab shows compact, course-colored lecture-prep and lecture-notes-review tasks on the selected days; unfinished tasks carry forward until marked done. Spaced-repetition practice is managed separately in Anki.

In **Schedule**, switch between the existing list and a rounded calendar with weekly and monthly views. Assignment blocks and class-prep/review blocks use each course's saved color, while calendar surfaces use the selected appearance palette.

The planner keeps its selected theme and pastel course colors in local data.
