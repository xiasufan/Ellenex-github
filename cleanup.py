import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox

directory_path = './cleanup columns here'

def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")], initialdir=directory_path)
    if file_path:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)
        load_columns(file_path)

def load_columns(file_path):
    try:
        df = pd.read_csv(file_path, nrows=0)
        columns = df.columns.tolist()
        update_columns_listbox(columns)
    except Exception as e:
        messagebox.showerror("Error", f"Unable to read file: {str(e)}")

def update_columns_listbox(columns):
    for widget in columns_frame.winfo_children():
        widget.destroy()

    for col in columns:
        create_column_widget(col)

def create_column_widget(col, marked_for_deletion=False):
    frame = tk.Frame(columns_frame)
    frame.pack(fill=tk.X, padx=10, pady=2)
    
    entry = tk.Entry(frame, width=40)
    entry.insert(0, col)
    entry.bind("<FocusOut>", lambda event, e=entry: update_column_name(e))
    entry.pack(side=tk.LEFT, padx=5)
    
    if marked_for_deletion:
        entry.config(state='disabled', disabledbackground='gray', disabledforeground='white')

    del_button = tk.Button(frame, text="X", command=lambda e=entry: mark_for_deletion(e))
    del_button.pack(side=tk.RIGHT)
    
    undo_button = tk.Button(frame, text="↩", command=lambda e=entry: undo_deletion(e))
    undo_button.pack(side=tk.RIGHT)
    undo_button.config(state='disabled' if not marked_for_deletion else 'normal')

def update_column_name(entry):
    new_name = entry.get()
    if not new_name:
        messagebox.showwarning("Warning", "Column name cannot be empty")

def mark_for_deletion(entry):
    entry.config(state='disabled', disabledbackground='gray', disabledforeground='white')
    for widget in entry.master.winfo_children():
        if isinstance(widget, tk.Button) and widget.cget('text') == '↩':
            widget.config(state='normal')

def undo_deletion(entry):
    entry.config(state='normal')
    for widget in entry.master.winfo_children():
        if isinstance(widget, tk.Button) and widget.cget('text') == '↩':
            widget.config(state='disabled')

def save_file():
    file_path = file_entry.get()
    if not file_path:
        messagebox.showwarning("Warning", "Please select a CSV file")
        return

    try:
        df = pd.read_csv(file_path)
        original_columns = df.columns.tolist()
        new_columns = []
        column_map = {}

        for frame, original_col in zip(columns_frame.winfo_children(), original_columns):
            for widget in frame.winfo_children():
                if isinstance(widget, tk.Entry):
                    if widget.cget('state') == 'normal':
                        new_columns.append(widget.get())
                        column_map[original_col] = widget.get()
                    else:
                        column_map[original_col] = None

        # Filter out columns marked for deletion
        columns_to_keep = [col for col in original_columns if column_map[col] is not None]
        df = df[columns_to_keep]

        # Rename the columns
        df.columns = [column_map[col] for col in columns_to_keep]
        
        df.to_csv(file_path, index=False)
        messagebox.showinfo("Success", f"File has been saved to {file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save file: {str(e)}")

app = tk.Tk()
app.title("CSV Column Edit Tool")

tk.Label(app, text="CSV File:").grid(row=0, column=0, padx=10, pady=10)
file_entry = tk.Entry(app, width=50)
file_entry.grid(row=0, column=1, padx=10, pady=10)
browse_button = tk.Button(app, text="Browse...", command=browse_file)
browse_button.grid(row=0, column=2, padx=10, pady=10)

columns_frame = tk.Frame(app)
columns_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

save_button = tk.Button(app, text="Save", command=save_file)
save_button.grid(row=2, column=1, padx=10, pady=10)

app.mainloop()
