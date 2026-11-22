---
name: native-gui-architecture
description: "Production native desktop GUI engineering in C/C++ (Win32 + Direct2D/DirectWrite, Dear ImGui, Nuklear, Clay, GTK4, SDL3). Covers DPI scaling, 60/120fps rendering, threading, dark mode, and crisp desktop UX."
license: MIT
compatibility: opencode
---
# Native Desktop GUI Architecture (C / C++)

Build native desktop applications that feel instantaneous, razor-sharp, and rock-solid.

## 1. Choosing the Right Stack
- **Windows Native Ultra-Light (C/C++):** Win32 + Direct2D + DirectWrite + DWM (`DwmSetWindowAttribute` for dark titlebar/Mica). Best for zero-dependency system utilities with native feel.
- **Cross-Platform Tooling / Editors / Debuggers:** SDL3 (or GLFW) + Dear ImGui (docking branch) or pure-C **Clay** / **Nuklear** + GPU renderer (Vulkan/D3D11/Metal/OpenGL). Best for high-density pro tools, profilers, audio/game editors.
- **Linux/Cross-Platform Standard Desktop:** GTK4 (pure C GObject) with CSS styling and `GListModel` virtualization.

## 2. Non-Negotiable Desktop Engineering Rules
- **UI Thread Purity:** NEVER perform disk I/O, network calls, heavy parsing, or subprocess waits on the UI thread. Offload to a worker thread pool; communicate back via lock-free ring buffer / atomic queue + `PostMessage` / `SDL_PushEvent` / `g_idle_add`.
- **Per-Monitor DPI v2:** Never hardcode pixel coordinates without scaling by current monitor DPI (`dpi / 96.0f`). Handle `WM_DPICHANGED` dynamically; recreate font/bitmap resources cleanly on scale change.
- **Zero-Flicker & Frame Pacing:**
  - Retained-mode: double-buffer / Direct2D swapchain, invalidate dirty rects only, handle `WM_ERASEBKGND` returning `1`.
  - Immediate-mode: event-driven wakeup (`WaitEventTimeout`) when idle so GPU/CPU usage drops to ~0% instead of spinning at 100% on a static screen; switch to VSync/120fps during active animations/dragging.
- **Deterministic Resource Lifetime:** Pair every GPU/GDI/Direct2D resource (`ID2D1Brush`, `HFONT`, textures) with explicit release on device-lost (`D2DERR_RECREATE_TARGET`) and shutdown.

## 3. Native UX Craft
- **Typography:** Use system UI fonts (`Segoe UI Variable` on Windows, `Inter`/`SF Pro` on macOS, system sans on Linux) + tabular monospace (`JetBrains Mono` / `Cascadia Mono`) for numeric tables, hex views, and logs.
- **Keyboard First:** Full Tab order, Esc to cancel, Ctrl+K command palette (for complex tools), clear focus rings, standard platform shortcuts.
- **State Completeness:** Every async view MUST render clean loading, empty, error (with retry), and populated states without layout jumping.
