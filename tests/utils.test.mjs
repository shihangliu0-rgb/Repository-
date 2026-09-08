/**
 * DevBox 纯逻辑层自动化测试
 * 运行：npm test  （或 node --test tests/）
 * 说明：MD5/CRC32/SHA 直接与 Node 内置 crypto/zlib 对拍，确保算法正确性。
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import zlib from 'node:zlib';

await import('../assets/js/utils.js');
const U = globalThis.DevUtil;

/* ---------------- 基础工具 ---------------- */

test('escapeHtml 转义', () => {
  assert.equal(U.escapeHtml('<a href="x">&\'</a>'), '&lt;a href=&quot;x&quot;&gt;&amp;&#39;&lt;/a&gt;');
});

test('formatBytes', () => {
  assert.equal(U.formatBytes(0), '0 B');
  assert.equal(U.formatBytes(1023), '1023 B');
  assert.equal(U.formatBytes(1024), '1 KB');
  assert.equal(U.formatBytes(1536), '1.5 KB');
  assert.equal(U.formatBytes(1048576), '1 MB');
});

/* ---------------- 编码 ---------------- */

test('Base64 与 Node Buffer 对拍（含中文/emoji/二进制）', () => {
  const cases = ['', 'hello', '你好，世界！', '🚀emoji✨', 'a'.repeat(1000), ' padded  \n text '];
  for (const s of cases) {
    const expected = Buffer.from(s, 'utf8').toString('base64');
    assert.equal(U.b64EncodeText(s), expected, 'encode: ' + JSON.stringify(s));
    assert.equal(U.b64DecodeText(expected), s, 'decode: ' + JSON.stringify(s));
  }
  // 二进制字节
  const bytes = crypto.randomBytes(512);
  assert.equal(Buffer.from(U.bytesToBase64(bytes), 'base64').toString('hex'), bytes.toString('hex'));
});

test('Base64 URL-Safe', () => {
  const s = 'subjects?_ill';
  const urlSafe = U.b64EncodeText(s, true);
  assert.ok(!/[+/=]/.test(urlSafe));
  const std = Buffer.from(s, 'utf8').toString('base64url');
  assert.equal(urlSafe, std);
  assert.equal(U.b64DecodeText(urlSafe), s);
});

test('Base64 解码容忍缺失 padding', () => {
  const full = Buffer.from('abc', 'utf8').toString('base64'); // YWJj
  const noPad = full.replace(/=+$/, '');
  assert.equal(U.b64DecodeText(noPad), 'abc');
});

/* ---------------- 哈希 ---------------- */

test('MD5 与 Node crypto 对拍（各种长度边界 + 二进制）', () => {
  const cases = [
    '', 'a', 'abc', 'message digest', '你好世界', 'The quick brown fox jumps over the lazy dog',
    ...[31, 55, 56, 57, 63, 64, 65, 119, 120, 127, 128, 500].map(n => 'x'.repeat(n)),
  ];
  for (const s of cases) {
    const expected = crypto.createHash('md5').update(s, 'utf8').digest('hex');
    assert.equal(U.md5(s), expected, 'len=' + s.length);
  }
  const bin = crypto.randomBytes(333);
  assert.equal(
    U.md5(new Uint8Array(bin)),
    crypto.createHash('md5').update(bin).digest('hex')
  );
});

test('CRC32 与 Node zlib 对拍', () => {
  assert.equal(U.crc32('123456789'), 'cbf43926');
  assert.equal(U.crc32(''), '00000000');
  for (let i = 0; i < 5; i++) {
    const bin = crypto.randomBytes(64 + i * 97);
    assert.equal(U.crc32(new Uint8Array(bin)), zlib.crc32(bin).toString(16).padStart(8, '0'));
  }
});

test('SHA 系列 与 Node crypto 对拍', async () => {
  for (const algo of ['SHA-1', 'SHA-256', 'SHA-384', 'SHA-512']) {
    const expected = crypto.createHash(algo.toLowerCase().replace('-', '')).update('你好 hello', 'utf8').digest('hex');
    assert.equal(await U.shaDigest(algo, '你好 hello'), expected, algo);
  }
});

/* ---------------- 时间 ---------------- */

test('parseTimestamp 秒/毫秒/日期字符串', () => {
  assert.equal(U.parseTimestamp('1700000000').getTime(), 1700000000 * 1000);
  assert.equal(U.parseTimestamp('1700000000000').getTime(), 1700000000000);
  assert.equal(U.parseTimestamp('2026-01-01T08:00:00').getTime(), new Date(2026, 0, 1, 8, 0, 0).getTime());
  assert.equal(U.parseTimestamp('垃圾'), null);
  assert.equal(U.parseTimestamp(''), null);
});

test('fmtDateTime / fmtWeek', () => {
  const d = new Date(2026, 0, 3, 9, 5, 7); // 2026-01-03 周六
  assert.equal(U.fmtDateTime(d), '2026-01-03 09:05:07');
  assert.equal(U.fmtWeek(d), '星期六');
});

test('relativeTime', () => {
  assert.equal(U.relativeTime(new Date(Date.now() - 3 * 86400000)), '3天前');
  assert.equal(U.relativeTime(new Date(Date.now() + 2 * 3600000)), '2小时后');
  assert.equal(U.relativeTime(new Date()), '刚刚');
});

/* ---------------- UUID / 密码 ---------------- */

test('UUID v4 格式与唯一性', () => {
  const set = new Set();
  for (let i = 0; i < 1000; i++) {
    const id = U.uuidV4();
    assert.match(id, /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/);
    set.add(id);
  }
  assert.equal(set.size, 1000);
});

test('randPassword 长度/字符集/报错', () => {
  for (let i = 0; i < 200; i++) {
    const p = U.randPassword({ length: 16, lower: true, upper: true, digits: true, symbols: true });
    assert.equal(p.length, 16);
    assert.match(p, /^[A-Za-z0-9!@#$%^&*()\-_=+[\]{}<>?/]+$/);
  }
  const digitsOnly = U.randPassword({ length: 20, lower: false, upper: false, digits: true, symbols: false });
  assert.match(digitsOnly, /^\d{20}$/);
  assert.throws(() => U.randPassword({ length: 8, lower: false, upper: false, digits: false, symbols: false }));
  const clean = U.randPassword({ length: 40, lower: true, upper: true, digits: true, symbols: true, avoidAmbiguous: true });
  assert.ok(!/[0O1lI]/.test(clean));
});

/* ---------------- 命名风格 ---------------- */

test('命名风格转换', () => {
  assert.deepEqual(U.tokenizeName('XMLHttpRequest'), ['xml', 'http', 'request']);
  assert.equal(U.toCamel('user_name'), 'userName');
  assert.equal(U.toCamel('foo-bar-baz'), 'fooBarBaz');
  assert.equal(U.toPascal('hello world'), 'HelloWorld');
  assert.equal(U.toSnake('fooBarBaz'), 'foo_bar_baz');
  assert.equal(U.toKebab('XMLHttpRequest'), 'xml-http-request');
  assert.equal(U.toConst('foo bar'), 'FOO_BAR');
});

/* ---------------- 文本统计 ---------------- */

test('textStats 中英文混排', () => {
  const s = '你好世界 hello world\n第二次';
  const st = U.textStats(s);
  assert.equal(st.chars, 20);
  assert.equal(st.cjk, 7);
  assert.equal(st.words, 9);
  assert.equal(st.lines, 2);
  assert.equal(st.bytes, 34);
});

/* ---------------- Diff ---------------- */

test('diffLines 基本场景', () => {
  const a = 'line1\nline2\nline3';
  const b = 'line1\nlineX\nline3\nline4';
  const ops = U.diffLines(a, b);
  assert.deepEqual(ops.map(o => o.type + ':' + o.text), [
    'same:line1', 'del:line2', 'add:lineX', 'same:line3', 'add:line4'
  ]);
  // 完全一致
  const same = U.diffLines('a\nb', 'a\nb');
  assert.ok(same.every(o => o.type === 'same'));
  // 空对比
  const fromEmpty = U.diffLines('', 'x');
  assert.deepEqual(fromEmpty, [{ type: 'add', text: 'x' }]);
});

/* ---------------- JWT ---------------- */

test('jwtDecode 解析与报错', () => {
  const b64url = (o) => Buffer.from(JSON.stringify(o)).toString('base64url');
  const token = `${b64url({ alg: 'HS256', typ: 'JWT' })}.${b64url({ sub: 'u1', exp: 1700000000 })}.SIG`;
  const d = U.jwtDecode(token);
  assert.equal(d.header.alg, 'HS256');
  assert.equal(d.payload.sub, 'u1');
  assert.equal(d.payload.exp, 1700000000);
  assert.equal(d.signature, 'SIG');
  assert.throws(() => U.jwtDecode('not-a-jwt'));
});

/* ---------------- 进制 ---------------- */

test('进制转换 BigInt 精确 + 全进制回转', () => {
  assert.equal(U.parseBigIntInBase('ff', 16), 255n);
  assert.equal(U.parseBigIntInBase('0x1F', 16), 31n);
  assert.equal(U.parseBigIntInBase('-101', 2), -5n);
  assert.equal(U.bigIntToBase(255n, 16), 'ff');
  assert.equal(U.bigIntToBase(-5n, 2), '-101');
  assert.throws(() => U.parseBigIntInBase('129', 8));
  // 大数精度：2^64+12345 在所有进制可无损回转
  const big = (1n << 64n) + 12345n;
  for (let base = 2; base <= 36; base++) {
    const s = U.bigIntToBase(big, base);
    assert.equal(U.parseBigIntInBase(s, base), big, 'base=' + base);
  }
});

/* ---------------- 颜色 ---------------- */

test('颜色转换', () => {
  assert.deepEqual(U.hexToRgb('#4f6ef7'), { r: 79, g: 110, b: 247, a: 1 });
  assert.deepEqual(U.hexToRgb('#abc'), { r: 170, g: 187, b: 204, a: 1 });
  assert.equal(U.hexToRgb('#zzz'), null);
  assert.equal(U.rgbToHex({ r: 79, g: 110, b: 247 }), '#4f6ef7');
  const hsl = U.rgbToHsl({ r: 255, g: 0, b: 0 });
  assert.deepEqual(hsl, { h: 0, s: 100, l: 50 });
  const back = U.hslToRgb(hsl);
  assert.deepEqual(back, { r: 255, g: 0, b: 0 });
  // 往返误差 ≤1
  for (const [r, g, b] of [[79, 110, 247], [12, 200, 130], [255, 255, 0]]) {
    const h = U.rgbToHsl({ r, g, b });
    const c = U.hslToRgb(h);
    assert.ok(Math.abs(c.r - r) <= 1 && Math.abs(c.g - g) <= 1 && Math.abs(c.b - b) <= 1);
  }
});

test('parseColor 支持 hex/rgb/hsl', () => {
  assert.deepEqual(U.parseColor('#ff0000'), { r: 255, g: 0, b: 0, a: 1 });
  assert.deepEqual(U.parseColor('rgb(0, 128, 255)'), { r: 0, g: 128, b: 255, a: 1 });
  assert.deepEqual(U.parseColor('rgba(0,0,0,0.5)'), { r: 0, g: 0, b: 0, a: 0.5 });
  const c = U.parseColor('hsl(120, 100%, 50%)');
  assert.deepEqual(c, { r: 0, g: 255, b: 0, a: 1 });
  assert.equal(U.parseColor('not-a-color'), null);
});

test('对比度计算（WCAG）', () => {
  const white = { r: 255, g: 255, b: 255 }, black = { r: 0, g: 0, b: 0 };
  assert.equal(U.contrastRatio(white, black).toFixed(2), '21.00');
  assert.equal(U.contrastRatio(white, white), 1);
});

/* ---------------- 单位 ---------------- */

test('单位换算', () => {
  const len = U.UNIT_GROUPS.find(g => g.id === 'length');
  assert.equal(U.convertUnit(1, 'km', 'm', len), 1000);
  assert.equal(U.convertUnit(1, 'in', 'mm', len), 25.4);
  const data = U.UNIT_GROUPS.find(g => g.id === 'data');
  assert.equal(U.convertUnit(1, 'GiB', 'MiB', data), 1024);
  assert.equal(U.convertUnit(1, 'GB', 'MB', data), 1000);
  const temp = U.UNIT_GROUPS.find(g => g.id === 'temp');
  assert.equal(U.convertUnit(100, 'C', 'F', temp), 212);
  assert.equal(U.convertUnit(0, 'C', 'K', temp), 273.15);
  const weight = U.UNIT_GROUPS.find(g => g.id === 'weight');
  assert.equal(U.convertUnit(1, 'jin', 'kg', weight), 0.5);
});

/* ---------------- 其他 ---------------- */

test('fmtNum 输出整洁', () => {
  assert.equal(U.fmtNum(0.30000000000000004), '0.3');
  assert.equal(U.fmtNum(1000), '1000');
});

test('passwordEntropyBits 合理', () => {
  assert.ok(U.passwordEntropyBits(12, 94) > 70 && U.passwordEntropyBits(12, 94) < 90);
});
