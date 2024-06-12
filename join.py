import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import chardet

def detect_encoding(file):
    with open(file, 'rb') as f:
        result = chardet.detect(f.read())
    return result['encoding']

def get_columns(file):
    encoding = detect_encoding(file)
    try:
        df = pd.read_csv(file, encoding=encoding, nrows=0)
        return df.columns.tolist(), encoding
    except Exception as e:
        raise Exception(f"Cannot read file {file} with detected encoding {encoding}: {str(e)}")

def merge_csv_files(main_file, processed_file, main_column, processed_column, main_encoding, processed_encoding):
    try:
        main_df = pd.read_csv(main_file, encoding=main_encoding)
        processed_df = pd.read_csv(processed_file, encoding=processed_encoding)
        
        # 去重处理，确保 processed_df 的主键列没有重复值
        processed_df = processed_df.drop_duplicates(subset=[processed_column])
        
        merged_df = pd.merge(main_df, processed_df, left_on=main_column, right_on=processed_column, how='left')
        
        output_file = f"{os.path.splitext(main_file)[0]}_merged.csv"
        merged_df.to_csv(output_file, index=False)
        
        messagebox.showinfo("成功", f"合并完成并保存为 {output_file}")
    except Exception as e:
        messagebox.showerror("错误", f"合并失败：{str(e)}")

def browse_file(entry, column_var, encoding_var):
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        entry.delete(0, tk.END)
        entry.insert(0, file_path)
        try:
            columns, encoding = get_columns(file_path)
            column_var.set('')
            column_var['values'] = columns
            encoding_var.set(encoding)
        except Exception as e:
            messagebox.showerror("错误", f"无法读取文件：{str(e)}")

def on_merge():
    main_file = main_file_entry.get()
    processed_file = processed_file_entry.get()
    main_column = main_column_var.get()
    processed_column = processed_column_var.get()
    main_encoding = main_encoding_var.get()
    processed_encoding = processed_encoding_var.get()
    
    if not main_file or not processed_file or not main_column or not processed_column:
        messagebox.showwarning("警告", "请确保所有输入项均已填写")
        return
    
    merge_csv_files(main_file, processed_file, main_column, processed_column, main_encoding, processed_encoding)

app = tk.Tk()
app.title("CSV 合并工具")

tk.Label(app, text="主表文件:").grid(row=0, column=0, padx=10, pady=10)
main_file_entry = tk.Entry(app, width=50)
main_file_entry.grid(row=0, column=1, padx=10, pady=10)
main_browse_button = tk.Button(app, text="浏览...", command=lambda: browse_file(main_file_entry, main_column_var, main_encoding_var))
main_browse_button.grid(row=0, column=2, padx=10, pady=10)

tk.Label(app, text="补全信息文件:").grid(row=1, column=0, padx=10, pady=10)
processed_file_entry = tk.Entry(app, width=50)
processed_file_entry.grid(row=1, column=1, padx=10, pady=10)
processed_browse_button = tk.Button(app, text="浏览...", command=lambda: browse_file(processed_file_entry, processed_column_var, processed_encoding_var))
processed_browse_button.grid(row=1, column=2, padx=10, pady=10)

tk.Label(app, text="主表合并列:").grid(row=2, column=0, padx=10, pady=10)
main_column_var = ttk.Combobox(app, width=47)
main_column_var.grid(row=2, column=1, padx=10, pady=10)

tk.Label(app, text="补全信息合并列:").grid(row=3, column=0, padx=10, pady=10)
processed_column_var = ttk.Combobox(app, width=47)
processed_column_var.grid(row=3, column=1, padx=10, pady=10)

main_encoding_var = tk.StringVar()
processed_encoding_var = tk.StringVar()

merge_button = tk.Button(app, text="合并", command=on_merge)
merge_button.grid(row=4, column=1, padx=10, pady=10)

app.mainloop()
