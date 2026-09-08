/* 正则表达式测试器：实时匹配、高亮、捕获组、速查表 */
(function () {
  'use strict';
  var D = globalThis.DevBox, U = globalThis.DevUtil;

  D.register({
    id: 'regex',
    name: '正则测试',
    icon: '🔭',
    category: 'text',
    desc: '实时匹配高亮、捕获组解析、常用正则速查',
    keywords: ['regex', 'regexp', '正则', '表达式', '匹配', 'pattern'],
    render: function (el) {
      var patInput = U.h('input', { class: 'input', style: 'flex:1;min-width:220px;font-family:var(--mono)', placeholder: '输入正则表达式，如 \\d+' });
      var flags = { g: U.h('input', { type: 'checkbox', checked: true }), i: U.h('input', { type: 'checkbox' }),
                    m: U.h('input', { type: 'checkbox' }), s: U.h('input', { type: 'checkbox' }),
                    u: U.h('input', { type: 'checkbox' }) };
      var textInput = U.h('textarea', { class: 'textarea', placeholder: '被测试的文本…' });
      var preview = U.h('div', { class: 'regex-preview' }, U.h('span', { class: 'placeholder muted' }, '匹配高亮显示在这里'));
      var matchList = U.h('div', {});
      var errBox = U.h('div', {});

      var CHEATS = [
        ['邮箱', '[\\w.+-]+@[\\w-]+\\.[\\w.]+'],
        ['手机号（中国）', '1[3-9]\\d{9}'],
        ['URL', 'https?://[^\\s<>"\']+'],
        ['IPv4', '\\b(?:(?:25[0-5]|2[0-4]\\d|1?\\d?\\d)\\.){3}(?:25[0-5]|2[0-4]\\d|1?\\d?\\d)\\b'],
        ['日期 YYYY-MM-DD', '\\d{4}-\\d{2}-\\d{2}'],
        ['中文汉字', '[\\u4e00-\\u9fff]+'],
        ['十六进制颜色', '#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})\\b'],
        ['正整数', '^\\d+$']
      ];

      function getRegex() {
        var f = '';
        Object.keys(flags).forEach(function (k) { if (flags[k].checked) f += k; });
        return new RegExp(patInput.value, f);
      }

      function render() {
        errBox.innerHTML = ''; matchList.innerHTML = '';
        preview.innerHTML = '';
        var pat = patInput.value;
        if (!pat) { preview.append(U.h('span', { class: 'placeholder muted' }, '输入正则后自动匹配')); return; }
        var re;
        try { re = getRegex(); }
        catch (e) {
          errBox.append(U.h('div', { class: 'err-text' }, '✗ 正则语法错误：' + e.message));
          return;
        }
        var text = textInput.value;
        var matches = [];
        if (re.global) {
          var m, guard = 0;
          while ((m = re.exec(text)) !== null && guard++ < 10000) {
            matches.push({ index: m.index, match: m[0], groups: m.slice(1) });
            if (m[0] === '') re.lastIndex++;
          }
        } else {
          var m0 = re.exec(text);
          if (m0) matches.push({ index: m0.index, match: m0[0], groups: m0.slice(1) });
        }

        /* 高亮（最多 500 处，防卡顿） */
        var frag = document.createDocumentFragment();
        var pos = 0;
        matches.slice(0, 500).forEach(function (mt, i) {
          frag.append(document.createTextNode(text.slice(pos, mt.index)));
          frag.append(U.h('mark', { class: 'g' + Math.min(3, Math.max(1, (i % 3) + 1)) }, mt.match));
          pos = mt.index + mt.match.length;
        });
        frag.append(document.createTextNode(text.slice(pos)));
        preview.appendChild(frag);

        /* 匹配列表 */
        if (!matches.length) {
          matchList.append(U.h('div', { class: 'muted' }, '没有匹配'));
        } else {
          var badge = U.h('span', { class: 'badge accent' }, matches.length + ' 处匹配');
          var tbl = U.h('table', { class: 'tbl' },
            U.h('thead', {}, U.h('tr', {}, U.h('th', {}, '#'), U.h('th', {}, '位置'), U.h('th', {}, '匹配'), U.h('th', {}, '捕获组'))),
            U.h('tbody', {}, matches.slice(0, 200).map(function (mt, i) {
              return U.h('tr', {},
                U.h('td', {}, String(i + 1)),
                U.h('td', { class: 'mono' }, String(mt.index)),
                U.h('td', { class: 'mono' }, mt.match),
                U.h('td', { class: 'mono muted' }, mt.groups.length ? mt.groups.map(function (g, gi) { return '$' + (gi + 1) + ' = ' + (g == null ? '∅' : g); }).join('  ') : '-'));
            })));
          matchList.append(U.h('div', { class: 'panel' }, U.h('p', { class: 'panel-title' }, '匹配结果 ', badge), tbl));
        }
      }

      patInput.addEventListener('input', U.debounce(render, 200));
      textInput.addEventListener('input', U.debounce(render, 200));
      Object.keys(flags).forEach(function (k) {
        flags[k].addEventListener('change', render);
      });

      patInput.value = '[\\w.+-]+@[\\w-]+\\.[\\w.]+';
      textInput.value = '联系方式：\n邮箱 dev@devbox.tools（工作）\n备用 admin@example.com.cn\n电话不提供';
      render();

      el.append(
        U.h('div', { class: 'panel' },
          U.h('div', { class: 'row' },
            U.h('span', { class: 'mono muted' }, '/'), patInput, U.h('span', { class: 'mono muted' }, '/gi'),
            Object.keys(flags).map(function (k) {
              return U.h('label', { class: 'check', title: '标志 ' + k }, flags[k], k);
            })),
          errBox,
          U.h('div', { class: 'field', style: 'margin-top:12px' }, U.h('label', {}, '测试文本'), textInput),
          U.h('div', { class: 'field', style: 'margin-top:12px' }, U.h('label', {}, '高亮预览'), preview)),
        matchList,
        U.h('details', { class: 'sheet' },
          U.h('summary', {}, '📎 常用正则速查（点击填入）'),
          U.h('div', { class: 'sheet-body' },
            U.h('table', { class: 'tbl' },
              U.h('tbody', {}, CHEATS.map(function (c) {
                return U.h('tr', {},
                  U.h('td', { style: 'white-space:nowrap' }, c[0]),
                  U.h('td', { class: 'mono' }, c[1]),
                  U.h('td', { style: 'width:70px' },
                    U.h('button', { class: 'btn ghost sm', onclick: function () { patInput.value = c[1]; render(); } }, '填入')));
              })))))
      );
    }
  });
})();
