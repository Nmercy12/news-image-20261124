import os
import shutil
import hashlib
import sys

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    source_image = os.path.join(script_dir, "entry.png")
    
    if not os.path.exists(source_image):
        print(f"Error: source image not found at {source_image}", file=sys.stderr)
        sys.exit(1)

    # Determine output directory
    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not output_dir:
        output_dir = os.path.join(script_dir, "out")

    os.makedirs(output_dir, exist_ok=True)
    
    # Target path
    target_image = os.path.join(output_dir, "entry.png")

    # Copy bytes exactly
    shutil.copyfile(source_image, target_image)

    # Verify byte size matches
    src_size = os.path.getsize(source_image)
    dst_size = os.path.getsize(target_image)
    if src_size != dst_size:
        print(f"Error: size mismatch! Source: {src_size}, Dest: {dst_size}", file=sys.stderr)
        sys.exit(1)

    # Verify PNG dimensions (1024x1024) from IHDR chunk
    with open(target_image, "rb") as f:
        header = f.read(24)
    if len(header) < 24 or header[:8] != b'\x89PNG\r\n\x1a\n' or header[12:16] != b'IHDR':
        print("Error: invalid PNG header or IHDR chunk", file=sys.stderr)
        sys.exit(1)
    width = int.from_bytes(header[16:20], byteorder='big')
    height = int.from_bytes(header[20:24], byteorder='big')
    if width != 1024 or height != 1024:
        print(f"Error: expected 1024x1024 dimensions, got {width}x{height}", file=sys.stderr)
        sys.exit(1)

    # Compute SHA-256 of target
    sha256_hash = hashlib.sha256()
    with open(target_image, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    file_hash = sha256_hash.hexdigest()

    print(f"Output path: {target_image}")
    print(f"SHA-256: {file_hash}")
    print(f"Size: {src_size} bytes")

if __name__ == "__main__":
    main()
