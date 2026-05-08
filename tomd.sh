#!/bin/bash

# Improved tomd.sh - Batch convert HTML to Markdown using markitdown

# 1. Dependency Check
if ! command -v markitdown &> /dev/null; then
    echo "Error: 'markitdown' is not installed. Install it with: pip install markitdown"
    exit 1
fi

# 2. Help/Usage
if [ $# -eq 0 ]; then
    echo "Usage: $(basename "$0") <file_or_folder1> [file_or_folder2 ...]"
    echo "Example: $(basename "$0") ./docs index.html about.html"
    exit 1
fi

# 3. Conversion Function
convert_file() {
    local input="$1"
    local output="${input%.html}.md"

    # Only process files ending in .html
    if [[ ! "$input" =~ \.html$ ]]; then
        return
    fi

    echo -n "Converting: $input... "
    
    # Run markitdown and capture success
    if markitdown "$input" > "$output" 2>/dev/null; then
        rm "$input"
        echo "Done (Source Deleted)."
    else
        echo "FAILED. (Kept source)"
        # Clean up the output file if it was created but is empty/corrupt
        [ -f "$output" ] && rm "$output"
    fi
}

# 4. Main Loop
for arg in "$@"; do
    if [ -d "$arg" ]; then
        # If it's a directory, find all .html files (recursive up to depth 3)
        # Use -print0 and read -d to safely handle spaces in filenames
        find "$arg" -maxdepth 3 -name "*.html" -type f -print0 | while IFS= read -r -d '' file; do
            convert_file "$file"
        done
    elif [ -f "$arg" ]; then
        # If it's a specific file
        convert_file "$arg"
    else
        echo "Warning: '$arg' is not a valid file or directory. Skipping."
    fi
done

echo "Batch conversion complete."
