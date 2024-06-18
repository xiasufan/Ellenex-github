import pandas as pd
import os
import re 

def clean_emails(input_csv, output_csv):
    # 尝试不同编码读取CSV文件，并跳过错误的行
    try:
        df = pd.read_csv(input_csv, encoding='utf-8', on_bad_lines='skip')
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(input_csv, encoding='latin1', on_bad_lines='skip')
        except UnicodeDecodeError:
            df = pd.read_csv(input_csv, encoding='iso-8859-1', on_bad_lines='skip')
    
    # 定义需要删除的无效邮件地址关键词
    invalid_domains = ['.js','.gif','.webp','wixpress', 'godaddy', 'sentry', 'jpg', 'null','?', 'no-reply', 'noreply', 'example.com', 'example', 'domain.com']
    
    # 处理Emails列
    def remove_invalid_emails(email_str):
        if pd.isna(email_str) or not isinstance(email_str, str):
            return email_str
        emails = re.split(r'[;,]', email_str)  # 使用正则表达式同时考虑分号和逗号
        valid_emails = [email.lower().strip() for email in emails if not any(domain in email.lower() for domain in invalid_domains)]
        return ';'.join(valid_emails)
    
    # 应用处理函数到Emails列
    df['Emails'] = df['Emails'].apply(remove_invalid_emails)
    
    # 拆分Emails列中的多个邮箱地址，并保持其他列的信息不变
    def split_emails(row):
        if pd.isna(row['Emails']) or not isinstance(row['Emails'], str):
            return pd.DataFrame({**row.drop(labels=['Emails']), 'Emails': []})
        emails = re.split(r'[;,]', row['Emails'])  # 使用正则表达式同时考虑分号和逗号
        other_columns = row.drop(labels=['Emails']).to_dict()
        return pd.DataFrame({**other_columns, 'Emails': emails})
    
    # 应用拆分函数并重组数据框
    split_df_list = df.apply(split_emails, axis=1).tolist()
    df = pd.concat(split_df_list).reset_index(drop=True)
    
    # 删除重复的Email行，只保留独特的Email行
    df = df.drop_duplicates(subset='Emails')

    # 保存处理后的CSV文件
    df.to_csv(output_csv, index=False)

# 指定要处理的目录路径
directory_path = './process email here'

# 遍历目录下的所有文件
for filename in os.listdir(directory_path):
    if filename.endswith('.csv'):
        input_csv = os.path.join(directory_path, filename)
        output_csv = os.path.join(directory_path, f"{os.path.splitext(filename)[0]}_processed.csv")
        # 调用函数进行处理
        clean_emails(input_csv, output_csv)
        print(f"Processed {input_csv} and saved as {output_csv}")
