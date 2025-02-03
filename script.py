import os
import re
import hashlib
from collections import defaultdict

def process_directory(root_dir):
    for dirpath, _, filenames in os.walk(root_dir):
        # Process markdown files with numeric prefixes
        md_files = []
        pattern = re.compile(r'^(\d+)\. (.*\.md)$')
        
        # Collect and hash markdown files
        content_map = defaultdict(list)
        for filename in filenames:
            match = pattern.match(filename)
            if match and filename.endswith('.md'):
                num_prefix, rest = match.groups()
                filepath = os.path.join(dirpath, filename)
                with open(filepath, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                md_files.append((filename, int(num_prefix), rest, filepath, file_hash))
                content_map[file_hash].append(md_files[-1])

        # Remove duplicates (keep lowest-numbered file)
        for hash_group in content_map.values():
            if len(hash_group) > 1:
                # Sort by numeric prefix and remove duplicates
                hash_group.sort(key=lambda x: x[1])
                for duplicate in hash_group[1:]:
                    os.remove(duplicate[3])
                    md_files.remove(duplicate)

        # Renumber remaining files
        md_files = [f for f in md_files if os.path.exists(f[3])]  # Remove deleted entries
        md_files.sort(key=lambda x: x[1])  # Sort by original numeric prefix
        
        # Generate new numbering and rename files
        for i, (old_name, _, rest, old_path, _) in enumerate(reversed(md_files), 1):
            new_prefix = f"{len(md_files) - i + 1:02d}"
            new_name = f"{new_prefix}. {rest}"
            if new_name != old_name:
                new_path = os.path.join(dirpath, new_name)
                os.rename(old_path, new_path)

if __name__ == "__main__":
    process_directory('.')
