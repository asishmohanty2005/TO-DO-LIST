import tkinter as tk
from tkinter import messagebox, font, colorchooser, ttk
from tkinter.simpledialog import askstring
from datetime import datetime, date
import json
import os
from collections import defaultdict

# File to store tasks
DATA_FILE = "todo_list_advanced.json"

class ToDoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced To-Do List")
        self.root.geometry("800x700")
        
        # Task list storage
        self.tasks = []
        
        # Current filter and search
        self.current_filter = "All"
        self.search_term = ""
        
        # Placeholder flag
        self.placeholder_active = True
        
        # Color theme
        self.current_theme = "Default"
        self.themes = {
            "Default": {
                "bg": "#f0f0f0",
                "fg": "#000000",
                "button_bg": "#4CAF50",
                "button_fg": "#ffffff",
                "listbox_bg": "#fefefe",
                "selected_bg": "#3498db"
            },
            "Dark": {
                "bg": "#2c3e50",
                "fg": "#ecf0f1",
                "button_bg": "#34495e",
                "button_fg": "#ecf0f1",
                "listbox_bg": "#34495e",
                "selected_bg": "#e74c3c"
            },
            "Light Blue": {
                "bg": "#e0f2fe",
                "fg": "#0c4a6e",
                "button_bg": "#0284c7",
                "button_fg": "#ffffff",
                "listbox_bg": "#ffffff",
                "selected_bg": "#38bdf8"
            },
            "Pastel": {
                "bg": "#fdf0d5",
                "fg": "#6b4e3a",
                "button_bg": "#e9b0a5",
                "button_fg": "#4a2c2a",
                "listbox_bg": "#fdf8f0",
                "selected_bg": "#c7b9a5"
            }
        }
        
        # Custom fonts
        self.title_font = font.Font(family="Segoe UI", size=14, weight="bold")
        self.task_font = font.Font(family="Segoe UI", size=11)
        
        # Create GUI
        self.create_widgets()
        self.load_tasks()
        self.update_statistics()
        
        # Bind events
        self.root.bind('<Return>', lambda e: self.add_task())
        self.root.bind('<Delete>', lambda e: self.delete_task())
        self.root.bind('<Control-f>', lambda e: self.focus_search())
        
    def create_widgets(self):
        # Top frame for title
        title_frame = tk.Frame(self.root, bg=self.themes[self.current_theme]["bg"])
        title_frame.pack(pady=10)
        tk.Label(title_frame, text="📝 Advanced Task Manager", font=self.title_font,
                bg=self.themes[self.current_theme]["bg"], fg=self.themes[self.current_theme]["fg"]).pack()
        
        # Search and filter frame
        filter_frame = tk.Frame(self.root, bg=self.themes[self.current_theme]["bg"])
        filter_frame.pack(pady=5, padx=10, fill="x")
        
        tk.Label(filter_frame, text="🔍 Search:", bg=self.themes[self.current_theme]["bg"],
                fg=self.themes[self.current_theme]["fg"]).pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(filter_frame, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<KeyRelease>', lambda e: self.search_tasks())
        
        tk.Label(filter_frame, text="📌 Filter:", bg=self.themes[self.current_theme]["bg"],
                fg=self.themes[self.current_theme]["fg"]).pack(side=tk.LEFT, padx=5)
        
        self.filter_var = tk.StringVar(value="All")
        filter_options = ["All", "Active", "Completed", "High Priority", "Medium Priority", "Low Priority", "Overdue"]
        self.filter_menu = ttk.Combobox(filter_frame, textvariable=self.filter_var, values=filter_options,
                                        state="readonly", width=15)
        self.filter_menu.pack(side=tk.LEFT, padx=5)
        self.filter_menu.bind('<<ComboboxSelected>>', lambda e: self.apply_filter())
        
        # Add task frame
        add_frame = tk.Frame(self.root, bg=self.themes[self.current_theme]["bg"])
        add_frame.pack(pady=10, padx=10, fill="x")
        
        self.task_entry = tk.Entry(add_frame, font=self.task_font, width=30)
        self.task_entry.pack(side=tk.LEFT, padx=(0, 10), expand=True, fill="x")
        
        # Priority dropdown
        tk.Label(add_frame, text="Priority:", bg=self.themes[self.current_theme]["bg"],
                fg=self.themes[self.current_theme]["fg"]).pack(side=tk.LEFT, padx=5)
        self.priority_var = tk.StringVar(value="Medium")
        priority_menu = ttk.Combobox(add_frame, textvariable=self.priority_var,
                                     values=["High", "Medium", "Low"], state="readonly", width=8)
        priority_menu.pack(side=tk.LEFT, padx=5)
        
        # Due date entry
        tk.Label(add_frame, text="Due Date:", bg=self.themes[self.current_theme]["bg"],
                fg=self.themes[self.current_theme]["fg"]).pack(side=tk.LEFT, padx=5)
        self.due_date_entry = tk.Entry(add_frame, width=12)
        self.due_date_entry.pack(side=tk.LEFT, padx=5)
        
        self.add_btn = tk.Button(add_frame, text="Add Task", command=self.add_task,
                                bg=self.themes[self.current_theme]["button_bg"],
                                fg=self.themes[self.current_theme]["button_fg"],
                                font=("Segoe UI", 10, "bold"), padx=15, pady=5)
        self.add_btn.pack(side=tk.RIGHT)
        
        # Listbox frame with scrollbar
        list_frame = tk.Frame(self.root)
        list_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.task_listbox = tk.Listbox(list_frame, font=self.task_font,
                                      yscrollcommand=scrollbar.set,
                                      selectbackground=self.themes[self.current_theme]["selected_bg"],
                                      selectforeground="white", height=15)
        self.task_listbox.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar.config(command=self.task_listbox.yview)
        
        # Right-click menu
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="✏️ Edit Task", command=self.edit_task)
        self.context_menu.add_command(label="✅ Mark Complete", command=self.complete_task)
        self.context_menu.add_command(label="🗑 Delete", command=self.delete_task)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="📅 Change Due Date", command=self.change_due_date)
        self.context_menu.add_command(label="⚠ Change Priority", command=self.change_priority)
        self.task_listbox.bind("<Button-3>", self.show_context_menu)
        
        # Double-click edit
        self.task_listbox.bind('<Double-Button-1>', lambda e: self.edit_task())
        
        # Buttons frame
        btn_frame = tk.Frame(self.root, bg=self.themes[self.current_theme]["bg"])
        btn_frame.pack(pady=10, padx=10, fill="x")
        
        buttons = [
            ("✓ Complete", self.complete_task, "#2ecc71"),
            ("✏️ Edit", self.edit_task, "#3498db"),
            ("🗑 Delete", self.delete_task, "#e74c3c"),
            ("🎨 Theme", self.change_theme, "#9b59b6"),
            ("⚠ Clear All", self.clear_all_tasks, "#95a5a6")
        ]
        
        for text, command, color in buttons:
            btn = tk.Button(btn_frame, text=text, command=command,
                          bg=color, fg="white", font=("Segoe UI", 9, "bold"),
                          padx=15, pady=5)
            btn.pack(side=tk.LEFT, padx=5)
        
        # Statistics frame
        self.stats_frame = tk.Frame(self.root, bg=self.themes[self.current_theme]["bg"],
                                   relief=tk.RIDGE, bd=2)
        self.stats_frame.pack(pady=10, padx=10, fill="x")
        
        self.stats_label = tk.Label(self.stats_frame, text="📊 Statistics Dashboard", font=("Segoe UI", 10, "bold"),
                                   bg=self.themes[self.current_theme]["bg"],
                                   fg=self.themes[self.current_theme]["fg"])
        self.stats_label.pack(pady=5)
        
        self.stats_details = tk.Label(self.stats_frame, text="", font=("Segoe UI", 9),
                                     bg=self.themes[self.current_theme]["bg"],
                                     fg=self.themes[self.current_theme]["fg"], justify=tk.LEFT)
        self.stats_details.pack(pady=5)
        
        # Status label
        self.status_label = tk.Label(self.root, text="", fg="green", font=("Segoe UI", 9))
        self.status_label.pack(pady=5)
        
        self.apply_theme()
    
    def add_task(self):
        task_text = self.task_entry.get().strip()
        if not task_text:
            messagebox.showwarning("Empty Task", "Please enter a task.")
            return
        
        due_date = self.due_date_entry.get().strip()
        if due_date:
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning("Invalid Date", "Please use YYYY-MM-DD format (e.g., 2024-12-31)")
                return
        
        priority = self.priority_var.get()
        
        self.tasks.append({
            "text": task_text,
            "completed": False,
            "due_date": due_date,
            "priority": priority
        })
        
        self.update_listbox()
        self.task_entry.delete(0, tk.END)
        self.due_date_entry.delete(0, tk.END)
        self.save_tasks()
        self.update_statistics()
        self.show_status(f"✅ Added: {task_text} ({priority} priority)")
    
    def edit_task(self):
        selected = self.task_listbox.curselection()
        if not selected:
            messagebox.showinfo("No Selection", "Select a task to edit.")
            return
        
        # Get the actual task index from filtered view
        filtered_tasks = self.filter_tasks(self.tasks)
        if selected[0] >= len(filtered_tasks):
            return
        
        actual_task = filtered_tasks[selected[0]]
        original_index = self.tasks.index(actual_task)
        
        new_text = askstring("Edit Task", "Edit task description:",
                            initialvalue=actual_task["text"])
        if new_text and new_text.strip():
            self.tasks[original_index]["text"] = new_text.strip()
            self.update_listbox()
            self.save_tasks()
            self.show_status(f"✏️ Task updated: {new_text}")
    
    def change_due_date(self):
        selected = self.task_listbox.curselection()
        if not selected:
            messagebox.showinfo("No Selection", "Select a task first.")
            return
        
        filtered_tasks = self.filter_tasks(self.tasks)
        if selected[0] >= len(filtered_tasks):
            return
        
        actual_task = filtered_tasks[selected[0]]
        original_index = self.tasks.index(actual_task)
        
        new_date = askstring("Due Date", "Enter due date (YYYY-MM-DD):\nLeave empty to remove due date.",
                            initialvalue=actual_task["due_date"])
        if new_date is not None:
            if new_date == "":
                self.tasks[original_index]["due_date"] = ""
                self.show_status("📅 Due date removed")
            else:
                try:
                    datetime.strptime(new_date, "%Y-%m-%d")
                    self.tasks[original_index]["due_date"] = new_date
                    self.show_status(f"📅 Due date set to {new_date}")
                except ValueError:
                    messagebox.showwarning("Invalid Date", "Use YYYY-MM-DD format")
                    return
            self.update_listbox()
            self.save_tasks()
            self.update_statistics()
    
    def change_priority(self):
        selected = self.task_listbox.curselection()
        if not selected:
            messagebox.showinfo("No Selection", "Select a task first.")
            return
        
        filtered_tasks = self.filter_tasks(self.tasks)
        if selected[0] >= len(filtered_tasks):
            return
        
        actual_task = filtered_tasks[selected[0]]
        original_index = self.tasks.index(actual_task)
        
        # Create custom dialog for priority
        priority_window = tk.Toplevel(self.root)
        priority_window.title("Change Priority")
        priority_window.geometry("250x180")
        priority_window.resizable(False, False)
        
        tk.Label(priority_window, text="Select Priority:", font=("Segoe UI", 10)).pack(pady=10)
        priority_var = tk.StringVar(value=actual_task["priority"])
        
        for p in ["High", "Medium", "Low"]:
            tk.Radiobutton(priority_window, text=p, variable=priority_var,
                          value=p, font=("Segoe UI", 10)).pack(anchor=tk.W, padx=20)
        
        def set_priority():
            self.tasks[original_index]["priority"] = priority_var.get()
            self.update_listbox()
            self.save_tasks()
            self.update_statistics()
            self.show_status(f"⚠ Priority changed to {priority_var.get()}")
            priority_window.destroy()
        
        tk.Button(priority_window, text="Set Priority", command=set_priority,
                 bg="#3498db", fg="white", padx=15, pady=5).pack(pady=10)
    
    def delete_task(self):
        selected = self.task_listbox.curselection()
        if not selected:
            messagebox.showinfo("No Selection", "Select a task to delete.")
            return
        
        filtered_tasks = self.filter_tasks(self.tasks)
        if selected[0] >= len(filtered_tasks):
            return
        
        actual_task = filtered_tasks[selected[0]]
        original_index = self.tasks.index(actual_task)
        deleted_task = self.tasks[original_index]["text"]
        
        del self.tasks[original_index]
        self.update_listbox()
        self.save_tasks()
        self.update_statistics()
        self.show_status(f"🗑 Deleted: {deleted_task}")
    
    def complete_task(self):
        selected = self.task_listbox.curselection()
        if not selected:
            messagebox.showinfo("No Selection", "Select a task to mark complete/incomplete.")
            return
        
        filtered_tasks = self.filter_tasks(self.tasks)
        if selected[0] >= len(filtered_tasks):
            return
        
        actual_task = filtered_tasks[selected[0]]
        original_index = self.tasks.index(actual_task)
        
        self.tasks[original_index]["completed"] = not self.tasks[original_index]["completed"]
        self.update_listbox()
        self.save_tasks()
        self.update_statistics()
        
        status = "✅ Completed" if self.tasks[original_index]["completed"] else "🔄 Marked as incomplete"
        self.show_status(f"{status}: {self.tasks[original_index]['text']}")
    
    def clear_all_tasks(self):
        if not self.tasks:
            return
        
        if messagebox.askyesno("Clear All", "⚠️ Are you sure you want to delete ALL tasks?"):
            self.tasks.clear()
            self.update_listbox()
            self.save_tasks()
            self.update_statistics()
            self.show_status("All tasks cleared.")
    
    def search_tasks(self):
        self.search_term = self.search_entry.get().strip().lower()
        self.apply_filter()
    
    def apply_filter(self):
        self.current_filter = self.filter_var.get()
        self.update_listbox()
    
    def filter_tasks(self, tasks):
        filtered = []
        today = date.today()
        
        for task in tasks:
            # Apply search filter
            if self.search_term and self.search_term not in task["text"].lower():
                continue
            
            # Apply category filter
            if self.current_filter == "Active" and task["completed"]:
                continue
            elif self.current_filter == "Completed" and not task["completed"]:
                continue
            elif self.current_filter == "High Priority" and task["priority"] != "High":
                continue
            elif self.current_filter == "Medium Priority" and task["priority"] != "Medium":
                continue
            elif self.current_filter == "Low Priority" and task["priority"] != "Low":
                continue
            elif self.current_filter == "Overdue":
                if task["completed"] or not task["due_date"]:
                    continue
                try:
                    due = datetime.strptime(task["due_date"], "%Y-%m-%d").date()
                    if due >= today:
                        continue
                except:
                    continue
            
            filtered.append(task)
        
        return filtered
    
    def update_listbox(self):
        self.task_listbox.delete(0, tk.END)
        filtered_tasks = self.filter_tasks(self.tasks)
        today = date.today()
        
        for task in filtered_tasks:
            # Format display text
            display_text = task["text"]
            
            # Add priority icon
            priority_icons = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
            display_text = f"{priority_icons[task['priority']]} {display_text}"
            
            # Add due date
            if task["due_date"]:
                try:
                    due = datetime.strptime(task["due_date"], "%Y-%m-%d").date()
                    if due < today and not task["completed"]:
                        display_text += f" ⏰ OVERDUE!"
                    else:
                        display_text += f" (Due: {task['due_date']})"
                except:
                    display_text += f" (Due: {task['due_date']})"
            
            # Mark completed
            if task["completed"]:
                display_text = f"✓ {display_text}"
            
            self.task_listbox.insert(tk.END, display_text)
        
        # Apply colors
        for i, task in enumerate(filtered_tasks):
            if task["completed"]:
                self.task_listbox.itemconfig(i, fg="#7f8c8d", bg="#ecf0f1")
            elif task["priority"] == "High":
                self.task_listbox.itemconfig(i, fg="#e74c3c", bg="#fdecea")
            elif task["priority"] == "Medium":
                self.task_listbox.itemconfig(i, fg="#f39c12", bg="#fef5e7")
            else:
                self.task_listbox.itemconfig(i, fg="#27ae60", bg="#e8f8f5")
            
            # Highlight overdue
            if (task["due_date"] and not task["completed"]):
                try:
                    if datetime.strptime(task["due_date"], "%Y-%m-%d").date() < today:
                        self.task_listbox.itemconfig(i, bg="#ffcccc")
                except:
                    pass
    
    def update_statistics(self):
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t["completed"])
        active = total - completed
        completion_rate = (completed / total * 100) if total > 0 else 0
        
        priority_counts = defaultdict(int)
        overdue = 0
        today = date.today()
        
        for task in self.tasks:
            priority_counts[task["priority"]] += 1
            if (task["due_date"] and not task["completed"]):
                try:
                    if datetime.strptime(task["due_date"], "%Y-%m-%d").date() < today:
                        overdue += 1
                except:
                    pass
        
        stats_text = f"Total Tasks: {total}    ✅ Completed: {completed}    🔄 Active: {active}\n"
        stats_text += f"Completion Rate: {completion_rate:.1f}%    ⚠ Overdue: {overdue}\n"
        stats_text += f"🔴 High: {priority_counts['High']}    🟡 Medium: {priority_counts['Medium']}    🟢 Low: {priority_counts['Low']}"
        
        self.stats_details.config(text=stats_text)
    
    def change_theme(self):
        # Create theme selection dialog
        theme_window = tk.Toplevel(self.root)
        theme_window.title("Choose Theme")
        theme_window.geometry("300x250")
        theme_window.resizable(False, False)
        
        tk.Label(theme_window, text="Select Color Theme:", font=("Segoe UI", 12, "bold")).pack(pady=10)
        
        for theme_name in self.themes.keys():
            btn = tk.Button(theme_window, text=theme_name, font=("Segoe UI", 10),
                          command=lambda t=theme_name: self.set_theme(t, theme_window),
                          width=15, pady=5)
            btn.pack(pady=5)
    
    def set_theme(self, theme_name, window):
        self.current_theme = theme_name
        self.apply_theme()
        window.destroy()
        self.show_status(f"🎨 Theme changed to {theme_name}")
    
    def apply_theme(self):
        theme = self.themes[self.current_theme]
        
        # Apply to root and frames
        for widget in [self.root, self.stats_frame]:
            widget.config(bg=theme["bg"])
        
        # Update labels
        for label in [self.stats_label, self.stats_details]:
            label.config(bg=theme["bg"], fg=theme["fg"])
        
        # Update listbox
        self.task_listbox.config(selectbackground=theme["selected_bg"])
        
        # Update add button
        self.add_btn.config(bg=theme["button_bg"], fg=theme["button_fg"])
    
    def show_context_menu(self, event):
        try:
            self.task_listbox.selection_clear(0, tk.END)
            self.task_listbox.selection_set(self.task_listbox.nearest(event.y))
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def focus_search(self):
        self.search_entry.focus_set()
    
    def save_tasks(self):
        try:
            with open(DATA_FILE, "w") as f:
                json.dump(self.tasks, f, indent=2)
        except Exception as e:
            print(f"Error saving tasks: {e}")
    
    def load_tasks(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    self.tasks = json.load(f)
                self.update_listbox()
                self.show_status(f"Loaded {len(self.tasks)} tasks.")
            except Exception as e:
                print(f"Error loading tasks: {e}")
                self.tasks = []
    
    def show_status(self, message):
        self.status_label.config(text=message)
        self.root.after(2000, lambda: self.status_label.config(text=""))

if __name__ == "__main__":
    root = tk.Tk()
    app = ToDoApp(root)
    root.mainloop()