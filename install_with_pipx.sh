#!/bin/bash

# Path ke file requirements.txt
requirements_file="requirements.txt"

# Baca file requirements.txt baris per baris
while IFS= read -r package; do
    if [ -n "$package" ]; then  # Pastikan tidak ada baris kosong
        echo "Installing $package with pipx..."
        pipx install "$package"
    fi
done < "$requirements_file"
