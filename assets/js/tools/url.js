/* URL 编解码 */
(function () {
  'use strict';
  var D = globalThis.DevBox, U = globalThis.DevUtil;

  D.register({
    id: 'url',
    name: 'URL 编解码',
    icon: '🔗',
    category: 'encode',
    desc: 'encodeURIComponent / encodeURI 双模式互转',
    keywords: ['url', 'encode', 'decode', 'uri', '编码', '解码', '转义', 'percent'],
    render: function (el) {
      var input = U.h('textarea', { class: 'textarea', placeholder: '输入 URL 或含特殊字符的文本…' });
      var output = U.h('div', { class: 'out' }, U.h('span', { class: 'placeholder' }, '输出显示在这里'));

      function tryRun(fn, name) {
        return function () {
          var src = input.value;
          if (!src) { output.innerHTML = ''; return; }
          try {
            output.textContent = fn(src);
            D.toast('✓ 已' + name);
          } catch (e) {
            output.innerHTML = '';
            output.append(U.h('span', { class: 'err-text' }, '✗ ' + e.message));
          }
        };
      }

      el.append(
        U.h('div', { class: 'panel' },
          U.h('p', { class: 'panel-title' }, '输入'),
          input,
          U.h('div', { class: 'row', style: 'margin-top:10px' },
            U.h('button', { class: 'btn', onclick: tryRun(encodeURIComponent, '编码（组件模式）') }, '编码'),
            U.h('button', { class: 'btn ghost', onclick: tryRun(decodeURIComponent, '解码（组件模式）') }, '解码'),
            U.h('button', { class: 'btn ghost', onclick: tryRun(encodeURI, '编码（保留 URL 结构）') }, '编码(URI)'),
            U.h('button', { class: 'btn ghost', onclick: tryRun(decodeURI, '解码(URI)') }, '解码(URI)'),
            U.h('button', { class: 'btn ghost', onclick: function () { input.value = ''; output.textContent = ''; } }, '清空')),
          U.h('p', { class: 'muted', style: 'margin:10px 0 0' },
            '组件模式会转义 ?, =, & 等所有保留字符，适合参数值；URI 模式保留 ://?&= 结构，适合整条 URL。')),
        U.h('div', { class: 'panel' },
          U.h('p', { class: 'panel-title' }, '输出'),
          output,
          U.h('div', { class: 'row', style: 'margin-top:10px' },
            D.copyBtn(function () { return output.textContent; }),
            U.h('button', { class: 'btn ghost sm', onclick: function () { var t = input.value; input.value = output.textContent; output.textContent = t; } }, '⇄ 交换')))
      );

      input.value = 'https://example.com/search?q=你好 世界&lang=zh';
    }
  });
})();
