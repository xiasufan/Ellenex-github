import os
import pandas as pd
import chardet

def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    return result['encoding']

# 指定要处理的目录
directory = './combine here'

# 初始化一个空的数据框，用于存储所有合并的数据
combined_df = pd.DataFrame()
extra_columns = set()

# 遍历目录下的所有文件
for filename in os.listdir(directory):
    if filename.endswith('.csv'):
        # 构建文件的完整路径
        file_path = os.path.join(directory, filename)
        
        # 检测文件编码
        encoding = detect_encoding(file_path)
        
        try:
            # 读取CSV文件
            df = pd.read_csv(file_path, encoding=encoding)
            if df.empty:
                print(f"File {filename} is empty. Skipping.")
                continue
            
            # 合并数据框
            combined_df = pd.concat([combined_df, df], ignore_index=True)
        except pd.errors.EmptyDataError:
            print(f"No columns to parse from file {filename}. Skipping.")
        except Exception as e:
            print(f"Error reading {filename}: {e}")
        
        # 记录多余的列名
        extra_columns.update(df.columns.difference(combined_df.columns))

# 构建新文件名
output_filename = 'combined_processed_files.csv'
output_file_path = os.path.join(directory, output_filename)

# 保存合并后的数据框为新的CSV文件
combined_df.to_csv(output_file_path, index=False)
print(f"All processed files have been combined and saved as {output_filename}")

# 保存多余的列名
extra_columns_filename = 'extra_columns.csv'
extra_columns_file_path = os.path.join(directory, extra_columns_filename)
with open(extra_columns_file_path, 'w') as f:
    for col in extra_columns:
        f.write(f"{col}\n")
print(f"Extra columns have been saved as {extra_columns_filename}")
