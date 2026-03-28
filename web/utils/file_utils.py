from typing import BinaryIO


def get_file_size(uploaded_file: BinaryIO) -> int:
    uploaded_file.seek(0, 2)  # Move to end of file
    size = uploaded_file.tell()
    uploaded_file.seek(0)  # Reset back to beginning
    return size