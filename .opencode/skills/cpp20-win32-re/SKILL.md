---
name: cpp20-win32-re
description: "Reverse engineer Windows PE32/PE32+ binaries and reconstruct/port legacy Win32 C++ (x86/MSVC) to clean modern C++20 (_WIN64) using REA (morluto/rea), Ghidra/IDA, and evidence-backed verification."
license: MIT
compatibility: opencode
metadata:
  source: https://github.com/morluto/rea
---
# C++20 / Win32 Reverse Engineering & x86→x64 Reconstruction (REA)

Evidence-first reverse engineering and clean-room reconstruction for Windows PE32/PE32+ binaries, legacy MSVC C++ codebases, and Win32/DirectX engines using **REA (`morluto/rea`)** + Ghidra/IDA + Graphify.

## 1. REA Tool Routing for Windows PE32/PE32+ Targets
Use REA whenever a claim depends on a shipped binary, decompilation, or runtime evidence. Skip REA for ordinary complete-source repos.
- **Zero-Engine Built-in PE Triage (run first — fast, deterministic, no Windows SDK or disassembler required):**
  - `inspect_pe_imports` — DLL names, named/ordinal imports, ILT/IAT RVAs, delay-load descriptors, import hash.
  - `inspect_native_exports` — PE export directory & ordinals.
  - `inspect_pe_resources` — Resource type/name/language trees, icon groups, embedded manifests/dialogs (file ranges + SHA-256).
  - `inspect_pe_load_config` — TLS callbacks (VA/RVA/offset/section), security cookie, SafeSEH, CFG, EH-continuation, XFG.
  - `inspect_pe_certificates` — Authenticode `WIN_CERTIFICATE` ranges & PKCS#7 signer identity.
  - `inspect_binary_hardening` — ASLR, DEP/NX, CFG, SafeSEH, stack-protector status with exact header fields.
- **Deep Static Decompilation & Tracing (requires Ghidra / IDA / Hopper / Kuna):**
  - `open_binary` — open target PE for disassembly/decompilation.
  - `trace_native_values` — static data-flow / constant tracing (static facts only, does not prove runtime execution).
- **CLI Fallback (if REA MCP is not registered):**
  - Prefer existing `rea` CLI, or `npx -y rea-agents@latest <command> /abs/path/to/target --json`.
  - Never install Node/Java/Ghidra/IDA automatically; diagnose missing engines honestly via `rea doctor`.

## 2. MSVC C++ ABI & Binary Structure Recovery
- **Calling Conventions:**
  - x86: `__cdecl` (caller cleans), `__stdcall` (callee cleans, Win32 APIs), `__thiscall` (`ECX` = `this`, callee cleans), `__fastcall` (`ECX`/`EDX`).
  - x64 (`_WIN64`): unified Microsoft x64 ABI (`RCX, RDX, R8, R9` / `XMM0..3`, 32-byte shadow space, 16-byte stack alignment).
- **Vtables & RTTI Recovery:**
  - Trace `vftable` pointers written in constructors/destructors; cross-reference MSVC `RTTI Complete Object Locator` (`COL`) and `TypeDescriptor` mangled names to reconstruct exact class hierarchies and virtual slot indices.
  - Never guess indirect virtual call targets—resolve through the concrete `vftable` + offset and cite the VA/RVA.
- **Struct & Binary Format Layout Verification:**
  - Lock every recovered binary/packet/asset struct with compile-time layout assertions:
    ```cpp
    static_assert(sizeof(PacketHeader) == 6);
    static_assert(offsetof(PacketHeader, opcode) == 2);
    ```
  - For binary parsers (wire protocols, archive VFS, mesh/texture/env formats), NEVER cast raw byte buffers to structs directly. Read via explicit little-endian cursor helpers (`std::span<const std::byte>` + `std::memcpy` / `std::bit_cast`) with strict bounds checks on every read.

## 3. Porting Legacy x86 Win32 C++ → Modern x64 C++20 (`/std:c++20`, `_WIN64`)
- **64-Bit Portability & Pointer-Width Traps:**
  - Replace `DWORD`/`LONG`/`int` storing pointers or sizes with `uintptr_t`, `size_t`, `DWORD_PTR`, `LONG_PTR`, `INT_PTR`, `LRESULT`, `WPARAM`, `LPARAM`.
  - Replace `GetWindowLong`/`SetWindowLong` (`GWL_USERDATA`, `GWL_WNDPROC`) with `GetWindowLongPtr`/`SetWindowLongPtr` (`GWLP_USERDATA`, `GWLP_WNDPROC`).
  - Keep wire-protocol and on-disk fields strictly fixed-width (`uint8_t`, `uint16_t`, `uint32_t`, `uint64_t`) so x64 builds remain 100% wire-compatible with x86 binaries.
- **Replacing Legacy VC++ 2005–2010 Idioms:**
  - Replace x86 inline `__asm` blocks with `<intrin.h>` intrinsics (`_rotl`, `_byteswap_ulong`, `_BitScanForward`, SSE2/AVX2) or portable C++20 `<bit>`.
  - Replace raw `HANDLE`/`HMODULE`/`HKEY`/`ID3D*`/heap pointers with lightweight zero-overhead RAII wrappers (`wil::unique_handle` or custom `UniqueHandle<Traits>` / `Microsoft::WRL::ComPtr`).
  - Replace `std::auto_ptr`, `hash_map`, unsafe `strcpy`/`sprintf`, and non-standard MSVC extensions with `std::unique_ptr`, `std::unordered_map`, `std::string_view`, `std::span`, `std::format`, and `/permissive-`.
  - Preserve original folder/module organization when requested, and document verified bugs from the original binary inline as `// BUG(<ID>): <observed binary flaw & fix>` rather than silently hiding behavioral changes.

## 4. Evidence & Anti-Hallucination Rules
- **Observed Absence != Proof:** Following REA's contract, a missing PE import/export/security table is observed absence of that table, not proof the binary never resolves APIs dynamically (`GetProcAddress` / ordinal / manual syscall).
- **Zero Skeletons:** `// TODO` stubs and guessed magic numbers are banned. Every constant, Win32 flag, struct offset, and opcode must cite its source VA/RVA, REA Evidence ID, or official Win32 header.
- **Differential Verification:** Validate reconstructed parsers, crypto/compression routines, and state machines against golden test vectors extracted from the original binary; compile with `/std:c++20 /W4 /WX /permissive-` (MSVC) or `-std=c++20 -Wall -Wextra -Wpedantic -Werror`.
