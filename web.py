import html
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs


def search_files(folder_path, keyword):
    found = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if keyword.lower() in file.lower():
                found.append(os.path.join(root, file))

    return found


PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>File Search Tool</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #0f172a;
      --panel: #111827;
      --card: #ffffff;
      --text: #111827;
      --muted: #6b7280;
      --accent: #2563eb;
      --accent-dark: #1d4ed8;
      --border: #d1d5db;
      --shadow: 0 20px 50px rgba(15, 23, 42, 0.18);
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      background:
        radial-gradient(circle at top left, rgba(37, 99, 235, 0.22), transparent 28%),
        radial-gradient(circle at top right, rgba(14, 165, 233, 0.16), transparent 24%),
        linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
      color: var(--text);
      min-height: 100vh;
      padding: 40px 18px;
    }

    .shell {
      max-width: 980px;
      margin: 0 auto;
      display: grid;
      gap: 18px;
    }

    .hero {
      background: linear-gradient(135deg, #0f172a, #1d4ed8);
      color: white;
      border-radius: 24px;
      padding: 28px;
      box-shadow: var(--shadow);
    }

    .hero h1 {
      margin: 0 0 8px;
      font-size: clamp(2rem, 4vw, 3.4rem);
      letter-spacing: -0.04em;
    }

    .hero p {
      margin: 0;
      max-width: 64ch;
      line-height: 1.6;
      color: rgba(255, 255, 255, 0.84);
    }

    .panel {
      background: rgba(255, 255, 255, 0.88);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.55);
      border-radius: 24px;
      padding: 22px;
      box-shadow: var(--shadow);
    }

    form {
      display: grid;
      gap: 14px;
      grid-template-columns: 1.4fr 1fr auto;
      align-items: end;
    }

    label {
      display: grid;
      gap: 8px;
      font-size: 0.95rem;
      font-weight: 700;
      color: var(--text);
    }

    input {
      width: 100%;
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 14px 16px;
      font-size: 1rem;
      outline: none;
      background: white;
    }

    input:focus {
      border-color: var(--accent);
      box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.14);
    }

    button {
      border: 0;
      border-radius: 14px;
      padding: 14px 20px;
      background: var(--accent);
      color: white;
      font-size: 1rem;
      font-weight: 700;
      cursor: pointer;
      transition: transform 120ms ease, background 120ms ease;
      white-space: nowrap;
    }

    button:hover {
      background: var(--accent-dark);
      transform: translateY(-1px);
    }

    .hint {
      margin-top: 12px;
      font-size: 0.95rem;
      color: var(--muted);
    }

    .results {
      display: grid;
      gap: 12px;
    }

    .summary {
      font-weight: 700;
      color: var(--text);
      margin-bottom: 6px;
    }

    .file {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 14px 16px;
      overflow-wrap: anywhere;
      box-shadow: 0 8px 20px rgba(15, 23, 42, 0.06);
    }

    .empty {
      background: #fff7ed;
      border: 1px solid #fdba74;
      color: #9a3412;
      border-radius: 16px;
      padding: 14px 16px;
    }

    .error {
      background: #fef2f2;
      border: 1px solid #fca5a5;
      color: #991b1b;
      border-radius: 16px;
      padding: 14px 16px;
    }

    @media (max-width: 820px) {
      form {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <main class="shell">
    <section class="hero">
      <h1>File Search Tool</h1>
      <p>Search a folder for files whose names contain your keyword. This page uses the same search logic as the command-line script, but runs in your browser.</p>
    </section>

    <section class="panel">
      <form method="post">
        <label>
          Folder path
          <input name="folder" placeholder="C:\\Users\\tejam\\Documents" value="__FOLDER_VALUE__">
        </label>
        <label>
          File name or keyword
          <input name="keyword" placeholder="report" value="__KEYWORD_VALUE__">
        </label>
        <button type="submit">Search</button>
      </form>
      <div class="hint">Tip: enter a full folder path on your machine. The search is case-insensitive and checks file names only.</div>
    </section>

    <section class="panel results">
      __BODY__
    </section>
  </main>
</body>
</html>"""


class RequestHandler(BaseHTTPRequestHandler):
    def _render(self, folder="", keyword="", body=""):
        page = (
        PAGE.replace("__FOLDER_VALUE__", html.escape(folder, quote=True))
        .replace("__KEYWORD_VALUE__", html.escape(keyword, quote=True))
        .replace("__BODY__", body)
        )
        encoded = page.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self):
        self._render(body='<div class="summary">Enter a folder path and keyword to start searching.</div>')

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length).decode("utf-8")
        fields = parse_qs(raw_body)
        folder = fields.get("folder", [""])[0].strip()
        keyword = fields.get("keyword", [""])[0].strip()

        if not folder or not keyword:
            self._render(
                folder=folder,
                keyword=keyword,
                body='<div class="error">Please enter both a folder path and a keyword.</div>',
            )
            return

        if not os.path.isdir(folder):
            self._render(
                folder=folder,
                keyword=keyword,
                body='<div class="error">That folder does not exist or is not accessible.</div>',
            )
            return

        results = search_files(folder, keyword)
        if results:
            items = ''.join(f'<div class="file">{html.escape(path)}</div>' for path in results)
            body = f'<div class="summary">Found {len(results)} matching file(s).</div>{items}'
        else:
            body = '<div class="empty">No matching files found.</div>'

        self._render(folder=folder, keyword=keyword, body=body)

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    host = "127.0.0.1"
    port = 8000
    server = ThreadingHTTPServer((host, port), RequestHandler)
    print(f"Serving on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping server...")
    finally:
        server.server_close()
