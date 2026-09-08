/* ============================================================
 * DevBox · utils.js —— 纯逻辑层（无 DOM 依赖，可被 Node 测试）
 * 编解码 / 哈希 / 时间 / 进制 / 颜色 / Diff / 单位 / 文本 …
 * ============================================================ */
(function (global) {
  'use strict';

  /* ---------------- 通用 ---------------- */

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function debounce(fn, ms) {
    var t = null;
    return function () {
      var args = arguments, self = this;
      clearTimeout(t);
      t = setTimeout(function () { fn.apply(self, args); }, ms);
    };
  }

  /** DOM 构建器：h('div', {class:'x', onclick: fn}, 'text', child, ...) */
  function h(tag, attrs) {
    var node = document.createElement(tag);
    if (attrs) {
      Object.keys(attrs).forEach(function (k) {
        var v = attrs[k];
        if (v == null || v === false) return;
        if (k === 'class') node.className = v;
        else if (k === 'html') node.innerHTML = v;
        else if (k.slice(0, 2) === 'on' && typeof v === 'function') node.addEventListener(k.slice(2), v);
        else node.setAttribute(k, v === true ? '' : v);
      });
    }
    for (var i = 2; i < arguments.length; i++) appendChild(node, arguments[i]);
    return node;
  }
  function appendChild(node, c) {
    if (c == null || c === false) return;
    if (Array.isArray(c)) { c.forEach(function (x) { appendChild(node, x); }); return; }
    node.append(c.nodeType ? c : global.document.createTextNode(String(c)));
  }

  async function copyText(text) {
    try {
      if (global.navigator && global.navigator.clipboard && global.isSecureContext) {
        await global.navigator.clipboard.writeText(text);
        return true;
      }
    } catch (e) { /* 走降级 */ }
    if (!global.document) return false;
    var ta = global.document.createElement('textarea');
    ta.value = text;
    ta.style.cssText = 'position:fixed;opacity:0;top:0;left:0';
    global.document.body.appendChild(ta);
    ta.select();
    try { global.document.execCommand('copy'); return true; }
    catch (e) { return false; }
    finally { ta.remove(); }
  }

  function formatBytes(n) {
    if (!isFinite(n) || n < 0) return '-';
    if (n < 1024) return n + ' B';
    var units = ['KB', 'MB', 'GB', 'TB', 'PB'];
    var v = n, i = -1;
    do { v /= 1024; i++; } while (v >= 1024 && i < units.length - 1);
    return (Math.round(v * 100) / 100) + ' ' + units[i];
  }

  /* ---------------- 编码转换 ---------------- */

  var te = new TextEncoder();
  var td = new TextDecoder('utf-8');
  function utf8Encode(s) { return te.encode(s); }
  function utf8Decode(bytes) { return td.decode(bytes); }

  function bytesToBase64(bytes, urlSafe) {
    var bin = '', CH = 0x8000;
    for (var i = 0; i < bytes.length; i += CH) {
      bin += String.fromCharCode.apply(null, bytes.subarray(i, i + CH));
    }
    var b64 = global.btoa(bin);
    return urlSafe ? b64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '') : b64;
  }

  function base64ToBytes(b64) {
    var clean = String(b64).replace(/[\s=]/g, '').replace(/-/g, '+').replace(/_/g, '/');
    var pad = clean.length % 4 === 2 ? '==' : clean.length % 4 === 3 ? '=' : '';
    var bin = global.atob(clean + pad);
    var bytes = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
    return bytes;
  }

  function b64EncodeText(s, urlSafe) { return bytesToBase64(utf8Encode(s), urlSafe); }
  function b64DecodeText(s) { return utf8Decode(base64ToBytes(s)); }

  /** 输出数字转字符串，保留有效位、去掉多余 0 */
  function fmtNum(x) {
    if (!isFinite(x)) return String(x);
    if (x !== 0 && (Math.abs(x) >= 1e15 || Math.abs(x) < 1e-9)) return x.toExponential(6).replace(/\.?0+e/, 'e');
    return String(parseFloat(x.toPrecision(12)));
  }

  /* ---------------- 哈希 ---------------- */

  /** MD5（纯 JS 实现，返回 32 位小写 hex） */
  function md5(input) {
    var msg = typeof input === 'string' ? utf8Encode(input) : input;
    var len = msg.length;
    var total = (((len + 8) >> 6) + 1) << 6;
    var buf = new Uint8Array(total);
    buf.set(msg);
    buf[len] = 0x80;
    var dv = new DataView(buf.buffer);
    var bitLen = len * 8;
    dv.setUint32(total - 8, bitLen >>> 0, true);
    dv.setUint32(total - 4, Math.floor(bitLen / 0x100000000), true);

    var K = new Int32Array(64);
    for (var i = 0; i < 64; i++) K[i] = Math.floor(Math.abs(Math.sin(i + 1)) * 4294967296) | 0;
    var S = [7, 12, 17, 22, 5, 9, 14, 20, 4, 11, 16, 23, 6, 10, 15, 21];

    var a0 = 0x67452301, b0 = 0xefcdab89, c0 = 0x98badcfe, d0 = 0x10325476;
    var M = new Int32Array(16);
    for (var off = 0; off < total; off += 64) {
      for (var j = 0; j < 16; j++) M[j] = dv.getUint32(off + j * 4, true);
      var A = a0, B = b0, C = c0, D = d0;
      for (var k = 0; k < 64; k++) {
        var F, g, r = k >> 4;
        if (r === 0) { F = (B & C) | (~B & D); g = k; }
        else if (r === 1) { F = (D & B) | (~D & C); g = (5 * k + 1) % 16; }
        else if (r === 2) { F = B ^ C ^ D; g = (3 * k + 5) % 16; }
        else { F = C ^ (B | ~D); g = (7 * k) % 16; }
        F = (F + A + M[g] + K[k]) | 0;
        var s = S[(r << 2) | (k & 3)];
        A = D; D = C; C = B;
        B = (B + ((F << s) | (F >>> (32 - s)))) | 0;
      }
      a0 = (a0 + A) | 0; b0 = (b0 + B) | 0; c0 = (c0 + C) | 0; d0 = (d0 + D) | 0;
    }
    return [a0, b0, c0, d0].map(function (x) {
      var out = '';
      for (var i = 0; i < 4; i++) {
        out += ((x >>> (i * 8 + 4)) & 0xf).toString(16) + ((x >>> (i * 8)) & 0xf).toString(16);
      }
      return out;
    }).join('');
  }

  var CRC_TABLE = (function () {
    var t = new Int32Array(256);
    for (var n = 0; n < 256; n++) {
      var c = n;
      for (var k = 0; k < 8; k++) c = (c & 1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1);
      t[n] = c;
    }
    return t;
  })();

  /** CRC32，返回 8 位小写 hex */
  function crc32(input) {
    var b = typeof input === 'string' ? utf8Encode(input) : input;
    var c = -1;
    for (var i = 0; i < b.length; i++) c = CRC_TABLE[(c ^ b[i]) & 0xff] ^ (c >>> 8);
    return ((c ^ -1) >>> 0).toString(16).padStart(8, '0');
  }

  /** SHA 系列：algo ∈ SHA-1/256/384/512，input 为字符串或 ArrayBuffer */
  async function shaDigest(algo, input) {
    var data = typeof input === 'string' ? utf8Encode(input) : new Uint8Array(input);
    var buf = await global.crypto.subtle.digest(algo, data);
    return Array.from(new Uint8Array(buf)).map(function (b) { return b.toString(16).padStart(2, '0'); }).join('');
  }

  /* ---------------- 时间 ---------------- */

  /** 智能解析：10 位按秒、13 位按毫秒、其余按日期字符串 */
  function parseTimestamp(raw) {
    var s = String(raw == null ? '' : raw).trim();
    if (!s) return null;
    if (/^-?\d+$/.test(s)) {
      var n = Number(s);
      var ms = Math.abs(n) < 1e11 ? n * 1000 : n;
      var d0 = new Date(ms);
      return isNaN(d0.getTime()) ? null : d0;
    }
    var d = new Date(s);
    if (isNaN(d.getTime())) d = new Date(s.replace(/(\d)\s+(\d)/, '$1T$2'));
    return isNaN(d.getTime()) ? null : d;
  }

  function pad2(n) { return String(n).padStart(2, '0'); }

  function fmtDateTime(d) {
    return d.getFullYear() + '-' + pad2(d.getMonth() + 1) + '-' + pad2(d.getDate()) +
      ' ' + pad2(d.getHours()) + ':' + pad2(d.getMinutes()) + ':' + pad2(d.getSeconds());
  }
  function fmtDate(d) { return fmtDateTime(d).slice(0, 10); }
  var WEEK = ['日', '一', '二', '三', '四', '五', '六'];
  function fmtWeek(d) { return '星期' + WEEK[d.getDay()]; }

  function relativeTime(d) {
    var diff = Date.now() - d.getTime();
    var abs = Math.abs(diff);
    var units = [[31536000000, '年'], [2592000000, '个月'], [604800000, '周'],
                 [86400000, '天'], [3600000, '小时'], [60000, '分钟'], [1000, '秒']];
    for (var i = 0; i < units.length; i++) {
      if (abs >= units[i][0]) {
        var v = Math.round(abs / units[i][0]);
        return diff >= 0 ? v + units[i][1] + '前' : v + units[i][1] + '后';
      }
    }
    return '刚刚';
  }

  /* ---------------- UUID / 密码 ---------------- */

  function uuidV4() {
    if (global.crypto && global.crypto.randomUUID) return global.crypto.randomUUID();
    var b = global.crypto.getRandomValues(new Uint8Array(16));
    b[6] = (b[6] & 0x0f) | 0x40;
    b[8] = (b[8] & 0x3f) | 0x80;
    var hex = Array.from(b).map(function (x) { return x.toString(16).padStart(2, '0'); }).join('');
    return hex.slice(0, 8) + '-' + hex.slice(8, 12) + '-' + hex.slice(12, 16) + '-' + hex.slice(16, 20) + '-' + hex.slice(20);
  }

  function randPassword(opts) {
    var o = opts || {};
    var length = Math.max(4, Math.min(128, o.length || 16));
    var sets = [];
    if (o.lower) sets.push('abcdefghijklmnopqrstuvwxyz');
    if (o.upper) sets.push('ABCDEFGHIJKLMNOPQRSTUVWXYZ');
    if (o.digits) sets.push('0123456789');
    if (o.symbols) sets.push('!@#$%^&*()-_=+[]{}<>?/');
    if (!sets.length) throw new Error('请至少选择一种字符类型');
    var pool = sets.join('');
    if (o.avoidAmbiguous) {
      var amb = '0O1lI|`\'";:,.{}[]()<>';
      pool = pool.split('').filter(function (c) { return amb.indexOf(c) === -1; }).join('');
      sets = sets.map(function (s) {
        return s.split('').filter(function (c) { return amb.indexOf(c) === -1; }).join('');
      }).filter(Boolean);
      if (!pool) throw new Error('排除易混淆字符后字符池为空');
    }
    function rnd(n) { return global.crypto.getRandomValues(new Uint32Array(1))[0] % n; }
    var chars = [];
    sets.forEach(function (s) { chars.push(s[rnd(s.length)]); });
    while (chars.length < length) chars.push(pool[rnd(pool.length)]);
    for (var i = chars.length - 1; i > 0; i--) {
      var j = rnd(i + 1), t = chars[i]; chars[i] = chars[j]; chars[j] = t;
    }
    return chars.slice(0, length).join('');
  }

  function passwordEntropyBits(len, poolSize) {
    return Math.round(len * Math.log2(Math.max(2, poolSize)));
  }

  /* ---------------- 命名风格 ---------------- */

  /** 把任意标识符拆成小写单词数组 */
  function tokenizeName(s) {
    return String(s)
      .replace(/([a-z0-9])([A-Z])/g, '$1 $2')
      .replace(/([A-Z]+)([A-Z][a-z])/g, '$1 $2')
      .split(/[^A-Za-z0-9]+/)
      .filter(Boolean)
      .map(function (w) { return w.toLowerCase(); });
  }
  function cap(w) { return w.charAt(0).toUpperCase() + w.slice(1); }
  function toCamel(s)   { var w = tokenizeName(s); return w.map(function (x, i) { return i ? cap(x) : x; }).join(''); }
  function toPascal(s)  { return tokenizeName(s).map(cap).join(''); }
  function toSnake(s)   { return tokenizeName(s).join('_'); }
  function toKebab(s)   { return tokenizeName(s).join('-'); }
  function toConst(s)   { return tokenizeName(s).join('_').toUpperCase(); }

  /* ---------------- 文本统计 ---------------- */

  function textStats(s) {
    var cps = Array.from(s);
    var cjk = 0;
    for (var i = 0; i < cps.length; i++) {
      if (/[\u3400-\u4dbf\u4e00-\u9fff]/.test(cps[i])) cjk++;
    }
    var latinWords = (s.match(/[A-Za-z0-9][A-Za-z0-9'_-]*/g) || []).length;
    return {
      chars: cps.length,
      charsNoSpace: cps.filter(function (c) { return !/\s/.test(c); }).length,
      words: latinWords + cjk,
      cjk: cjk,
      lines: s.length ? s.split('\n').length : 0,
      bytes: utf8Encode(s).length
    };
  }

  /* ---------------- Diff（行级 LCS） ---------------- */

  function diffLines(aText, bText) {
    var a = aText === '' ? [] : String(aText).split('\n');
    var b = bText === '' ? [] : String(bText).split('\n');
    var n = a.length, m = b.length;
    if (n * m > 16000000) throw new Error('文本过长，请拆分后对比（上限约 4000×4000 行）');
    var dp = new Array(n + 1);
    for (var i = 0; i <= n; i++) dp[i] = new Uint16Array(m + 1);
    for (i = n - 1; i >= 0; i--) {
      for (var j = m - 1; j >= 0; j--) {
        dp[i][j] = a[i] === b[j] ? dp[i + 1][j + 1] + 1
                                 : Math.max(dp[i + 1][j], dp[i][j + 1]);
      }
    }
    var out = [];
    i = 0; j = 0;
    while (i < n && j < m) {
      if (a[i] === b[j]) { out.push({ type: 'same', text: a[i] }); i++; j++; }
      else if (dp[i + 1][j] >= dp[i][j + 1]) { out.push({ type: 'del', text: a[i] }); i++; }
      else { out.push({ type: 'add', text: b[j] }); j++; }
    }
    while (i < n) out.push({ type: 'del', text: a[i++] });
    while (j < m) out.push({ type: 'add', text: b[j++] });
    return out;
  }

  /* ---------------- JWT ---------------- */

  function jwtDecode(token) {
    var parts = String(token).trim().split('.');
    if (parts.length < 2 || parts.length > 3) throw new Error('JWT 应由 2~3 段组成（以 . 分隔）');
    function decodePart(p) {
      var b = p.replace(/-/g, '+').replace(/_/g, '/');
      return JSON.parse(utf8Decode(base64ToBytes(b)));
    }
    return {
      header: decodePart(parts[0]),
      payload: parts.length > 1 ? decodePart(parts[1]) : null,
      signature: parts.length > 2 ? parts[2] : null
    };
  }

  /* ---------------- 进制转换（BigInt 精确） ---------------- */

  var DIGITS = '0123456789abcdefghijklmnopqrstuvwxyz';

  /** 解析 base(2~36) 字符串为 BigInt；非法字符抛错 */
  function parseBigIntInBase(str, base) {
    var s = String(str).trim().toLowerCase().replace(/^0x/, '');
    var neg = s[0] === '-';
    if (neg || s[0] === '+') s = s.slice(1);
    if (!s) throw new Error('请输入数字');
    if (base < 2 || base > 36) throw new Error('进制须在 2~36 之间');
    var valid = DIGITS.slice(0, base);
    var n = 0n, B = BigInt(base);
    for (var i = 0; i < s.length; i++) {
      var idx = valid.indexOf(s[i]);
      if (idx === -1) throw new Error('字符 "' + s[i] + '" 不是合法的 ' + base + ' 进制数字');
      n = n * B + BigInt(idx);
    }
    return neg ? -n : n;
  }

  function bigIntToBase(n, base) {
    if (base < 2 || base > 36) throw new Error('进制须在 2~36 之间');
    if (n < 0n) return '-' + (-n).toString(base);
    return n.toString(base);
  }

  /* ---------------- 颜色 ---------------- */

  function clamp(n, min, max) { return Math.min(max, Math.max(min, n)); }

  function hexToRgb(hex) {
    var s = String(hex).trim().replace(/^#/, '');
    if (/^[0-9a-f]{3}$/i.test(s) || /^[0-9a-f]{4}$/i.test(s)) {
      s = s.split('').map(function (c) { return c + c; }).join('');
    }
    if (!/^[0-9a-f]{6}([0-9a-f]{2})?$/i.test(s)) return null;
    return {
      r: parseInt(s.slice(0, 2), 16),
      g: parseInt(s.slice(2, 4), 16),
      b: parseInt(s.slice(4, 6), 16),
      a: s.length === 8 ? parseInt(s.slice(6, 8), 16) / 255 : 1
    };
  }

  function rgbToHex(rgb) {
    function hh(n) { return Math.round(clamp(n, 0, 255)).toString(16).padStart(2, '0'); }
    var a = rgb.a == null ? 1 : rgb.a;
    return '#' + hh(rgb.r) + hh(rgb.g) + hh(rgb.b) + (a < 1 ? hh(a * 255) : '');
  }

  function rgbToHsl(rgb) {
    var r = rgb.r / 255, g = rgb.g / 255, b = rgb.b / 255;
    var max = Math.max(r, g, b), min = Math.min(r, g, b);
    var l = (max + min) / 2, h = 0, s = 0;
    if (max !== min) {
      var d = max - min;
      s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
      switch (max) {
        case r: h = (g - b) / d + (g < b ? 6 : 0); break;
        case g: h = (b - r) / d + 2; break;
        default: h = (r - g) / d + 4;
      }
      h /= 6;
    }
    /* 返回未取整的精确值（0-360 / 0-100 / 0-100），由调用方按需取整 */
    return { h: h * 360, s: s * 100, l: l * 100 };
  }

  function hslToRgb(hsl) {
    var h = (((hsl.h % 360) + 360) % 360) / 360;
    var s = clamp(hsl.s, 0, 100) / 100;
    var l = clamp(hsl.l, 0, 100) / 100;
    if (s === 0) { var v = Math.round(l * 255); return { r: v, g: v, b: v }; }
    var q = l < 0.5 ? l * (1 + s) : l + s - l * s;
    var p = 2 * l - q;
    function f(t) {
      t = ((t % 1) + 1) % 1;
      if (t < 1 / 6) return p + (q - p) * 6 * t;
      if (t < 1 / 2) return q;
      if (t < 2 / 3) return p + (q - p) * (2 / 3 - t) * 6;
      return p;
    }
    return {
      r: Math.round(f(h + 1 / 3) * 255),
      g: Math.round(f(h) * 255),
      b: Math.round(f(h - 1 / 3) * 255)
    };
  }

  /** 解析 #hex / rgb() / rgba() / hsl() 字符串，失败返回 null */
  function parseColor(str) {
    var s = String(str || '').trim();
    if (!s) return null;
    if (s[0] === '#') return hexToRgb(s);
    var m = s.match(/^rgba?\(\s*([\d.]+)[\s,]+([\d.]+)[\s,]+([\d.]+)\s*(?:[,/]\s*([\d.]+%?))?\s*\)$/i);
    if (m) {
      return {
        r: +m[1], g: +m[2], b: +m[3],
        a: m[4] == null ? 1 : (m[4].endsWith('%') ? parseFloat(m[4]) / 100 : +m[4])
      };
    }
    m = s.match(/^hsla?\(\s*([\d.]+)(?:deg)?[\s,]+([\d.]+)%[\s,]+([\d.]+)%\s*(?:[,/]\s*([\d.]+%?))?\s*\)$/i);
    if (m) {
      var rgb = hslToRgb({ h: +m[1], s: +m[2], l: +m[3] });
      rgb.a = m[4] == null ? 1 : (m[4].endsWith('%') ? parseFloat(m[4]) / 100 : +m[4]);
      return rgb;
    }
    return null;
  }

  function luminance(rgb) {
    function f(c) {
      c /= 255;
      return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    }
    return 0.2126 * f(rgb.r) + 0.7152 * f(rgb.g) + 0.0722 * f(rgb.b);
  }

  function contrastRatio(c1, c2) {
    var l1 = luminance(c1), l2 = luminance(c2);
    return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
  }

  /* ---------------- 单位换算 ---------------- */

  var UNIT_GROUPS = [
    { id: 'length', name: '长度', units: [
      { id: 'mm', name: '毫米 mm', f: 0.001 }, { id: 'cm', name: '厘米 cm', f: 0.01 },
      { id: 'm', name: '米 m', f: 1 }, { id: 'km', name: '千米 km', f: 1000 },
      { id: 'in', name: '英寸 in', f: 0.0254 }, { id: 'ft', name: '英尺 ft', f: 0.3048 },
      { id: 'mi', name: '英里 mi', f: 1609.344 }, { id: 'nmi', name: '海里 nmi', f: 1852 }
    ]},
    { id: 'weight', name: '重量', units: [
      { id: 'mg', name: '毫克 mg', f: 1e-6 }, { id: 'g', name: '克 g', f: 0.001 },
      { id: 'kg', name: '千克 kg', f: 1 }, { id: 't', name: '吨 t', f: 1000 },
      { id: 'jin', name: '斤', f: 0.5 }, { id: 'oz', name: '盎司 oz', f: 0.028349523125 },
      { id: 'lb', name: '磅 lb', f: 0.45359237 }
    ]},
    { id: 'temp', name: '温度', special: 'temp', units: [
      { id: 'C', name: '摄氏度 °C' }, { id: 'F', name: '华氏度 °F' }, { id: 'K', name: '开尔文 K' }
    ]},
    { id: 'data', name: '数据存储', units: [
      { id: 'bit', name: '比特 bit', f: 0.125 }, { id: 'B', name: '字节 B', f: 1 },
      { id: 'KB', name: '千字节 KB (10³)', f: 1e3 }, { id: 'MB', name: 'MB (10⁶)', f: 1e6 },
      { id: 'GB', name: 'GB (10⁹)', f: 1e9 }, { id: 'TB', name: 'TB (10¹²)', f: 1e12 },
      { id: 'KiB', name: 'KiB (2¹⁰)', f: 1024 }, { id: 'MiB', name: 'MiB (2²⁰)', f: 1048576 },
      { id: 'GiB', name: 'GiB (2³⁰)', f: 1073741824 }, { id: 'TiB', name: 'TiB (2⁴⁰)', f: 1099511627776 }
    ]},
    { id: 'area', name: '面积', units: [
      { id: 'm2', name: '平方米 m²', f: 1 }, { id: 'km2', name: '平方千米 km²', f: 1e6 },
      { id: 'ha', name: '公顷 ha', f: 1e4 }, { id: 'mu', name: '亩', f: 2000 / 3 },
      { id: 'ft2', name: '平方英尺 ft²', f: 0.09290304 }
    ]},
    { id: 'speed', name: '速度', units: [
      { id: 'mps', name: '米/秒 m/s', f: 1 }, { id: 'kmh', name: '千米/时 km/h', f: 1 / 3.6 },
      { id: 'mph', name: '英里/时 mph', f: 0.44704 }, { id: 'knot', name: '节 kn', f: 0.514444 }
    ]},
    { id: 'time', name: '时间', units: [
      { id: 'ms', name: '毫秒 ms', f: 0.001 }, { id: 's', name: '秒 s', f: 1 },
      { id: 'min', name: '分钟 min', f: 60 }, { id: 'h', name: '小时 h', f: 3600 },
      { id: 'd', name: '天 d', f: 86400 }, { id: 'w', name: '周 week', f: 604800 }
    ]}
  ];

  function toCelsius(v, unit) {
    if (unit === 'F') return (v - 32) * 5 / 9;
    if (unit === 'K') return v - 273.15;
    return v;
  }
  function fromCelsius(v, unit) {
    if (unit === 'F') return v * 9 / 5 + 32;
    if (unit === 'K') return v + 273.15;
    return v;
  }

  function convertUnit(value, fromId, toId, group) {
    if (group.special === 'temp') return fromCelsius(toCelsius(value, fromId), toId);
    var from = group.units.find(function (u) { return u.id === fromId; });
    var to = group.units.find(function (u) { return u.id === toId; });
    if (!from || !to) throw new Error('未知单位');
    return value * from.f / to.f;
  }

  /* ---------------- 导出 ---------------- */

  global.DevUtil = {
    escapeHtml: escapeHtml,
    debounce: debounce,
    h: h,
    copyText: copyText,
    formatBytes: formatBytes,
    fmtNum: fmtNum,
    utf8Encode: utf8Encode,
    utf8Decode: utf8Decode,
    bytesToBase64: bytesToBase64,
    base64ToBytes: base64ToBytes,
    b64EncodeText: b64EncodeText,
    b64DecodeText: b64DecodeText,
    md5: md5,
    crc32: crc32,
    shaDigest: shaDigest,
    parseTimestamp: parseTimestamp,
    fmtDateTime: fmtDateTime,
    fmtDate: fmtDate,
    fmtWeek: fmtWeek,
    relativeTime: relativeTime,
    pad2: pad2,
    uuidV4: uuidV4,
    randPassword: randPassword,
    passwordEntropyBits: passwordEntropyBits,
    tokenizeName: tokenizeName,
    toCamel: toCamel, toPascal: toPascal, toSnake: toSnake, toKebab: toKebab, toConst: toConst,
    textStats: textStats,
    diffLines: diffLines,
    jwtDecode: jwtDecode,
    parseBigIntInBase: parseBigIntInBase,
    bigIntToBase: bigIntToBase,
    clamp: clamp,
    hexToRgb: hexToRgb,
    rgbToHex: rgbToHex,
    rgbToHsl: rgbToHsl,
    hslToRgb: hslToRgb,
    parseColor: parseColor,
    luminance: luminance,
    contrastRatio: contrastRatio,
    UNIT_GROUPS: UNIT_GROUPS,
    convertUnit: convertUnit
  };
})(globalThis);
