#!/usr/bin/env node
/**
 * Horus Context Mode — OpenCode MCP stdio JSON-RPC server.
 * Adapted from Domush/antigravity-plugin-context-mode (MIT).
 * Requires Node.js >= 22.5.0 (built-in node:sqlite + FTS5, zero npm dependencies).
 */
import fs from "node:fs";
import path from "node:path";
import readline from "node:readline";
import { fileURLToPath } from "node:url";
import { ContextModeStore } from "./lib/store.js";
import { createTools } from "./lib/tools.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
let pkgVersion = "2.0.0";
try {
  const pkg = JSON.parse(fs.readFileSync(path.join(__dirname, "package.json"), "utf8"));
  if (pkg.version) pkgVersion = pkg.version;
} catch {}

const cliArg = process.argv[2];
if (cliArg === "--version" || cliArg === "-v") {
  console.log(`horus-context-mode v${pkgVersion}`);
  process.exit(0);
}
if (cliArg === "--help" || cliArg === "-h") {
  console.log(`Horus Context Mode MCP Server (v${pkgVersion})
Usage:
  node .opencode/context-mode/server.js                 Start MCP stdio JSON-RPC server
  node .opencode/context-mode/dashboard/server.mjs      Start standalone web dashboard
  node .opencode/context-mode/server.js --version       Print version
Requirements: Node.js >= 22.5.0 (built-in node:sqlite).`);
  process.exit(0);
}

const store = new ContextModeStore();
let currentCwd = process.cwd();
let currentSessionId =
  process.env.HORUS_SESSION_ID ||
  process.env.OPENCODE_SESSION_ID ||
  process.env.CONVERSATION_ID ||
  "default";

const tools = createTools({
  store,
  getCwd: () => currentCwd,
  getSessionId: () =>
    process.env.HORUS_ROOT_SESSION_ID ||
    process.env.HORUS_SESSION_ID ||
    process.env.OPENCODE_SESSION_ID ||
    process.env.CONVERSATION_ID ||
    currentSessionId ||
    "default"
});

const TOOL_DEFINITIONS = [
  {
    name: "ctx_execute",
    description:
      "Execute JavaScript, Python, PowerShell, or Shell code in a local sandbox to process large logs, filter data, or compute results without dumping raw output into the OpenCode context window.",
    inputSchema: {
      type: "object",
      properties: {
        language: {
          type: "string",
          enum: ["javascript", "nodejs", "python", "shell", "powershell", "cmd"],
          description: "Runtime language"
        },
        code: { type: "string", description: "Source code snippet to execute" },
        file: { type: "string", description: "Optional script file path to execute" },
        args: { type: "array", items: { type: "string" }, description: "Optional command-line arguments" },
        intent: { type: "string", description: "One-line explanation of what this script analyzes" }
      }
    }
  },
  {
    name: "ctx_batch",
    description:
      "Execute multiple shell commands in batch, indexing all outputs into SQLite FTS5 and returning only matching search snippets to preserve tokens.",
    inputSchema: {
      type: "object",
      properties: {
        commands: { type: "array", items: { type: "string" }, description: "List of shell commands to execute" },
        queries: {
          type: "array",
          items: { type: "string" },
          description: "Search queries to filter and extract from the combined output"
        }
      },
      required: ["commands"]
    }
  },
  {
    name: "ctx_search",
    description:
      "Search the local SQLite FTS5 database across indexed logs, files, tool outputs, and documentation using BM25 + Trigram RRF. If path is a file, directory, or URL, it is automatically indexed Just-In-Time if unindexed or modified.",
    inputSchema: {
      type: "object",
      properties: {
        queries: { type: "array", items: { type: "string" }, description: "Search queries or tokens to match" },
        path: {
          type: "string",
          description: "Path to a file, directory, or URL to search (auto-indexed Just-In-Time if unindexed or changed). Omit to search active session."
        },
        scope: {
          type: "string",
          enum: ["session", "worktree", "all"],
          description: "Search scope when path is omitted (default: session)"
        },
        limit: { type: "integer", description: "Max number of snippets to return (default 5)" },
        offset: { type: "integer", description: "Offset for pagination" },
        reverse: {
          type: "boolean",
          description: "Search in reverse order (tail-first), prioritizing the newest lines/entries at the end of log files (default: false)"
        }
      },
      required: ["queries"]
    }
  },
  {
    name: "ctx_resume",
    description: "Retrieve current session state, active sources, indexed items, and compaction pointers.",
    inputSchema: {
      type: "object",
      properties: {
        seq: { type: "integer", description: "Optional journal event sequence to retrieve" }
      }
    }
  },
  {
    name: "ctx_stats",
    description:
      "Show Horus Context Mode token savings report (raw bytes vs tokens returned to LLM, savings percentage, and database metrics).",
    inputSchema: {
      type: "object",
      properties: {
        reset: { type: "boolean", description: "Reset session statistics" }
      }
    }
  },
  {
    name: "ctx_doctor",
    description: "Check Horus Context Mode SQLite database health, FTS5 availability, schema, and active runtimes.",
    inputSchema: {
      type: "object",
      properties: {}
    }
  },
  {
    name: "ctx_purge",
    description: "Purge indexed sources and journal records for this session, worktree, or entire database.",
    inputSchema: {
      type: "object",
      properties: {
        scope: { type: "string", enum: ["session", "worktree", "all"], description: "Purge scope" }
      }
    }
  }
];

function sendJsonRpc(obj) {
  process.stdout.write(JSON.stringify(obj) + "\n");
}

function sendResponse(id, result) {
  sendJsonRpc({ jsonrpc: "2.0", id, result });
}

function sendError(id, code, message, data) {
  sendJsonRpc({
    jsonrpc: "2.0",
    id,
    error: { code, message, ...(data !== undefined ? { data } : {}) }
  });
}

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  terminal: false
});

rl.on("line", async (line) => {
  const trimmed = line.trim();
  if (!trimmed) return;

  let msg;
  try {
    msg = JSON.parse(trimmed);
  } catch (err) {
    sendError(null, -32700, "Parse error", String(err));
    return;
  }

  const { id, method, params } = msg;
  if (id === undefined || id === null) return;

  try {
    switch (method) {
      case "initialize": {
        if (params?.rootPath) currentCwd = params.rootPath;
        if (params?.sessionId) currentSessionId = params.sessionId;
        sendResponse(id, {
          protocolVersion: "2024-11-05",
          capabilities: { tools: {} },
          serverInfo: { name: "horus-context-mode", version: pkgVersion }
        });
        break;
      }
      case "ping": {
        sendResponse(id, {});
        break;
      }
      case "tools/list": {
        sendResponse(id, { tools: TOOL_DEFINITIONS });
        break;
      }
      case "tools/call": {
        const toolName = params?.name;
        const toolArgs = params?.arguments || {};
        const callSessionId =
          toolArgs.sessionId ||
          params?._meta?.sessionId ||
          params?._meta?.conversationId ||
          params?.sessionId;
        if (callSessionId) currentSessionId = callSessionId;

        if (!tools[toolName]) {
          sendError(id, -32601, `Unknown tool: ${toolName}`);
          break;
        }

        try {
          const result = await tools[toolName](toolArgs);
          sendResponse(id, {
            content: [
              {
                type: "text",
                text: typeof result === "string" ? result : JSON.stringify(result, null, 2)
              }
            ],
            isError: false
          });
        } catch (toolErr) {
          sendResponse(id, {
            content: [
              {
                type: "text",
                text: `Tool error (${toolName}): ${toolErr.message || String(toolErr)}`
              }
            ],
            isError: true
          });
        }
        break;
      }
      default: {
        sendError(id, -32601, `Method not found: ${method}`);
        break;
      }
    }
  } catch (handlerErr) {
    sendError(id, -32603, "Internal server error", String(handlerErr));
  }
});

process.on("SIGINT", () => {
  store.close();
  process.exit(0);
});

process.on("SIGTERM", () => {
  store.close();
  process.exit(0);
});
