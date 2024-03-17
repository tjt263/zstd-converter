#!/usr/bin/env python3

import os
import sys
import shutil
import tarfile
import zipfile
import patoolib
import zstandard as zstd

# Function to create a tar archive of files within a directory
def create_tar_archive(directory, output_file):
    with tarfile.open(output_file, 'w') as tar:
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                tar.add(file_path, arcname=os.path.relpath(file_path, directory))

# Function to compress files within an archive with Zstandard
def compress_archive_with_zstd(input_file, output_file):
    cctx = zstd.ZstdCompressor()
    with open(input_file, 'rb') as f_in:
        compressed_data = cctx.compress(f_in.read())
    with open(output_file, 'wb') as f_out:
        f_out.write(compressed_data)

# Main function to orchestrate the compression process
def compress_archives_to_tar_zst(archive_dir, output_dir):
    for file_name in os.listdir(archive_dir):
        file_path = os.path.join(archive_dir, file_name)
        if os.path.isfile(file_path) and (file_name.endswith(".zip") or file_name.endswith(".rar")):
            # Create temporary directory to extract files
            temp_extract_dir = os.path.join(output_dir, 'temp_extract')
            os.makedirs(temp_extract_dir, exist_ok=True)

            # Extract files from archive
            if file_name.endswith(".zip"):
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_extract_dir)
            elif file_name.endswith(".rar"):
                patoolib.extract_archive(file_path, outdir=temp_extract_dir)

            # Create tar archive of extracted files
            temp_tar_file = os.path.join(output_dir, f'{os.path.splitext(file_name)[0]}.tar')
            create_tar_archive(temp_extract_dir, temp_tar_file)

            # Compress tar archive with Zstandard
            output_file = os.path.join(output_dir, f'{os.path.splitext(file_name)[0]}.tar.zst')
            compress_archive_with_zstd(temp_tar_file, output_file)

            # Clean up temporary directory and tar file
            shutil.rmtree(temp_extract_dir)
            os.remove(temp_tar_file)

if __name__ == "__main__":
    # Check if the correct number of arguments is provided
    if len(sys.argv) != 3:
        print("Usage: python script.py input_dir output_dir")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    
    # Check if input directory exists
    if not os.path.exists(input_dir):
        print("Input directory does not exist.")
        sys.exit(1)
    
    # Check if output directory exists, if not create it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Perform the compression
    compress_archives_to_tar_zst(input_dir, output_dir)
