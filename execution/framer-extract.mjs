#!/usr/bin/env node

import crypto from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";

const args = process.argv.slice(2);

if (args.length === 0 || args.includes("--help") || args.includes("-h")) {
  console.log(
    [
      "Usage: node scripts/framer-extract.mjs <url> [outputDir] [--max-pages N]",
      "",
      "Example:",
      "  node scripts/framer-extract.mjs https://example.com ./extracted-site --max-pages 60",
    ].join("\n"),
  );
  process.exit(0);
}

const startUrlInput = args[0];
const outputDir = path.resolve(args[1] ?? "framer-export");
const maxPagesIndex = args.indexOf("--max-pages");
const maxPages =
  maxPagesIndex >= 0 && args[maxPagesIndex + 1]
    ? Number(args[maxPagesIndex + 1])
    : 40;

if (!Number.isFinite(maxPages) || maxPages <= 0) {
  console.error("`--max-pages` must be a positive number.");
  process.exit(1);
}

let startUrl;
try {
  startUrl = new URL(startUrlInput);
} catch {
  console.error(`Invalid URL: ${startUrlInput}`);
  process.exit(1);
}

const pageQueue = [normalizePageUrl(startUrl)];
const visitedPages = new Set();
const savedAssets = new Map();
const inFlightAssets = new Map();

await fs.mkdir(outputDir, { recursive: true });

for (let i = 0; i < pageQueue.length && visitedPages.size < maxPages; i += 1) {
  const pageUrl = pageQueue[i];
  if (visitedPages.has(pageUrl)) continue;

  visitedPages.add(pageUrl);
  process.stdout.write(`- Crawling page: ${pageUrl}\n`);

  try {
    await processPage({
      pageUrl,
      startOrigin: startUrl.origin,
      outputDir,
      pageQueue,
      visitedPages,
      savedAssets,
      inFlightAssets,
    });
  } catch (error) {
    process.stdout.write(
      `  ! Failed page ${pageUrl}: ${error instanceof Error ? error.message : String(error)}\n`,
    );
  }
}

process.stdout.write("\nDone.\n");
process.stdout.write(`Pages saved: ${visitedPages.size}\n`);
process.stdout.write(`Assets saved: ${savedAssets.size}\n`);
process.stdout.write(`Output: ${outputDir}\n`);

async function processPage({
  pageUrl,
  startOrigin,
  outputDir,
  pageQueue,
  visitedPages,
  savedAssets,
  inFlightAssets,
}) {
  const res = await fetchWithRetry(pageUrl, {
    headers: { "user-agent": "framer-extract/1.0" },
  });
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}`);
  }

  const contentType = res.headers.get("content-type") || "";
  if (!contentType.includes("text/html")) {
    throw new Error(`Expected HTML, got ${contentType}`);
  }

  let html = await res.text();
  const pageFile = getLocalPagePath(pageUrl);
  const pageAbsFile = path.join(outputDir, pageFile);

  html = await rewriteHtmlReferences({
    html,
    pageUrl,
    pageFile,
    startOrigin,
    outputDir,
    pageQueue,
    visitedPages,
    savedAssets,
    inFlightAssets,
  });

  await writeFileSafe(pageAbsFile, html);
}

async function rewriteHtmlReferences({
  html,
  pageUrl,
  pageFile,
  startOrigin,
  outputDir,
  pageQueue,
  visitedPages,
  savedAssets,
  inFlightAssets,
}) {
  html = await replaceAsync(
    html,
    /\b(src|href|poster)=(["'])(.*?)\2/gi,
    async (full, attr, quote, rawValue) => {
      const rewritten = await rewriteReference({
        rawValue,
        attr: attr.toLowerCase(),
        pageUrl,
        pageFile,
        startOrigin,
        outputDir,
        pageQueue,
        visitedPages,
        savedAssets,
        inFlightAssets,
      });
      return `${attr}=${quote}${rewritten}${quote}`;
    },
  );

  html = await replaceAsync(html, /\bsrcset=(["'])(.*?)\1/gi, async (full, quote, raw) => {
    const parts = raw
      .split(",")
      .map((chunk) => chunk.trim())
      .filter(Boolean);

    const rewrittenParts = [];
    for (const part of parts) {
      const [urlPart, descriptor] = part.split(/\s+/, 2);
      const rewrittenUrl = await rewriteReference({
        rawValue: urlPart,
        attr: "srcset",
        pageUrl,
        pageFile,
        startOrigin,
        outputDir,
        pageQueue,
        visitedPages,
        savedAssets,
        inFlightAssets,
      });
      rewrittenParts.push(descriptor ? `${rewrittenUrl} ${descriptor}` : rewrittenUrl);
    }

    return `srcset=${quote}${rewrittenParts.join(", ")}${quote}`;
  });

  html = await replaceAsync(html, /url\(([^)]+)\)/gi, async (full, inside) => {
    const raw = stripQuotes(inside.trim());
    const rewritten = await rewriteReference({
      rawValue: raw,
      attr: "css-url",
      pageUrl,
      pageFile,
      startOrigin,
      outputDir,
      pageQueue,
      visitedPages,
      savedAssets,
      inFlightAssets,
    });
    return `url("${rewritten}")`;
  });

  return html;
}

async function rewriteReference({
  rawValue,
  attr,
  pageUrl,
  pageFile,
  startOrigin,
  outputDir,
  pageQueue,
  visitedPages,
  savedAssets,
  inFlightAssets,
}) {
  const normalizedRawValue = decodeHtmlEntities(rawValue).trim();
  if (!normalizedRawValue || isSkippableValue(normalizedRawValue)) return rawValue;

  const absUrl = toAbsoluteUrl(normalizedRawValue, pageUrl);
  if (!absUrl) return rawValue;

  if (isPageReference(absUrl, attr, startOrigin)) {
    const normalized = normalizePageUrl(absUrl.href);
    if (!visitedPages.has(normalized) && !pageQueue.includes(normalized)) {
      pageQueue.push(normalized);
    }
    const targetFile = getLocalPagePath(absUrl.href);
    return relativeFilePath(pageFile, targetFile) + (absUrl.hash || "");
  }

  if (!isAssetReference(absUrl, attr)) return rawValue;

  const targetAsset = await saveAsset(absUrl.href, outputDir, savedAssets, inFlightAssets);
  return relativeFilePath(pageFile, targetAsset) + (absUrl.hash || "");
}

async function saveAsset(assetUrl, outputDir, savedAssets, inFlightAssets) {
  const key = normalizeAssetUrl(assetUrl);
  if (savedAssets.has(key)) return savedAssets.get(key);
  if (inFlightAssets.has(key)) return inFlightAssets.get(key);

  const job = (async () => {
    const res = await fetchWithRetry(assetUrl, {
      headers: { "user-agent": "framer-extract/1.0" },
    });
    if (!res.ok) {
      throw new Error(`Asset download failed (${res.status}) ${assetUrl}`);
    }

    const contentType = res.headers.get("content-type") || "";
    const isTextLike = /text\/|application\/(javascript|json|xml)/i.test(contentType);
    const localPath = getLocalAssetPath(assetUrl, contentType);
    const isJavaScriptLike =
      /javascript|ecmascript|module/i.test(contentType) ||
      localPath.endsWith(".mjs") ||
      localPath.endsWith(".js");
    const absFile = path.join(outputDir, localPath);
    const buffer = Buffer.from(await res.arrayBuffer());

    if (isTextLike) {
      let text = buffer.toString("utf8");
      if (contentType.includes("text/css") || localPath.endsWith(".css")) {
        text = await rewriteCssUrls(
          text,
          assetUrl,
          localPath,
          outputDir,
          savedAssets,
          inFlightAssets,
        );
      }
      await writeFileSafe(absFile, text);

      // Framer pages import many route chunks dynamically from .mjs files.
      // Crawl module dependencies so interactions/hydration can run offline.
      if (isJavaScriptLike) {
        await crawlJavaScriptDependencies(text, assetUrl, outputDir, savedAssets, inFlightAssets);
      }
    } else {
      await writeBinarySafe(absFile, buffer);
    }

    savedAssets.set(key, localPath);
    process.stdout.write(`  + Asset: ${assetUrl}\n`);
    return localPath;
  })();

  inFlightAssets.set(key, job);
  try {
    return await job;
  } finally {
    inFlightAssets.delete(key);
  }
}

async function rewriteCssUrls(cssText, cssUrl, cssLocalPath, outputDir, savedAssets, inFlightAssets) {
  return replaceAsync(cssText, /url\(([^)]+)\)/gi, async (full, inside) => {
    const raw = stripQuotes(inside.trim());
    if (isSkippableValue(raw)) return full;
    const abs = toAbsoluteUrl(raw, cssUrl);
    if (!abs || abs.origin !== new URL(cssUrl).origin) return full;

    const target = await saveAsset(abs.href, outputDir, savedAssets, inFlightAssets);
    const rel = relativeFilePath(cssLocalPath, target);
    return `url("${rel}")`;
  });
}

async function crawlJavaScriptDependencies(
  jsText,
  jsUrl,
  outputDir,
  savedAssets,
  inFlightAssets,
) {
  const specs = extractJavaScriptModuleSpecifiers(jsText);
  if (specs.length === 0) return;

  await Promise.all(
    specs.map(async (specifier) => {
      const abs = toAbsoluteUrl(specifier, jsUrl);
      if (!abs) return;
      if (!["http:", "https:"].includes(abs.protocol)) return;

      try {
        await saveAsset(abs.href, outputDir, savedAssets, inFlightAssets);
      } catch {
        // Some optional chunks may not exist in a given publish. Ignore hard-fail.
      }
    }),
  );
}

function extractJavaScriptModuleSpecifiers(jsText) {
  const results = new Set();

  const staticImportRegex =
    /\b(?:import|export)\s+[^"'`]*?\bfrom\s*["'`]([^"'`]+)["'`]/g;
  const dynamicImportRegex = /\bimport\s*\(\s*["'`]([^"'`]+)["'`]\s*\)/g;

  for (const match of jsText.matchAll(staticImportRegex)) {
    const spec = match[1];
    if (isModuleSpecifierCandidate(spec)) results.add(spec);
  }

  for (const match of jsText.matchAll(dynamicImportRegex)) {
    const spec = match[1];
    if (isModuleSpecifierCandidate(spec)) results.add(spec);
  }

  return [...results];
}

function isModuleSpecifierCandidate(specifier) {
  if (!specifier) return false;
  if (specifier.startsWith("data:")) return false;
  if (specifier.startsWith("node:")) return false;
  if (specifier.startsWith("/")) return true;
  if (specifier.startsWith("./")) return true;
  if (specifier.startsWith("../")) return true;
  return /^https?:\/\//i.test(specifier);
}

function getLocalPagePath(input) {
  const url = new URL(input);
  let pathname = safeDecode(url.pathname);
  if (!pathname || pathname === "/") return "index.html";
  if (pathname.endsWith("/")) pathname += "index";
  if (!path.extname(pathname)) pathname += "/index";
  let output = pathname.replace(/^\/+/, "");
  if (!output.endsWith(".html")) output += ".html";
  if (url.search) output = appendQueryHash(output, url.search);
  return output;
}

function getLocalAssetPath(input, contentType = "") {
  const url = new URL(input);
  let pathname = safeDecode(url.pathname).replace(/^\/+/, "");
  if (!pathname) pathname = "__root";
  if (pathname.endsWith("/")) pathname += "index";
  if (!path.extname(pathname)) {
    if (contentType.includes("text/css")) pathname += ".css";
    else if (/javascript|ecmascript|module/i.test(contentType)) pathname += ".js";
    else if (contentType.includes("application/json")) pathname += ".json";
    else if (contentType.includes("text/html")) pathname += ".html";
    else if (contentType.startsWith("text/")) pathname += ".txt";
    else pathname += ".bin";
  }
  const withHost = path.posix.join("__assets", url.host, pathname);
  return url.search ? appendQueryHash(withHost, url.search) : withHost;
}

function appendQueryHash(filePath, search) {
  const ext = path.posix.extname(filePath);
  const base = ext ? filePath.slice(0, -ext.length) : filePath;
  const hash = crypto.createHash("sha1").update(search).digest("hex").slice(0, 8);
  return `${base}__q${hash}${ext}`;
}

function normalizePageUrl(input) {
  const url = new URL(input);
  url.hash = "";
  if (!url.pathname) url.pathname = "/";
  return url.href;
}

function normalizeAssetUrl(input) {
  const url = new URL(input);
  url.hash = "";
  return url.href;
}

function toAbsoluteUrl(raw, base) {
  try {
    return new URL(raw, base);
  } catch {
    return null;
  }
}

function isPageReference(url, attr, startOrigin) {
  if (attr !== "href") return false;
  if (url.origin !== startOrigin) return false;
  const ext = path.posix.extname(url.pathname).toLowerCase();
  if (!ext) return true;
  return ext === ".html" || ext === ".htm";
}

function isAssetReference(url, attr) {
  if (!["http:", "https:"].includes(url.protocol)) return false;

  if (attr === "src" || attr === "poster" || attr === "srcset" || attr === "css-url") {
    return true;
  }

  if (attr !== "href") return false;

  const assetExtensions = new Set([
    ".css",
    ".js",
    ".mjs",
    ".json",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".svg",
    ".ico",
    ".avif",
    ".woff",
    ".woff2",
    ".ttf",
    ".otf",
    ".eot",
    ".mp4",
    ".webm",
    ".mp3",
    ".wav",
    ".pdf",
    ".txt",
    ".xml",
    ".map",
  ]);

  const ext = path.posix.extname(url.pathname).toLowerCase();
  return Boolean(ext && assetExtensions.has(ext));
}

function isSkippableValue(value) {
  const lower = value.toLowerCase();
  return (
    lower.startsWith("#") ||
    lower.startsWith("data:") ||
    lower.startsWith("mailto:") ||
    lower.startsWith("tel:") ||
    lower.startsWith("javascript:") ||
    lower.startsWith("blob:")
  );
}

function relativeFilePath(fromFile, toFile) {
  const fromDir = path.posix.dirname(fromFile.replace(/\\/g, "/"));
  let rel = path.posix.relative(fromDir, toFile.replace(/\\/g, "/"));
  if (!rel || rel === "") rel = ".";
  return rel;
}

async function writeFileSafe(filePath, content) {
  await fs.mkdir(path.dirname(filePath), { recursive: true });
  await fs.writeFile(filePath, content, "utf8");
}

async function writeBinarySafe(filePath, buffer) {
  await fs.mkdir(path.dirname(filePath), { recursive: true });
  await fs.writeFile(filePath, buffer);
}

function stripQuotes(value) {
  return value.replace(/^['"]|['"]$/g, "");
}

function decodeHtmlEntities(value) {
  return value
    .replaceAll("&amp;", "&")
    .replaceAll("&quot;", '"')
    .replaceAll("&#39;", "'")
    .replaceAll("&lt;", "<")
    .replaceAll("&gt;", ">");
}

function safeDecode(input) {
  try {
    return decodeURIComponent(input);
  } catch {
    return input;
  }
}

async function replaceAsync(input, regex, replacer) {
  const matches = [...input.matchAll(regex)];
  if (matches.length === 0) return input;

  const replacements = await Promise.all(matches.map((match) => replacer(...match)));
  let output = input;
  for (let i = matches.length - 1; i >= 0; i -= 1) {
    const match = matches[i];
    const replacement = replacements[i];
    output = `${output.slice(0, match.index)}${replacement}${output.slice(match.index + match[0].length)}`;
  }
  return output;
}

async function fetchWithRetry(url, options, maxAttempts = 3) {
  let lastError;

  for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
    try {
      const res = await fetch(url, options);
      if (res.ok) return res;

      // Retry only for transient server-side statuses.
      if (attempt < maxAttempts && [408, 429, 500, 502, 503, 504].includes(res.status)) {
        await sleep(200 * attempt);
        continue;
      }
      return res;
    } catch (error) {
      lastError = error;
      if (attempt < maxAttempts) {
        await sleep(200 * attempt);
        continue;
      }
    }
  }

  throw lastError ?? new Error(`Fetch failed for ${url}`);
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
