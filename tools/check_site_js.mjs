import { readFileSync } from "node:fs";


if (process.argv.length < 3) {
  throw new Error("usage: node tools/check_site_js.mjs <html> [<html> ...]");
}

for (const path of process.argv.slice(2)) {
  const html = readFileSync(path, "utf8");
  const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)];
  if (scripts.length === 0) {
    throw new Error(`${path}: no inline JavaScript found`);
  }
  for (const [index, match] of scripts.entries()) {
    try {
      new Function(match[1]);
    } catch (error) {
      throw new Error(`${path}: inline script ${index + 1} does not parse`, {
        cause: error,
      });
    }
  }
  console.log(`${path}: ${scripts.length} inline script(s) parse`);
}
