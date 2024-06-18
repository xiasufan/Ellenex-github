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
        
        # Remove duplicates to ensure there are no duplicate keys in processed_df
        processed_df = processed_df.drop_duplicates(subset=[processed_column])
        
        # Merge the dataframes
        merged_df = pd.merge(main_df, processed_df, left_on=main_column, right_on=processed_column, how='left', suffixes=('', '_dup'))

        # Combine duplicate columns
        for col in processed_df.columns:
            if col != processed_column and col in main_df.columns:
                merged_df[col] = merged_df.apply(lambda row: ','.join(filter(pd.notna, [row[col], row[f"{col}_dup"]])), axis=1)
                merged_df.drop(columns=[f"{col}_dup"], inplace=True)

        output_file = f"{os.path.splitext(main_file)[0]}_merged.csv"
        merged_df.to_csv(output_file, index=False)
        
        messagebox.showinfo("Success", f"Merged file saved as {output_file}")
    except Exception as e:
        messagebox.showerror("Error", f"Merge failed: {str(e)}")

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
            messagebox.showerror("Error", f"Cannot read file: {str(e)}")

def on_merge():
    main_file = main_file_entry.get()
    processed_file = processed_file_entry.get()
    main_column = main_column_var.get()
    processed_column = processed_column_var.get()
    main_encoding = main_encoding_var.get()
    processed_encoding = processed_encoding_var.get()
    
    if not main_file or not processed_file or not main_column or not processed_column:
        messagebox.showwarning("Warning", "Please ensure all fields are filled")
        return
    
    merge_csv_files(main_file, processed_file, main_column, processed_column, main_encoding, processed_encoding)

app = tk.Tk()
app.title("CSV Merge Tool")

tk.Label(app, text="Main File:").grid(row=0, column=0, padx=10, pady=10)
main_file_entry = tk.Entry(app, width=50)
main_file_entry.grid(row=0, column=1, padx=10, pady=10)
main_browse_button = tk.Button(app, text="Browse...", command=lambda: browse_file(main_file_entry, main_column_var, main_encoding_var))
main_browse_button.grid(row=0, column=2, padx=10, pady=10)

tk.Label(app, text="Supplementary File:").grid(row=1, column=0, padx=10, pady=10)
processed_file_entry = tk.Entry(app, width=50)
processed_file_entry.grid(row=1, column=1, padx=10, pady=10)
processed_browse_button = tk.Button(app, text="Browse...", command=lambda: browse_file(processed_file_entry, processed_column_var, processed_encoding_var))
processed_browse_button.grid(row=1, column=2, padx=10, pady=10)

tk.Label(app, text="Main File Merge Column:").grid(row=2, column=0, padx=10, pady=10)
main_column_var = ttk.Combobox(app, width=47)
main_column_var.grid(row=2, column=1, padx=10, pady=10)

tk.Label(app, text="Supplementary File Merge Column:").grid(row=3, column=0, padx=10, pady=10)
processed_column_var = ttk.Combobox(app, width=47)
processed_column_var.grid(row=3, column=1, padx=10, pady=10)

main_encoding_var = tk.StringVar()
processed_encoding_var = tk.StringVar()

merge_button = tk.Button(app, text="Merge", command=on_merge)
merge_button.grid(row=4, column=1, padx=10, pady=10)

app.mainloop()
