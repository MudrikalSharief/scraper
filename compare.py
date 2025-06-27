# # This script compares two Excel files, extracts unique URLs, and saves them to a new file.

import pandas as pd

# Replace with your actual file names
file1 = "result1.xlsx"
file2 = "result2.xlsx"
output_file = "unique_urls.xlsx"

# Read both Excel files
df1 = pd.read_excel(file1)
df2 = pd.read_excel(file2)

# Ensure consistent column names (adjust if needed)
url_col = "url"
name_col = "Journal Name" 

# Combine both DataFrames
combined = pd.concat([df1[[name_col, url_col]], df2[[name_col, url_col]]], ignore_index=True)

# Count duplicates based on URL
total_links = len(combined)
unique_links = combined[url_col].nunique()
duplicate_count = total_links - unique_links

# Drop duplicates based on URL, keeping the first occurrence
unique = combined.drop_duplicates(subset=[url_col], keep='first')

# Save to a new Excel file
unique[[name_col, url_col]].to_excel(output_file, index=False)

print(f"Unique URLs saved to {output_file}")
print(f"Number of duplicated links: {duplicate_count}")