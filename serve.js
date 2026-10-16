const http = require('http');
const fs = require('fs');
const path = require('path');
const os = require('os');

const PORT = process.env.PORT || 8080;
const ROOT_DIR = __dirname;

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.webmanifest': 'application/manifest+json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon'
};

function getLocalIPs() {
  const interfaces = os.networkInterfaces();
  const addresses = [];
  for (const name of Object.keys(interfaces)) {
    for (const net of interfaces[name]) {
      if (net.family === 'IPv4' && !net.internal) {
        addresses.push({ iface: name, ip: net.address });
      }
    }
  }
  return addresses;
}

const server = http.createServer((req, res) => {
  let reqPath = decodeURI(req.url.split('?')[0]);
  if (reqPath === '/' || reqPath === '') {
    reqPath = '/index.html';
  }

  let filePath = path.join(ROOT_DIR, reqPath);

  // Security check: ensure path stays within ROOT_DIR
  if (!filePath.startsWith(ROOT_DIR)) {
    res.writeHead(403, { 'Content-Type': 'text/plain' });
    res.end('403 Forbidden');
    return;
  }

  fs.stat(filePath, (err, stats) => {
    if (err || !stats.isFile()) {
      res.writeHead(404, { 'Content-Type': 'text/plain' });
      res.end('404 Not Found');
      return;
    }

    const ext = path.extname(filePath).toLowerCase();
    const contentType = MIME_TYPES[ext] || 'application/octet-stream';

    // Allow cross-origin and local network caching headers
    res.writeHead(200, {
      'Content-Type': contentType,
      'Cache-Control': ext === '.html' ? 'no-cache' : 'public, max-age=3600',
      'Access-Control-Allow-Origin': '*'
    });

    const stream = fs.createReadStream(filePath);
    stream.pipe(res);
  });
});

server.listen(PORT, '0.0.0.0', () => {
  const ips = getLocalIPs();
  console.log('================================================================');
  console.log(' ECHO iPhone Standalone Testing Server Active');
  console.log('================================================================');
  console.log(` Local Machine URL : http://localhost:${PORT}`);
  
  if (ips.length > 0) {
    console.log(' iPhone Wi-Fi URLs :');
    ips.forEach(entry => {
      console.log(`   * http://${entry.ip}:${PORT}  (${entry.iface})`);
    });
  } else {
    console.log(' No external Wi-Fi interface detected.');
  }
  console.log('----------------------------------------------------------------');
  console.log(' Procedure to install ECHO on iPhone:');
  console.log('   1. Ensure your iPhone is connected to the same Wi-Fi network.');
  console.log('   2. Open Safari on your iPhone and type in the Wi-Fi URL above.');
  console.log('   3. Tap the Share icon (square with upward arrow) at the bottom.');
  console.log('   4. Select "Add to Home Screen" and tap "Add".');
  console.log('   5. Launch ECHO from your Home Screen in 100% standalone mode.');
  console.log('================================================================');
  console.log(' Press Ctrl+C in terminal to stop server.');
});
