---
name: native-gui-architecture
description: "Native C/C++ desktop GUI (Win32/Direct2D, ImGui, GTK4, SDL3, Clay): DPI scaling, 120fps rendering, threading, dark."
license: MIT
compatibility: opencode, antigravity, dsh
metadata:
  version: "0.8.0-horus"
---
# Native Desktop GUI Architecture (C / C++)

Build native desktop applications that feel instantaneous, razor-sharp, and rock-solid across high-DPI monitors, dark/light themes, and heavy workloads.

## 1. Choosing the Right Stack
- **Windows Native Ultra-Light (C/C++):** Win32 + Direct2D + DirectWrite + DWM (`DwmSetWindowAttribute` with `DWMWA_USE_IMMERSIVE_DARK_MODE` / `DWMWA_SYSTEMBACKDROP_TYPE` for Mica/Acrylic). Best for zero-dependency system utilities with native Windows 11 feel.
- **Cross-Platform Pro Tools / Editors / Debuggers:** SDL3 (or GLFW) + Dear ImGui (docking branch) or pure-C **Clay** / **Nuklear** + GPU renderer (D3D11/Vulkan/Metal/OpenGL). Best for high-density audio, RE, profiler, and game tools.
- **Linux / Cross-Platform Standard Desktop:** GTK4 (pure C GObject) with CSS tokens and `GListModel` virtualization for large lists.

## 2. Non-Negotiable Desktop Engineering Rules
- **UI Thread Purity:** NEVER perform disk I/O, network calls, heavy parsing, or subprocess waits on the UI thread. Offload to a worker thread pool; communicate back via lock-free ring buffer / atomic queue + `PostMessageW` (Win32) / `SDL_PushEvent` (SDL3) / `g_idle_add` (GTK4).
- **Per-Monitor DPI v2 (Windows & Cross-Platform):**
  - Declare `SetProcessDpiAwarenessContext(DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2)` (or manifest equivalent) before window creation.
  - Never hardcode unscaled pixel coordinates — scale every metric by `dpi / 96.0f`.
  - Handle `WM_DPICHANGED`: apply the suggested `RECT*` from `lParam`, rebuild fonts/DPI-dependent bitmaps cleanly, and redraw.
- **Zero-Flicker & Smart Frame Pacing:**
  - Retained-mode (Win32/Direct2D): use Direct2D / DXGI swapchain (`DXGI_SWAP_EFFECT_FLIP_DISCARD`), handle `WM_ERASEBKGND` returning `1`, and invalidate dirty rects only.
  - Immediate-mode (ImGui/SDL3): use event-driven wakeup (`SDL_WaitEventTimeout`) when idle so CPU/GPU usage drops near ~0% on a static screen; switch to VSync / 120fps only during active input, scrolling, or animations.
- **Deterministic GPU/GDI Lifetime & Device-Loss Recovery:**
  - Pair every `ID2D1Brush`, `IDWriteTextFormat`, `HFONT`, and texture with RAII release (`ComPtr` / `UniqueHandle`).
  - Handle `D2DERR_RECREATE_TARGET` / `DXGI_ERROR_DEVICE_REMOVED` by discarding device-dependent resources cleanly and recreating them on the next frame without crashing.

## 3. Native UX Craft & Accessibility
- **Typography & Tokens:** Use system UI fonts (`Segoe UI Variable` on Windows, `SF Pro` on macOS, system sans on Linux) + tabular monospace (`Cascadia Mono` / `JetBrains Mono`) for hex dumps, tables, and logs. Follow `ui-ux-design-systems` semantic tokens and 4/8px spacing grids (never raw hardcoded hex scattered in paint code).
- **Keyboard First:** Complete Tab order, `Esc` to cancel, `Ctrl+K` command palette for complex tools, visible focus rings (≥ 3:1 contrast), and native platform accelerators.
- **State Completeness:** Every async view MUST render clean `loading`, `empty`, `error` (with retry), and `populated` states without layout jumping.

## 4. Mandatory Verification Gate (Before Returning `STATUS: DONE`)
- Build with strict warnings (`/W4 /WX` or `-Wall -Wextra -Werror`) and verify zero GDI/HANDLE/COM leaks on window create → resize → close cycles.
- Verify **100%, 150%, and 200% DPI** scaling (no clipped text or blurry bitmaps), **Light + Dark** theme switching, **keyboard-only** navigation, and **idle CPU < 1%** when no animation is active.
- Route large build/crash/ETW logs through `ctx_search` (`horus-context-mode`) and check callers via `graphify query` before refactoring shared UI state.
