import fs from "node:fs";
import path from "node:path";
import http from "node:http";
import os from "node:os";
import { execSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { ContextModeStore, FILE_CATEGORIES } from "../lib/store.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const store = new ContextModeStore();
const HTML_FILE = path.join(__dirname, "index.html");

function getPackageVersion() {
  try {
    const pkg = JSON.parse(fs.readFileSync(path.join(__dirname, "../package.json"), "utf8"));
    if (pkg.version) return pkg.version;
  } catch {}
  return "1.0.0";
}

function getRenderedHtml() {
  const raw = fs.readFileSync(HTML_FILE, "utf8");
  const ver = getPackageVersion();
  return raw.replace('id="dashboard-version">--</span>', `id="dashboard-version">v${ver}</span>`);
}

let appStartTime = Date.now() - Math.round(process.uptime() * 1000);
if (!appStartTime) {
  appStartTime = Date.now() - Math.round(process.uptime() * 1000);
}

// Clear session-level overrides on app session restart
try {
  const recordedSessionTime = store.getMeta("app_session_start_time");
  if (!recordedSessionTime || recordedSessionTime !== String(appStartTime)) {
    store.clearSessionOverrides();
    store.setMeta("app_session_start_time", String(appStartTime));
  }
} catch {}

function resolveTargetSession(data, defaultConvId = "default") {
  const scope = data.scope || (data.sessionId === "all" ? "lifetime" : (data.sessionId === "app" ? "app" : "conversation"));
  const convId = data.conversationId || (data.sessionId !== "all" && data.sessionId !== "app" && data.sessionId ? data.sessionId : (defaultConvId || "default"));
  let targetSid = convId;
  if (scope === "lifetime" || scope === "all") targetSid = "all";
  else if (scope === "app" || scope === "session") targetSid = "app";
  return { scope, convId, targetSid };
}

function getStatsPayload(data, defaultConvId = "default") {
  const { scope, convId, targetSid } = resolveTargetSession(data, defaultConvId);
  let stats;
  if (scope === "lifetime" || scope === "all") {
    stats = store.getStats("all");
  } else if (scope === "app" || scope === "session") {
    stats = store.getStats("app", { sinceTs: appStartTime });
  } else {
    stats = store.getStats(convId);
  }

  stats.scope = scope;
  stats.conversationId = convId;
  stats.appStartTime = appStartTime;
  stats.conversationCutoffBytes = store.getCutoff(convId);
  stats.appCutoffBytes = store.getCutoff("app");
  stats.globalCutoffBytes = store.getCutoff(null);
  stats.hasConversationCutoffOverride = store.hasCutoffOverride(convId);
  stats.hasAppCutoffOverride = store.hasCutoffOverride("app");
  stats.cutoffBytes = scope === "lifetime"
    ? stats.globalCutoffBytes
    : (scope === "app" ? stats.appCutoffBytes : stats.conversationCutoffBytes);

  stats.conversationMaxAutoIndexBytes = store.getMaxAutoIndexBytes(convId);
  stats.appMaxAutoIndexBytes = store.getMaxAutoIndexBytes("app");
  stats.globalMaxAutoIndexBytes = store.getMaxAutoIndexBytes(null);
  stats.maxAutoIndexBytes = scope === "lifetime"
    ? stats.globalMaxAutoIndexBytes
    : (scope === "app" ? stats.appMaxAutoIndexBytes : stats.conversationMaxAutoIndexBytes);

  stats.conversationExemptExtensions = store.getExemptExtensions(convId);
  stats.appExemptExtensions = store.getExemptExtensions("app");
  stats.globalExemptExtensions = store.getExemptExtensions(null);
  stats.exemptExtensions = scope === "lifetime"
    ? stats.globalExemptExtensions
    : (scope === "app" ? stats.appExemptExtensions : stats.conversationExemptExtensions);

  stats.fileCategories = Object.values(FILE_CATEGORIES);
  stats.conversationExemptCategories = store.getExemptCategories(convId);
  stats.appExemptCategories = store.getExemptCategories("app");
  stats.globalExemptCategories = store.getExemptCategories(null);
  stats.exemptCategories = scope === "lifetime"
    ? stats.globalExemptCategories
    : (scope === "app" ? stats.appExemptCategories : stats.conversationExemptCategories);

  stats.conversationCustomExtensions = store.getCustomExemptExtensions(convId);
  stats.appCustomExtensions = store.getCustomExemptExtensions("app");
  stats.globalCustomExtensions = store.getCustomExemptExtensions(null);
  stats.customExtensions = scope === "lifetime"
    ? stats.globalCustomExtensions
    : (scope === "app" ? stats.appCustomExtensions : stats.conversationCustomExtensions);

  // Sandbox cap is always double the current cutoff setting (or default 32 KB if none)
  stats.sandboxCapBytes = stats.cutoffBytes > 0
    ? (stats.cutoffBytes * 2)
    : parseInt(process.env.CONTEXT_MODE_MAX_OUTPUT_BYTES || "32768", 10);
  stats.isPaused = store.isPaused(targetSid);

  stats.version = getPackageVersion();

  return stats;
}

// Standalone HTTP dashboard server for OpenCode / Horus Context Mode
{
  // Standalone HTTP server for preview/testing
  const port = process.env.PORT || 8765;
  const server = http.createServer((req, res) => {
    const url = new URL(req.url, `http://localhost:${port}`);

    if (req.method === "GET" && (url.pathname === "/" || url.pathname === "/index.html")) {
      res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
      res.end(getRenderedHtml());
      return;
    }

    if (req.method === "GET" && url.pathname === "/api/stats") {
      const data = Object.fromEntries(url.searchParams.entries());
      const stats = getStatsPayload(data);
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(JSON.stringify(stats));
      return;
    }

    if ((req.method === "GET" || req.method === "POST") && url.pathname === "/api/cutoff") {
      const handleCutoffReq = (data) => {
        const { scope, targetSid, convId } = resolveTargetSession(data);
        const cutoffBytes = data.cutoff === "none" || data.cutoff === 0 || data.cutoff === "0" ? 0 : parseInt(data.cutoff, 10);
        const saved = store.setCutoff(cutoffBytes, targetSid);
        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(
          JSON.stringify({
            ok: true,
            cutoffBytes: saved,
            scope,
            sessionId: targetSid,
            globalCutoffBytes: store.getCutoff(null),
            appCutoffBytes: store.getCutoff("app"),
            conversationCutoffBytes: store.getCutoff(convId)
          })
        );
      };
      if (req.method === "GET") {
        const data = Object.fromEntries(url.searchParams.entries());
        handleCutoffReq(data);
      } else {
        let body = "";
        req.on("data", (c) => (body += c));
        req.on("end", () => {
          try {
            handleCutoffReq(JSON.parse(body || "{}"));
          } catch (e) {
            res.writeHead(400, { "Content-Type": "application/json" });
            res.end(JSON.stringify({ error: e.message }));
          }
        });
      }
      return;
    }

    if ((req.method === "GET" || req.method === "POST") && url.pathname === "/api/auto-index-limit") {
      const handleAutoIndexReq = (data) => {
        const { scope, targetSid, convId } = resolveTargetSession(data);
        const limitBytes = data.limit === "none" || data.limit === 0 || data.limit === "0" ? 0 : parseInt(data.limit, 10);
        const saved = store.setMaxAutoIndexBytes(limitBytes, targetSid);
        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(
          JSON.stringify({
            ok: true,
            maxAutoIndexBytes: saved,
            scope,
            sessionId: targetSid,
            globalMaxAutoIndexBytes: store.getMaxAutoIndexBytes(null),
            appMaxAutoIndexBytes: store.getMaxAutoIndexBytes("app"),
            conversationMaxAutoIndexBytes: store.getMaxAutoIndexBytes(convId)
          })
        );
      };
      if (req.method === "GET") {
        const data = Object.fromEntries(url.searchParams.entries());
        handleAutoIndexReq(data);
      } else {
        let body = "";
        req.on("data", (c) => (body += c));
        req.on("end", () => {
          try {
            handleAutoIndexReq(JSON.parse(body || "{}"));
          } catch (e) {
            res.writeHead(400, { "Content-Type": "application/json" });
            res.end(JSON.stringify({ error: e.message }));
          }
        });
      }
      return;
    }

    if ((req.method === "GET" || req.method === "POST") && (url.pathname === "/api/toggle-active" || url.pathname === "/api/paused")) {
      const handleToggleReq = (data) => {
        const { scope, targetSid } = resolveTargetSession(data);
        const current = store.isPaused(targetSid);
        const newPaused = data.paused !== undefined ? (data.paused === true || data.paused === "true" || data.paused === "1") : !current;
        const saved = store.setPaused(newPaused, targetSid);
        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ ok: true, isPaused: saved, scope, sessionId: targetSid }));
      };
      if (req.method === "GET") {
        const data = Object.fromEntries(url.searchParams.entries());
        handleToggleReq(data);
      } else {
        let body = "";
        req.on("data", (c) => (body += c));
        req.on("end", () => {
          try {
            handleToggleReq(JSON.parse(body || "{}"));
          } catch (e) {
            res.writeHead(400, { "Content-Type": "application/json" });
            res.end(JSON.stringify({ error: e.message }));
          }
        });
      }
      return;
    }

    if ((req.method === "GET" || req.method === "POST") && url.pathname === "/api/exemptions") {
      const handleExemptReq = (data) => {
        const { scope, targetSid } = resolveTargetSession(data);
        const action = data.action || "get";
        if (action === "toggleCategory" && data.category) {
          store.toggleExemptCategory(data.category, data.enabled !== undefined ? (data.enabled === true || data.enabled === "true" || data.enabled === "1") : null, targetSid);
        } else if (action === "setCategories" && Array.isArray(data.categories)) {
          store.setExemptCategories(data.categories, targetSid);
        } else if (action === "add" && data.ext) {
          store.addCustomExemptExtension(data.ext, targetSid);
        } else if (action === "remove" && data.ext) {
          store.removeCustomExemptExtension(data.ext, targetSid);
        } else if (action === "reset") {
          store.setExemptCategories(null, targetSid);
          store.setCustomExemptExtensions([], targetSid);
        } else if (action === "set" && Array.isArray(data.extensions)) {
          store.setExemptExtensions(data.extensions, targetSid);
        }
        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(JSON.stringify({
          ok: true,
          exemptCategories: store.getExemptCategories(targetSid),
          customExtensions: store.getCustomExemptExtensions(targetSid),
          exemptExtensions: store.getExemptExtensions(targetSid),
          scope,
          sessionId: targetSid
        }));
      };
      if (req.method === "GET") {
        const data = Object.fromEntries(url.searchParams.entries());
        handleExemptReq(data);
      } else {
        let body = "";
        req.on("data", (c) => (body += c));
        req.on("end", () => {
          try {
            handleExemptReq(JSON.parse(body || "{}"));
          } catch (e) {
            res.writeHead(400, { "Content-Type": "application/json" });
            res.end(JSON.stringify({ error: e.message }));
          }
        });
      }
      return;
    }
    if ((req.method === "GET" || req.method === "POST") && url.pathname === "/api/purge") {
      const handlePurgeReq = (data) => {
        const { scope, convId } = resolveTargetSession(data);
        let result;
        if (scope === "lifetime" || scope === "all") {
          result = store.purge({ scope: "all" });
        } else if (scope === "app" || scope === "session") {
          result = store.purge({ scope: "app", sinceTs: appStartTime });
        } else {
          result = store.purge({ scope: "conversation", sessionId: convId });
        }
        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(JSON.stringify(result));
      };
      if (req.method === "GET") {
        const data = Object.fromEntries(url.searchParams.entries());
        handlePurgeReq(data);
      } else {
        let body = "";
        req.on("data", (c) => (body += c));
        req.on("end", () => {
          try {
            handlePurgeReq(JSON.parse(body || "{}"));
          } catch (e) {
            res.writeHead(400, { "Content-Type": "application/json" });
            res.end(JSON.stringify({ error: e.message }));
          }
        });
      }
      return;
    }

    if (req.method === "GET" && url.pathname === "/api/doctor") {
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(JSON.stringify(store.doctor()));
      return;
    }

    if (req.method === "GET" && url.pathname === "/api/resume") {
      const data = Object.fromEntries(url.searchParams.entries());
      const { scope, convId } = resolveTargetSession(data);
      let resume;
      if (scope === "lifetime" || scope === "all") {
        resume = store.getResumeState("all", 10);
      } else if (scope === "app" || scope === "session") {
        resume = store.getResumeState("app", 10, { sinceTs: appStartTime });
      } else {
        resume = store.getResumeState(convId, 10);
      }
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(JSON.stringify(resume));
      return;
    }

    if (req.method === "GET" && url.pathname === "/api/source-chunks") {
      const sourceId = url.searchParams.get("sourceId");
      const chunks = store.getSourceChunks(sourceId);
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ ok: true, sourceId, chunks }));
      return;
    }

    if (req.method === "POST" && url.pathname === "/api/search") {
      let body = "";
      req.on("data", (c) => (body += c));
      req.on("end", () => {
        try {
          const data = JSON.parse(body || "{}");
          const queries = Array.isArray(data.queries) ? data.queries : [data.query || ""];
          const result = store.search({ queries, limit: 5 });
          res.writeHead(200, { "Content-Type": "application/json" });
          res.end(JSON.stringify(result));
        } catch (e) {
          res.writeHead(400, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ error: e.message }));
        }
      });
      return;
    }

    res.writeHead(404);
    res.end("Not Found");
  });

  server.listen(port, "127.0.0.1", () => {
    console.log(`[horus-context-mode dashboard] standalone server listening at http://127.0.0.1:${port}`);
  });
}
