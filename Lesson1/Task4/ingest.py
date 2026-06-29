import argparse
import sys
import time
from pathlib import Path
from rag.config import get_settings
from rag.engine import build_index


def main():
    parser = argparse.ArgumentParser(description="Build vector index")
    parser.add_argument("--data-dir", type=Path, default=None)
    parser.add_argument("--chunk-size", type=int, default=None)
    parser.add_argument("--chunk-overlap", type=int, default=None)
    args = parser.parse_args()

    settings = get_settings()

    if args.data_dir:
        settings.data_dir = args.data_dir
    if args.chunk_size:
        settings.chunk_size = args.chunk_size
    if args.chunk_overlap:
        settings.chunk_overlap = args.chunk_overlap

    if not settings.data_dir.exists():
        print(f"Data directory not found: {settings.data_dir}")
        sys.exit(1)

    start = time.time()
    try:
        store = build_index(settings)
        elapsed = time.time() - start
        print(f"Indexed {store.count()} chunks in {elapsed:.1f}s")
    except Exception as e:
        print(f"Error building index: {e}")
        raise


if __name__ == "__main__":
    main()
