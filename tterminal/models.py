"""
Data models for the TODO list application
"""

from dataclasses import dataclass, asdict, field
from enum import Enum
from typing import List, Dict, Any
from datetime import datetime
import json
import os


class Priority(Enum):
    """Priority levels based on Eisenhower Matrix"""
    URGENT_IMPORTANT = 1    # Do First (Red)
    NOT_URGENT_IMPORTANT = 2    # Schedule (Orange) 
    URGENT_NOT_IMPORTANT = 3    # Delegate (Yellow)
    NOT_URGENT_NOT_IMPORTANT = 4    # Eliminate (Green)
    
    @property
    def label(self) -> str:
        labels = {
            Priority.URGENT_IMPORTANT: "Urgent & Important",
            Priority.NOT_URGENT_IMPORTANT: "Important, Not Urgent", 
            Priority.URGENT_NOT_IMPORTANT: "Urgent, Not Important",
            Priority.NOT_URGENT_NOT_IMPORTANT: "Not Urgent, Not Important"
        }
        return labels[self]
    
    @property
    def color(self) -> str:
        colors = {
            Priority.URGENT_IMPORTANT: "red",
            Priority.NOT_URGENT_IMPORTANT: "orange",
            Priority.URGENT_NOT_IMPORTANT: "yellow", 
            Priority.NOT_URGENT_NOT_IMPORTANT: "green"
        }
        return colors[self]


class Status(Enum):
    """Task status for kanban board"""
    TODO = "todo"
    DOING = "doing" 
    DONE = "done"


@dataclass
class Task:
    """A TODO task with priority classification"""
    id: str
    title: str
    description: str = ""
    priority: Priority = Priority.NOT_URGENT_NOT_IMPORTANT
    status: Status = Status.TODO
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for serialization"""
        data = asdict(self)
        data['priority'] = self.priority.value
        data['status'] = self.status.value
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create task from dictionary"""
        data['priority'] = Priority(data['priority'])
        data['status'] = Status(data['status'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)
    
    def update(self, **kwargs):
        """Update task fields and timestamp"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()


class TaskManager:
    """Manages tasks and persistence"""
    
    def __init__(self, data_file: str = None):
        if data_file is None:
            home = os.path.expanduser("~")
            data_dir = os.path.join(home, ".tterminal")
            os.makedirs(data_dir, exist_ok=True)
            data_file = os.path.join(data_dir, "tasks.json")
        
        self.data_file = data_file
        self.tasks: List[Task] = []
        self.load_tasks()
    
    def load_tasks(self):
        """Load tasks from file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.tasks = [Task.from_dict(task_data) for task_data in data]
            except (json.JSONDecodeError, KeyError, ValueError):
                # If file is corrupted, start fresh
                self.tasks = []
    
    def save_tasks(self):
        """Save tasks to file"""
        data = [task.to_dict() for task in self.tasks]
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_task(self, task: Task):
        """Add a new task"""
        self.tasks.append(task)
        self.save_tasks()
    
    def get_task(self, task_id: str) -> Task:
        """Get task by ID"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        raise ValueError(f"Task with ID {task_id} not found")
    
    def update_task(self, task_id: str, **kwargs):
        """Update a task"""
        task = self.get_task(task_id)
        task.update(**kwargs)
        self.save_tasks()
    
    def delete_task(self, task_id: str):
        """Delete a task"""
        self.tasks = [task for task in self.tasks if task.id != task_id]
        self.save_tasks()
    
    def get_tasks_by_status(self, status: Status) -> List[Task]:
        """Get tasks by status"""
        return [task for task in self.tasks if task.status == status]
    
    def sort_tasks_by_priority(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by priority (urgent+important first)"""
        return sorted(tasks, key=lambda t: t.priority.value)
    
    def sort_tasks_by_date(self, tasks: List[Task], reverse: bool = True) -> List[Task]:
        """Sort tasks by creation date"""
        return sorted(tasks, key=lambda t: t.created_at, reverse=reverse)