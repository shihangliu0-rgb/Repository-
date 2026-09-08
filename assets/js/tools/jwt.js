/* JWT 解码器（不验证签名，仅解析） */
(function () {
  'use strict';
  var D = globalThis.DevBox, U = globalThis.DevUtil;

  D.register({
    id: 'jwt',
    name: 'JWT 解码',
    icon: '🎫',
    category: 'encode',
    desc: '解析 JWT 的 Header / Payload，自动识别过期时间',
    keywords: ['jwt', 'token', 'decode', '令牌', '解码', 'auth'],
    render: function (el) {
      var input = U.h('textarea', { class: 'textarea', placeholder: '粘贴 JWT（eyJhbGci… 格式）…' });
      var out = U.h('div', {});

      function render() {
        out.innerHTML = '';
        var token = input.value.trim();
        if (!token) { out.append(U.h('span', { class: 'placeholder muted' }, '等待输入…')); return; }
        var decoded;
        try { decoded = U.jwtDecode(token); }
        catch (e) {
          out.append(U.h('div', { class: 'err-text' }, '✗ ' + e.message));
          return;
        }
        var now = Date.now() / 1000;

        function pretty(obj) { return JSON.stringify(obj, null, 2); }
        function timeRow(label, v) {
          if (typeof v !== 'number') return null;
          var d = new Date(v * 1000);
          var expired = label === 'exp' && v < now;
          return U.h('div', { class: 'kv' },
            U.h('span', { class: 'k' }, label),
            U.h('span', { class: 'v' },
              String(v) + ' → ',
              U.fmtDateTime(d) + '（' + U.relativeTime(d) + '）',
              expired ? U.h('span', { class: 'badge err' }, '已过期') :
                (label === 'exp' ? U.h('span', { class: 'badge ok' }, '有效') : null)));
        }

        var claimRows = [];
        ['exp', 'iat', 'nbf'].forEach(function (k) {
          if (decoded.payload && k in decoded.payload) {
            var r = timeRow(k, decoded.payload[k]);
            if (r) claimRows.push(r);
          }
        });

        out.append(
          U.h('div', { class: 'grid2' },
            U.h('div', {},
              U.h('p', { class: 'panel-title' }, U.h('span', {}, 'HEADER'), ' ', U.h('span', { class: 'badge accent' }, (decoded.header.alg || '?'))),
              U.h('div', { class: 'out' }, pretty(decoded.header), D.copyBtn(function () { return pretty(decoded.header); }))),
            U.h('div', {},
              U.h('p', { class: 'panel-title' }, 'PAYLOAD'),
              U.h('div', { class: 'out' }, pretty(decoded.payload), D.copyBtn(function () { return pretty(decoded.payload); }))))
        );
        if (claimRows.length) {
          out.append(U.h('div', { class: 'panel' }, U.h('p', { class: 'panel-title' }, '时间声明'), U.h('div', {}, claimRows)));
        }
        if (decoded.signature) {
          out.append(U.h('div', { class: 'panel' },
            U.h('p', { class: 'panel-title' }, 'SIGNATURE（本工具不验证签名）'),
            U.h('div', { class: 'out' }, decoded.signature)));
        }
      }

      input.addEventListener('input', U.debounce(render, 250));
      input.value = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IuW8gKDnuiIsImlhdCI6MTcwMDAwMDAwMH0.dummy_signature_replace_me';
      try { render(); } catch (e) {}
      // 示例签名非法不影响展示（本工具不校验签名）
      el.append(U.h('div', { class: 'panel' },
        U.h('p', { class: 'panel-title' }, '输入 Token'), input,
        U.h('p', { class: 'muted', style: 'margin:8px 0 0' }, '⚠️ 仅在本地解码展示，不会发送到任何服务器，也不验证签名。')),
        U.h('div', { class: 'tool-body' }, out));
    }
  });
})();
