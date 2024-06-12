import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)
        load_columns(file_path)

def load_columns(file_path):
    try:
        df = pd.read_csv(file_path, nrows=0)
        columns = df.columns.tolist()
        for col in columns:
            columns_listbox.insert(tk.END, col)
    except Exception as e:
        messagebox.showerror("错误", f"无法读取文件：{str(e)}")

def edit_column_name():
    selected_indices = columns_listbox.curselection()
    if not selected_indices:
        messagebox.showwarning("警告", "请选择一个列名进行编辑")
        return

    selected_index = selected_indices[0]
    old_name = columns_listbox.get(selected_index)
    new_name = simpledialog.askstring("编辑列名", f"请输入新的列名 (当前列名: {old_name})")
    if new_name:
        columns_listbox.delete(selected_index)
        columns_listbox.insert(selected_index, new_name)

def save_selected_columns():
    selected_indices = columns_listbox.curselection()
    if not selected_indices:
        messagebox.showwarning("警告", "请选择要保存的列")
        return

    file_path = file_entry.get()
    if not file_path:
        messagebox.showwarning("警告", "请选择一个CSV文件")
        return

    try:
        df = pd.read_csv(file_path)
        selected_columns = [columns_listbox.get(i) for i in selected_indices]
        new_df = df[selected_columns]

        save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if save_path:
            new_df.to_csv(save_path, index=False)
            messagebox.showinfo("成功", f"文件已保存到 {save_path}")
    except Exception as e:
        messagebox.showerror("错误", f"保存文件失败：{str(e)}")

app = tk.Tk()
app.title("CSV 列编辑工具")

tk.Label(app, text="CSV 文件:").grid(row=0, column=0, padx=10, pady=10)
file_entry = tk.Entry(app, width=50)
file_entry.grid(row=0, column=1, padx=10, pady=10)
browse_button = tk.Button(app, text="浏览...", command=browse_file)
browse_button.grid(row=0, column=2, padx=10, pady=10)

columns_listbox = tk.Listbox(app, selectmode=tk.MULTIPLE, width=50, height=20)
columns_listbox.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

edit_button = tk.Button(app, text="编辑列名", command=edit_column_name)
edit_button.grid(row=2, column=0, padx=10, pady=10)

save_button = tk.Button(app, text="保存选择的列", command=save_selected_columns)
save_button.grid(row=2, column=2, padx=10, pady=10)

app.mainloop()
