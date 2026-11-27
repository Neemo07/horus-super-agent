---
name: cpp20-win32-re
description: "Port legacy Win32/x86 C++ and PE32/PE32+ binaries to clean modern C++20 (_WIN64) using REA/Ghidra evidence."
license: MIT
compatibility: opencode, antigravity, dsh
metadata:
  source: https://github.com/morluto/rea
  version: "0.8.0-horus"
---
# C++20 / Win32 Reverse Engineering & x86→x64 Reconstruction (REA)

Evidence-first reverse engineering and clean-room reconstruction for Windows PE32/PE32+ binaries, legacy MSVC C++ codebases, and Win32/DirectX engines using **REA (`morluto/rea`)** + Ghidra/IDA + Graphify + Horus Context Mode.

## 1. REA Tool Routing & Large-Tree Navigation
Use REA whenever a claim depends on a shipped binary, decompilation, or runtime evidence. Skip REA for ordinary complete-source repos.
- **Zero-Engine Built-in PE Triage (run first):** `inspect_pe_imports`, `inspect_native_exports`, `inspect_pe_resources`, `inspect_pe_load_config`, `inspect_pe_certificates`, `inspect_binary_hardening`.
- **Deep Static Decompilation (requires Ghidra / IDA / Hopper / Kuna):** `open_binary`, `trace_native_values` (static facts only — never claim runtime behavior from static analysis alone).
- **Large Decompilation Trees & Build Logs:** Index decompiled trees with `graphify extract . --code-only` (`graphify query/path/explain`) and route huge disassembly dumps or MSVC warning logs through `ctx_search`/`ctx_execute` (`horus-context-mode`).
- **CLI Fallback:** `rea` CLI or `npx -y rea-agents@latest <command> /abs/path/to/target --json`. Never auto-install Node/Java/Ghidra/IDA; diagnose missing engines via `rea doctor`.

## 2. MSVC C++ ABI & Binary Structure Recovery
- **Calling Conventions:**
  - x86: `__cdecl` (caller cleans), `__stdcall` (callee cleans, Win32 APIs), `__thiscall` (`ECX` = `this`, callee cleans), `__fastcall` (`ECX`/`EDX`).
  - x64 (`_WIN64`): unified Microsoft x64 ABI (`RCX, RDX, R8, R9` / `XMM0..3`, 32-byte shadow space, 16-byte stack alignment).
- **Vtables & RTTI Recovery:**
  - Trace `vftable` pointers written in constructors/destructors; cross-reference MSVC `RTTI Complete Object Locator` (`COL`) and `TypeDescriptor` mangled names to reconstruct exact class hierarchies and virtual slot indices.
  - Never guess indirect virtual call targets — resolve through the concrete `vftable` + offset and cite the VA/RVA.
- **Struct & Binary Format Layout Verification:**
  - Lock every recovered binary/packet/asset struct with compile-time layout assertions:
    ```cpp
    static_assert(sizeof(PacketHeader) == 6);
    static_assert(offsetof(PacketHeader, opcode) == 2);
    ```
  - For binary parsers (wire protocols, archive VFS, mesh/texture/env formats), NEVER cast raw byte buffers to structs directly. Read via explicit little-endian cursor helpers (`std::span<const std::byte>` + `std::memcpy` / `std::bit_cast`) with strict bounds checks on every read.

## 3. Porting Legacy x86 Win32 C++ → Modern x64 C++20 (`/std:c++20`, `_WIN64`)

### x86 → x64 Porting Hazard Matrix (Check Every Module)
| Legacy x86 Trap | Safe `_WIN64` C++20 Replacement |
| :--- | :--- |
| `DWORD`/`LONG`/`int` holding pointers or sizes | `uintptr_t`, `size_t`, `ptrdiff_t`, `DWORD_PTR`, `LONG_PTR`, `INT_PTR`, `LRESULT`, `WPARAM`, `LPARAM` |
| `GetWindowLong`/`SetWindowLong` (`GWL_USERDATA`, `GWL_WNDPROC`) | `GetWindowLongPtr`/`SetWindowLongPtr` (`GWLP_USERDATA`, `GWLP_WNDPROC`) |
| Implicit `#pragma pack` or pointer-sized fields on the wire | Explicit fixed-width `uint8_t`/`uint16_t`/`uint32_t`/`uint64_t` + `#pragma pack(push, 1)` ONLY on wire views with `static_assert` |
| 32-bit `time_t` serialized to disk/network | Explicit `int32_t`/`uint32_t` or `int64_t` wire type (never serialize raw `time_t`) |
| Legacy x86 inline `__asm` | `<intrin.h>` intrinsics (`_rotl`, `_byteswap_ulong`, `_BitScanForward`, SSE2/AVX2) or C++20 `<bit>` |
| Raw `HANDLE`/`HMODULE`/`HKEY`/`ID3D*` | Zero-overhead RAII (`wil::unique_handle`, `UniqueHandle<Traits>`, `Microsoft::WRL::ComPtr`) |
| `std::auto_ptr`, `hash_map`, `strcpy`/`sprintf`, VC++ extensions | `std::unique_ptr`, `std::unordered_map`, `std::string_view`, `std::span`, `std::format`, `/permissive-` |
| Mixing Win32 SEH (`__try`) with C++ destructors | Isolate SEH into leaf C-style helpers or explicitly document `/EHa` vs `/EHsc` |

- Preserve original folder/module organization when requested, and document verified bugs from the original binary inline as `// BUG(<ID>): <observed binary flaw & fix>` rather than silently hiding behavioral changes.

## 4. Evidence & Golden-Vector Differential Verification Gate
- **Observed Absence != Proof:** A missing PE import/export/security table is observed absence, not proof the binary never resolves APIs dynamically (`GetProcAddress` / ordinal).
- **Zero Skeletons:** `// TODO` stubs and guessed magic numbers are banned. Every constant, Win32 flag, struct offset, and opcode must cite its source VA/RVA, REA Evidence ID, or official Win32 header.
- **Differential Proof Gate:** Validate reconstructed parsers, crypto/compression routines, and state machines against golden input/output test vectors extracted from the original binary; compile clean with `/std:c++20 /W4 /WX /permissive-` (+ `/fsanitize=address` in Debug) or `-std=c++20 -Wall -Wextra -Wpedantic -Werror -fsanitize=address,undefined`.
