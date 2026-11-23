---
name: modern-c-mastery
description: "Modern C11/C17/C23 engineering: arena allocators, UB elimination, strict compiler hardening flags, and sanitizer verification."
license: MIT
compatibility: opencode
---
# Modern C (C11 / C17 / C23) Mastery

Write tight, deterministic, zero-UB, production-grade C. Never write 1990s-style fragile C.

## 1. Language Baseline & Modern Idioms
- **Target C23 where toolchain supports (`-std=c23`), otherwise C17 (`-std=c17`).**
- **Exact-width & semantic types:** Always use `<stdint.h>` (`uint8_t`, `uint32_t`, `int64_t`, `uintptr_t`), `size_t` for sizes/indices, `ptrdiff_t` for pointer deltas, `bool` (`<stdbool.h>` in C17, keyword in C23). Never assume `int` or `long` widths.
- **C23 upgrades (when `-std=c23` is active):**
  - `nullptr` instead of `NULL` / `0`.
  - `constexpr` for compile-time typed constants (replaces untyped `#define` magic numbers).
  - `typeof` / `typeof_unqual` for type-safe generic macros.
  - `<stdckdint.h>` (`ckd_add`, `ckd_sub`, `ckd_mul`) for overflow-checked integer math.
  - `[[nodiscard]]` on all functions returning error codes or owned handles; `[[maybe_unused]]` instead of `(void)x;`.
  - `static_assert(cond, "msg")` (or `_Static_assert` in C17) to enforce struct layout, ABI sizes, and enum bounds at compile time.
- **Safe slices & strings:** Prefer fat pointers `typedef struct { const uint8_t *ptr; size_t len; } ByteSlice;` / `StrView` over NUL-terminated scanning (`strlen`/`strcpy`/`sprintf` are banned; use `snprintf` or explicit length-bounded builders).

## 2. Memory Ownership & Allocator Architecture
- **Explicit ownership in every API:** Document who owns every pointer (`in` borrowed, `out` caller-frees, or `arena`-owned).
- **Arena / Region Allocators first:** Group request/frame/phase allocations into a linear `Arena` (`arena_alloc`, `arena_reset`, `arena_destroy`) to eliminate fragmentation and per-object leak bugs.
- **Deterministic cleanup:** Use single-exit `goto cleanup;` with zero-initialized locals (`Foo f = {0};`) so partial initialization never leaks resources.
- **Overflow-safe allocation:** Always check `count > SIZE_MAX / sizeof(T)` (or `ckd_mul`) before `malloc`/`calloc`/`realloc`. Never overwrite the original pointer directly on `realloc` failure:
  ```c
  void *tmp = realloc(buf, new_cap);
  if (!tmp) return ERR_OOM;
  buf = tmp;
  ```

## 3. Zero Undefined Behavior (UB) Checklist
- **Type punning:** NEVER cast `uint8_t*` to `uint32_t*` (breaks strict aliasing & alignment). Always use `memcpy(&val, ptr, sizeof val)` — modern compilers optimize it to a single load instruction.
- **Integer safety:** Never shift by `>= width`, never shift negative values, never rely on signed integer overflow wrapping.
- **Uninitialized memory:** Always zero-initialize structs (`T x = {0};`). Watch padding bytes before `memcmp` or hashing/serialization.
- **Pointer arithmetic:** Never compute pointers outside `[base, base + len]` (one-past-end is valid to form, never to dereference).
- **Thread safety:** Use `<stdatomic.h>` with explicit memory orders (`memory_order_acquire` / `memory_order_release`) rather than `volatile` (which is ONLY for MMIO/signals, never concurrency).

## 4. API Design, Build & Verification
- **Opaque types:** Expose `typedef struct Engine Engine;` in `.h`, define `struct Engine { ... };` in `.c`. Keep internal helpers `static`.
- **Error handling:** Return typed `enum Status` with `[[nodiscard]]`. Never ignore return values from I/O, allocators, or syscalls.
- **Mandatory Compiler Flags:**
  - GCC/Clang: `-Wall -Wextra -Wpedantic -Wshadow -Wconversion -Wsign-conversion -Wstrict-prototypes -Wmissing-prototypes -Werror`
  - MSVC: `/W4 /WX /permissive- /sdl`
- **Mandatory Sanitizer Verification (Debug/Test builds):**
  - `-g -O1 -fno-omit-frame-pointer -fsanitize=address,undefined` (add `-fsanitize=thread` for multithreaded modules).
- **Static Analysis (when installed):** `clang-tidy`, `cppcheck --enable=all`, and unit tests covering boundary sizes (`0`, `1`, `SIZE_MAX`, malformed input, OOM paths).
