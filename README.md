# tterminal

A TUI kanban TODO list application with priority classification using the Eisenhower Matrix.

## Features

- 📝 **Kanban Board**: Organize tasks in Todo, Doing, and Done columns
- ⚡ **Priority Classification**: Use the Eisenhower Matrix to prioritize tasks
  - Urgent & Important (Do First)
  - Important, Not Urgent (Schedule)
  - Urgent, Not Important (Delegate)
  - Not Urgent, Not Important (Eliminate)
- 🔧 **Task Management**: Create, edit, and delete tasks
- 📊 **Sorting**: Toggle between priority and date sorting
- 💾 **Persistence**: Tasks are automatically saved locally
- ⌨️ **Keyboard Navigation**: Full keyboard control

## Installation

Install from PyPI (once published):

```bash
pip install tterminal
```

Or install from source:

```bash
git clone https://github.com/HanzCEO/t.git
cd t
pip install -e .
```

## Usage

Launch the application:

```bash
tterminal
```

### Key Bindings

- **`n`**: Create a new task
- **`q`**: Quit the application
- **`s`**: Toggle sorting between priority and date
- **`esc`**: Exit current modal/dialog or focus main board
- **Click on task**: Edit existing task

### Creating Tasks

1. Press `n` to open the new task dialog
2. Enter a task title (required)
3. Optionally add a description
4. Select priority using the Eisenhower Matrix:
   - **Urgent & Important**: Critical tasks requiring immediate attention
   - **Important, Not Urgent**: Important tasks to schedule for later
   - **Urgent, Not Important**: Tasks that can be delegated
   - **Not Urgent, Not Important**: Tasks that can be eliminated
5. Click "Create" or press Enter to save

### Editing Tasks

1. Click on any task to open the edit dialog
2. Modify title, description, priority, or status
3. Change status to move tasks between columns (Todo ↔ Doing ↔ Done)
4. Click "Save" to update or "Delete" to remove the task

### Sorting

Press `s` to toggle between:
- **Priority sorting**: Orders tasks by Eisenhower Matrix priority
- **Date sorting**: Orders tasks by creation date (newest first)

## Data Storage

Tasks are automatically saved to `~/.tterminal/tasks.json` and persist between sessions.

## Author

**Haxors** - hanzhaxors@gmail.com

## License

MIT License
