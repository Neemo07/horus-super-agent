---
name: reverse-engineer-anything
description: "Inspect PE/ELF/Mach-O binaries, Electron/JS bundles, archives, and binary hardening via REA MCP or CLI."
license: MIT
compatibility: opencode
metadata:
  source: https://github.com/morluto/rea
---
# Reverse Engineer Anything (REA) — Dedicated Tool Routing & Evidence Skill

Use REA (`morluto/rea`) when a software analysis, compatibility, porting, or defensive audit claim depends on a shipped binary, package, or artifact rather than available source code. Skip REA for ordinary complete-source repositories.

## 1. Connection, CLI Fallback & Recovery
- **MCP first:** If REA MCP tools are already connected in OpenCode, call them directly—do not run `rea doctor` or `rea setup` on every task.
- **Enable in `opencode.jsonc`:**
  ```jsonc
  "mcp": {
    "rea": {
      "type": "local",
      "command": ["npx", "-y", "rea-agents@latest", "mcp"],
      "enabled": true
    }
  }
  ```
- **CLI fallback (when MCP is unavailable):** Prefer an existing `rea` CLI, or run `npx -y rea-agents@latest <command> /abs/path/to/target --json` from a trusted directory outside the target project.
- **Honest recovery:** Never auto-install Node.js, Java, Ghidra, IDA, Hopper, or Kuna. If a connection fails or an engine is missing, run `rea doctor`, report the exact blocker, and continue with zero-engine built-in REA tools where possible.

## 2. Target-First REA Tool Routing

### Windows PE32 / PE32+ (Zero-Engine Built-in Tools — Run First)
- `inspect_pe_imports` — DLL names, named/ordinal imports, ILT/IAT RVAs, delay-load descriptors, import hash.
- `inspect_native_exports` — PE export directories & ordinals (also supports ELF dynamic exports).
- `inspect_pe_resources` — Resource type/name/language trees, icon groups, manifests/dialogs (file ranges + SHA-256).
- `inspect_pe_load_config` — TLS callbacks (VA/RVA/offset/section), security cookie, SafeSEH, CFG, EH-continuation, XFG.
- `inspect_pe_certificates` — Authenticode `WIN_CERTIFICATE` ranges & PKCS#7 signer identity.
- `inspect_binary_hardening` — Cross-platform PE/ELF/Mach-O mitigation audit (ASLR, DEP/NX, CFG, SafeSEH, stack-protector) with exact header fields.

### Linux ELF & macOS Mach-O (Zero-Engine Built-in Tools)
- `inspect_elf_dependencies` — `DT_NEEDED`, `DT_SONAME`, `RPATH`/`RUNPATH`, `PT_INTERP`, symbol versions.
- `inspect_elf_notes`, `inspect_dwarf_units`, `inspect_elf_unwind_ranges`, `inspect_native_initializers` — Build-IDs, DWARF compile units, unwind ranges, init/fini tables.
- `inspect_rust_binary` / `inspect_go_binary` — Embedded `cargo-auditable` dependency metadata or Go module/build metadata.

### Deep Static Analysis (Requires Installed Engine: Ghidra / IDA / Hopper / Kuna)
- `open_binary` — Open native binary or archive target for disassembly/decompilation.
- `trace_native_values` — Static value and data-flow tracing (establishes static facts only, not runtime execution).

### Packages, Electron / JS, Managed & Defensive Audits
- **Electron / ASAR / JS trees:** `analyze_javascript_application` (or `open_binary` → `inspect_artifact` with `detail: "summary"` → targeted `source_paths`). Check Electron fuses with `inspect_electron_fuses`.
- **Archives / Installers (ZIP, APK, IPA, MSIX, DMG, PyInstaller, Bun, Deno):** `open_binary` → `inspect_artifact` (`detail: "summary"` first for large inventories).
- **Managed .NET PE/CLI:** `inspect_managed_artifact`.
- **Release Exposure Audit (Defensive):** `audit_release_exposure` / `rea audit-release-exposure` on local `.app`, install dir, ASAR, or executable. Preserve unknown/unassessed checks honestly.
- **SQLite / Captures:** `inspect_sqlite_database` (schema first), `inspect_web_network_capture` (HAR/SAZ/mitmproxy/qlog), `inspect_pcap_capture` / `inspect_packet_capture` (recorded captures only).

## 3. Strict Evidence & Anti-Hallucination Contract
- **Preserve Evidence IDs & Digests:** Quote exact SHA-256 digests, VAs/RVAs, section ranges, and `parent_evidence_id` references. Use `detail: "summary"` + `inspect_analysis_view` paging for large outputs instead of dumping raw megabytes into context.
- **Observed Absence != Proof:** A missing import table, security directory, or metadata section is observed absence of that table—never claim it proves the binary is unsigned or never loads APIs dynamically.
- **Static != Runtime:** Never claim observed runtime behavior solely from static decompilation or header inspection.
- **Scope Boundary:** Use REA strictly for authorized software comprehension, compatibility/porting, interoperability, and defensive security auditing. Do not generate exploit payloads or DRM-bypass workflows.
