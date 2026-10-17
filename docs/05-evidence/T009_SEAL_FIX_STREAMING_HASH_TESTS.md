# T009-SEAL-FIX Streaming SHA-256 Tests & Memory Safety Report

## 1. Context & Architectural Requirement (FIX-S03)
In the 2016–2024 flight performance dataset, Parquet output partitions may reach hundreds of megabytes. Using `f.read_bytes()` to compute cryptographic hashes loaded entire partitions into memory buffers, creating severe RAM pressure and risk of `OutOfMemoryError` on constrained workers.

---

## 2. Implementation: Streaming Block Hashing
The helper function `compute_file_sha256(p: Path, chunk_size: int = 65536) -> str` was integrated into `src/flight_pipeline/storage/publication.py`.
- **Block Size:** 64 KB (65,536 bytes), matching standard OS page clustering and I/O buffer sizes.
- **Memory Bound:** Maximum memory buffer is strictly capped at 64 KB regardless of whether the file size is 10 KB or 10 GB.
- **Python Compatibility:** Implemented using standard binary stream reads compatible with Python 3.10 runtime without external C-extensions.

---

## 3. Test Suite & Invariant Verification (`test_streaming_sha256_matches_hashlib_and_handles_blocks`)

A dedicated unit test was added to `tests/test_publication_safety.py` covering four test dimensions:

1. **Empty File Invariant (0 bytes):**
   - File size: 0 bytes.
   - Verified output: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
   - Matches standard `hashlib.sha256(b"").hexdigest()` exactly.
2. **Small File Invariant (< 64KB):**
   - File size: ~2.3 KB.
   - Evaluated within a single block read iteration.
   - Matches standard `hashlib.sha256` output.
3. **Multi-Block File Invariant (> 64KB):**
   - File size: 200,000 bytes (~195 KB, spanning 4 distinct buffer chunks).
   - Verifies loop accumulation across block boundaries.
   - Matches standard `hashlib.sha256` output.
4. **I/O Error Handling Invariant:**
   - Evaluated against a non-existent file path.
   - Verifies explicit `FileNotFoundError` propagation with clear diagnostic path info.

- **Suite Execution:** PASS in < 0.05s.
