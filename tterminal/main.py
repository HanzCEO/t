"""
Main TUI application using Textual
"""

import uuid
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Button, Input, TextArea, Select
from textual.screen import Screen, ModalScreen
from textual.binding import Binding
from typing import List, Optional

from .models import Task, TaskManager, Priority, Status


class TaskWidget(Static):
    """A widget representing a single task"""
    
    def __init__(self, task: Task, **kwargs):
        super().__init__(**kwargs)
        self.task = task
        self.can_focus = True
    
    def render(self) -> str:
        """Render the task"""
        priority_indicator = "●" if self.task.priority != Priority.NOT_URGENT_NOT_IMPORTANT else "○"
        return f"[{self.task.priority.color}]{priority_indicator}[/] {self.task.title}"
    
    def on_click(self) -> None:
        """Handle task click for editing"""
        self.app.push_screen(EditTaskScreen(self.task))


class KanbanColumn(Container):
    """A column in the kanban board"""
    
    def __init__(self, title: str, status: Status, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.status = status
        self.tasks: List[TaskWidget] = []
    
    def compose(self) -> ComposeResult:
        """Compose the column"""
        yield Static(f"[bold]{self.title}[/]", classes="column-header")
        yield Container(id=f"tasks-{self.status.value}", classes="task-container")
    
    def add_task(self, task: Task):
        """Add a task to this column"""
        task_widget = TaskWidget(task, classes="task-item")
        self.tasks.append(task_widget)
        container = self.query_one(f"#tasks-{self.status.value}")
        container.mount(task_widget)
    
    def clear_tasks(self):
        """Clear all tasks from the column"""
        container = self.query_one(f"#tasks-{self.status.value}")
        container.remove_children()
        self.tasks.clear()


class NewTaskScreen(Screen[Task]):
    """Screen for creating a new task"""
    
    BINDINGS = [
        Binding("escape", "dismiss", "Cancel"),
    ]
    
    def compose(self) -> ComposeResult:
        """Compose the new task screen"""
        yield Static("[bold]Create New Task[/]")
        yield Input(placeholder="Task title (required)", id="title-input")
        yield Static("Description:")
        yield TextArea("", placeholder="Optional task description", id="description-input")
        yield Static("[bold]Priority (Eisenhower Matrix)[/]")
        yield Select([
            ("Urgent & Important (Do First)", Priority.URGENT_IMPORTANT),
            ("Important, Not Urgent (Schedule)", Priority.NOT_URGENT_IMPORTANT), 
            ("Urgent, Not Important (Delegate)", Priority.URGENT_NOT_IMPORTANT),
            ("Not Urgent, Not Important (Eliminate)", Priority.NOT_URGENT_NOT_IMPORTANT)
        ], id="priority-select", value=Priority.NOT_URGENT_NOT_IMPORTANT)
        yield Button("Create", variant="primary", id="create-button")
        yield Button("Cancel", variant="default", id="cancel-button")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "create-button":
            self.create_task()
        elif event.button.id == "cancel-button":
            self.dismiss()
    
    def create_task(self):
        """Create a new task"""
        title_input = self.query_one("#title-input", Input)
        description_input = self.query_one("#description-input", TextArea)
        priority_select = self.query_one("#priority-select", Select)
        
        title = title_input.value.strip()
        if not title:
            return  # Don't create empty tasks
        
        description = description_input.text.strip()
        priority = priority_select.value
        
        task = Task(
            id=str(uuid.uuid4()),
            title=title,
            description=description,
            priority=priority
        )
        
        # Add to task manager
        self.app.task_manager.add_task(task)
        
        # Refresh the main screen
        self.app.refresh_tasks(force=True)
        
        self.dismiss()


class EditTaskScreen(Screen[Task]):
    """Screen for editing an existing task"""
    
    BINDINGS = [
        Binding("escape", "dismiss", "Cancel"),
    ]
    
    def __init__(self, task: Task, **kwargs):
        super().__init__(**kwargs)
        self.task = task
    
    def compose(self) -> ComposeResult:
        """Compose the edit task screen"""
        yield Static("[bold]Edit Task[/]")
        yield Input(value=self.task.title, id="title-input")
        yield Static("Description:")
        yield TextArea(self.task.description, id="description-input")
        yield Static("[bold]Priority[/]")
        yield Select([
            ("Urgent & Important (Do First)", Priority.URGENT_IMPORTANT),
            ("Important, Not Urgent (Schedule)", Priority.NOT_URGENT_IMPORTANT), 
            ("Urgent, Not Important (Delegate)", Priority.URGENT_NOT_IMPORTANT),
            ("Not Urgent, Not Important (Eliminate)", Priority.NOT_URGENT_NOT_IMPORTANT)
        ], id="priority-select", value=self.task.priority)
        yield Static("[bold]Status[/]")
        yield Select([
            ("Todo", Status.TODO),
            ("Doing", Status.DOING),
            ("Done", Status.DONE)
        ], id="status-select", value=self.task.status)
        yield Button("Save", variant="primary", id="save-button")
        yield Button("Delete", variant="error", id="delete-button")
        yield Button("Cancel", variant="default", id="cancel-button")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "save-button":
            self.save_task()
        elif event.button.id == "delete-button":
            self.delete_task()
        elif event.button.id == "cancel-button":
            self.dismiss()
    
    def save_task(self):
        """Save task changes"""
        title_input = self.query_one("#title-input", Input)
        description_input = self.query_one("#description-input", TextArea)
        priority_select = self.query_one("#priority-select", Select)
        status_select = self.query_one("#status-select", Select)
        
        title = title_input.value.strip()
        if not title:
            return  # Don't save empty titles
        
        # Update the task
        self.app.task_manager.update_task(
            self.task.id,
            title=title,
            description=description_input.text.strip(),
            priority=priority_select.value,
            status=status_select.value
        )
        
        # Refresh the main screen
        self.app.refresh_tasks(force=True)
        
        self.dismiss()
    
    def delete_task(self):
        """Delete the task"""
        self.app.task_manager.delete_task(self.task.id)
        self.app.refresh_tasks(force=True)
        self.dismiss()


class TodoApp(App):
    """Main TODO application"""
    
    CSS = """
    /* Main application styles */
    
    Screen {
        background: $surface;
    }
    
    #kanban-board {
        padding: 1;
        height: 100%;
    }
    
    .kanban-column {
        border: solid $primary;
        width: 1fr;
        margin: 0 1;
        padding: 1;
        background: $panel;
    }
    
    .column-header {
        text-align: center;
        background: $primary;
        color: $text;
        padding: 1;
        margin-bottom: 1;
    }
    
    .task-container {
        height: 100%;
        overflow-y: auto;
    }
    
    .task-item {
        border: solid $secondary;
        margin: 1 0;
        padding: 1;
        background: $surface;
        color: $text;
    }
    
    .task-item:hover {
        background: $accent;
        border: solid $accent;
    }
    
    .task-item:focus {
        border: solid $warning;
        background: $warning 10%;
    }
    
    /* Form elements */
    Input, TextArea, Select {
        margin: 1 0;
    }
    
    TextArea {
        height: 5;
        max-height: 10;
    }
    """
    
    TITLE = "TTerm - Kanban TODO List"
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("n", "new_task", "New Task"),
        Binding("escape", "focus_board", "Focus Board"),
        Binding("s", "toggle_sort", "Toggle Sort"),
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.task_manager = TaskManager()
        self.sort_by_priority = True  # Default sorting
        self._last_task_count = 0  # Cache for performance
    
    def compose(self) -> ComposeResult:
        """Compose the main application"""
        yield Header()
        yield Footer()
        
        with Horizontal(id="kanban-board"):
            self.todo_column = KanbanColumn("📝 TODO", Status.TODO, classes="kanban-column")
            self.doing_column = KanbanColumn("⚡ DOING", Status.DOING, classes="kanban-column")
            self.done_column = KanbanColumn("✅ DONE", Status.DONE, classes="kanban-column")
            
            yield self.todo_column
            yield self.doing_column  
            yield self.done_column
    
    def on_mount(self) -> None:
        """Called when app is mounted"""
        self.refresh_tasks()
    
    def on_unmount(self) -> None:
        """Called when app is unmounted - ensure data is saved"""
        self.task_manager.force_save()
    
    def refresh_tasks(self, force: bool = False):
        """Refresh all tasks in the kanban board (with performance optimization)"""
        current_task_count = len(self.task_manager.tasks)
        
        # Only refresh if task count changed or forced
        if not force and current_task_count == self._last_task_count:
            return
            
        self._last_task_count = current_task_count
        
        # Clear all columns
        self.todo_column.clear_tasks()
        self.doing_column.clear_tasks()
        self.done_column.clear_tasks()
        
        # Get tasks by status and sort them
        for status in Status:
            tasks = self.task_manager.get_tasks_by_status(status)
            
            if self.sort_by_priority:
                tasks = self.task_manager.sort_tasks_by_priority(tasks)
            else:
                tasks = self.task_manager.sort_tasks_by_date(tasks)
            
            # Add to appropriate column
            if status == Status.TODO:
                for task in tasks:
                    self.todo_column.add_task(task)
            elif status == Status.DOING:
                for task in tasks:
                    self.doing_column.add_task(task)
            elif status == Status.DONE:
                for task in tasks:
                    self.done_column.add_task(task)
    
    def action_new_task(self) -> None:
        """Create a new task"""
        self.push_screen(NewTaskScreen())
    
    def action_focus_board(self) -> None:
        """Focus on the main board (escape from modals), or quit if no modals are open"""
        # Check if there are any modal screens active
        if len(self.screen_stack) <= 1:
            # No modals are open, so quit the application
            self.exit()
        # If modals are open, this action will be handled by the modal screens themselves
    
    def action_toggle_sort(self) -> None:
        """Toggle between priority and date sorting"""
        self.sort_by_priority = not self.sort_by_priority
        self.refresh_tasks(force=True)
        sort_type = "priority" if self.sort_by_priority else "date"
        self.notify(f"Sorting by {sort_type}")


def main():
    """Main entry point"""
    app = TodoApp()
    app.run()


if __name__ == "__main__":
    main()