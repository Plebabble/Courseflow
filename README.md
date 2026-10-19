# Assignment Planner

On Windows, double-click `Launch Planner.pyw` to open the planner in its own desktop window. The first launch prepares its private Python environment and may take a few minutes; it needs an internet connection to download the required packages. Later launches open directly. No browser tab or command window is needed.

The launcher requires Python 3.10 or newer and the Microsoft Edge WebView2 Runtime.

If startup fails, check `planner_launcher.log` and `planner_startup.log` in this folder for details.

Keep `assignments.json` and, if you use calendar scheduling, `calendar.ics` in this folder. The app saves assignments and daily availability overrides to `assignments.json`.

These local planner files contain personal information and are excluded from GitHub by `.gitignore`, along with exported backups, CSV files, logs, secrets, and the local Python environment. Each person who downloads the app uses their own local planner data.

The sidebar displays estimated free hours by date and allows date-by-date overrides. Use the reset button to return to calendar estimates. Scheduling distributes assignment work in proportion to each day's available hours. The Today tab shows your assignments for the day, and Schedule shows upcoming assignment work. Availability defaults and waking hours are saved with your planner data; the fallback settings are tucked into a collapsed sidebar section.

Use the **Data** tab to customize the app theme, add/rename/recolor/remove course/category labels, and export backups. Theme colors cover the page, sidebar and panels, buttons, assignment cards, input fields, text, and borders. Assignment lists are grouped under collapsed **Current assignments** and **Completed assignments** sections.

The **Class & Test Prep** tab has a central topic manager: choose a course and its class date to add, rename, or delete topics. Topic dates must fall on one of the course's configured meeting days. Color-coded course dropdowns below it show each course's saved topics and class dates. Set or change course meeting days in the **Data** tab alongside course names and colors. The **Today** tab shows a compact, course-colored lecture-prep task before the next class and a lecture-notes-review task after the previous class; unfinished tasks carry forward until marked done. When completing a lecture notes review, record its color as red, orange, yellow, or green. This records the result only; it does not schedule spaced reviews yet. The **Schedule** tab lists upcoming class-prep and review tasks alongside assignment work.

The planner keeps its warm cream background and pastel course colors.
