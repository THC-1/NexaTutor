/** @type {import('next').NextConfig} */

const fs = require("fs");
const path = require("path");

function readJsonFile(filePath) {
  try {
    return JSON.parse(fs.readFileSync(filePath, "utf8"));
  } catch {
    return {};
  }
}

function firstNonEmpty(...values) {
  for (const value of values) {
    if (value !== undefined && value !== null && String(value).trim() !== "") {
      return String(value).trim();
    }
  }
  return "";
}

const SETTINGS_DIR = path.resolve(__dirname, "..", "data", "user", "settings");
const SYSTEM_SETTINGS = readJsonFile(path.join(SETTINGS_DIR, "system.json"));
const BACKEND_PORT = firstNonEmpty(
  process.env.BACKEND_PORT,
  SYSTEM_SETTINGS.backend_port,
  "8001",
);

// Use data/user/settings as the frontend source of truth. Environment values
// remain explicit deployment overrides for Docker/CI.
const NEXT_PUBLIC_API_BASE = firstNonEmpty(
  process.env.NEXT_PUBLIC_API_BASE,
  SYSTEM_SETTINGS.next_public_api_base,
  `http://localhost:${BACKEND_PORT}`,
);

process.env.NEXT_PUBLIC_API_BASE = NEXT_PUBLIC_API_BASE;

// Resolve the build-time application version from the single source of
// truth at ``deeptutor/__version__.py``. The Python file is parsed with a
// small regex so the JS build does not need to execute Python.
const APP_VERSION = (() => {
  try {
    const text = fs.readFileSync(
      path.resolve(__dirname, "..", "deeptutor", "__version__.py"),
      "utf8",
    );
    const match = text.match(/__version__\s*=\s*["']([^"']+)["']/);
    if (match) return match[1];
  } catch {}
  return "";
})();

const nextConfig = {
  // Keep the production build used by `deeptutor start` separate from the
  // `.next` development cache used by the explicit `deeptutor start --dev`.
  // Without separate directories either command can invalidate the other
  // process while it is running.
  distDir:
    process.env.NEXATUTOR_NEXT_DIST_DIR ||
    process.env.DEEPTUTOR_NEXT_DIST_DIR ||
    ".next",

  // Expose the build-time version to the browser so the sidebar badge
  // can compare it against GitHub's latest release.
  env: {
    NEXT_PUBLIC_APP_VERSION: APP_VERSION,
    NEXT_PUBLIC_API_BASE,
  },

  // Standalone output: self-contained server.js + minimal node_modules
  // This eliminates the need to copy the full node_modules into Docker production images
  output: "standalone",

  // web/proxy.ts (the Next.js middleware) forwards /api/* and /ws/* to the
  // backend by buffering and re-issuing the request. Next caps the buffered
  // request body at 10MB by default, but the backend accepts uploads up to
  // 200MB (DocumentValidator.MAX_FILE_SIZE). Raise the proxy cap to match (plus
  // multipart overhead headroom) so knowledge-base document uploads aren't
  // silently truncated when they pass through the proxy.
  experimental: {
    proxyClientMaxBodySize: 210 * 1024 * 1024,
  },

  // Move dev indicator to bottom-right corner
  devIndicators: {
    position: "bottom-right",
  },

  // Transpile mermaid and related packages for proper ESM handling
  transpilePackages: ["mermaid"],

  // Next.js 16 blocks cross-origin access to /_next/* dev resources (HMR
  // WebSocket, fonts, dev-only scripts) unless the request host is on this
  // allow-list. Without it, browsing http://127.0.0.1:<port>/ against a dev
  // server bound to localhost silently breaks client hydration — the SSR HTML
  // renders, but no React event handlers or effects ever attach.
  // Dev-only: `allowedDevOrigins` has no effect on `next build`/`next start`.
  allowedDevOrigins: ["127.0.0.1"],

  // Turbopack configuration (used when running `npm run dev:turbo`)
  turbopack: {
    resolveAlias: {
      // Fix for mermaid's cytoscape dependency - use CJS version
      cytoscape: "cytoscape/dist/cytoscape.cjs.js",
    },
  },

  // Webpack configuration (used for production builds - next build)
  webpack: (config) => {
    const path = require("path");
    config.resolve.alias = {
      ...config.resolve.alias,
      cytoscape: path.resolve(
        __dirname,
        "node_modules/cytoscape/dist/cytoscape.cjs.js",
      ),
    };
    return config;
  },
};

module.exports = nextConfig;
