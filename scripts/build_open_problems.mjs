import { readFile, writeFile } from "node:fs/promises";
import { marked } from "marked";

const source = await readFile(new URL("../open-problems.md", import.meta.url), "utf8");
const content = marked.parse(source);
const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Open Problems - My EA Blog</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&amp;family=Lora:ital,wght@0,400;0,600;0,700;1,400&amp;display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/style.css">
  <script defer src="/analytics.js"></script>
  <script defer src="/_vercel/insights/script.js"></script>
</head>
<body>
  <nav class="site-nav">
    <a href="/">home</a>
    <a href="/open-problems" class="active">open problems</a>
    <a href="/chat-in-spanish">chat in spanish</a>
    <a href="/live-with-me">live with me</a>
  </nav>

  <main class="prose open-problems">
${content.trim().split("\n").map((line) => `    ${line}`).join("\n")}
  </main>
</body>
</html>
`;

await writeFile(new URL("../public/open-problems.html", import.meta.url), html);
