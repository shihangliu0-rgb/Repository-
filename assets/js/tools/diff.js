/* 文本差异对比（行级 LCS） */
(function () {
  'use strict';
  var D = globalThis.DevBox, U = globalThis.DevUtil;

  D.register({
    id: 'diff',
    name: '文本差异',
    icon: '🔀',
    category: 'text',
    desc: '两段文本行级对比，类似 git diff 的可读结果',
    keywords: ['diff', 'compare', '对比', '差异', '比较', '文本'],
    render: function (el) {
      var ta = U.h('textarea', { class: 'textarea', placeholder: '原始文本…' });
      var tb = U.h('textarea', { class: 'textarea', placeholder: '修改后的文本…' });
      var result = U.h('div', {});
      var statSpan = U.h('span', {});

      function render() {
        result.innerHTML = '';
        statSpan.textContent = '';
        if (!ta.value && !tb.value) return;
        var ops;
        try { ops = U.diffLines(ta.value, tb.value); }
        catch (e) { result.append(U.h('div', { class: 'err-text' }, '✗ ' + e.message)); return; }
        var add = ops.filter(function (o) { return o.type === 'add'; }).length;
        var del = ops.filter(function (o) { return o.type === 'del'; }).length;
        statSpan.append(
          U.h('span', { class: 'badge ok' }, '+' + add),
          ' ', U.h('span', { class: 'badge err' }, '−' + del), ' ',
          U.h('span', { class: 'badge' }, ops.length + ' 行'));
        if (!add && !del) {
          result.append(U.h('div', { class: 'badge ok', style: 'display:inline-block;padding:6px 14px' }, '✓ 两段文本完全一致'));
          return;
        }
        var box = U.h('div', { class: 'diffbox' }, ops.map(function (o) {
          var sign = o.type === 'add' ? '+' : o.type === 'del' ? '-' : ' ';
          return U.h('div', { class: 'diffline ' + o.type },
            U.h('span', { class: 'sign' }, sign), o.text === '' ? ' ' : o.text);
        }));
        result.append(box);
      }

      var debounced = U.debounce(render, 300);
      ta.addEventListener('input', debounced);
      tb.addEventListener('input', debounced);

      ta.value = 'DevBox 工具箱\n版本 1.0\n纯前端实现\n支持暗色模式';
      tb.value = 'DevBox 开发者工具箱\n版本 1.0\n纯前端实现，无依赖\n支持暗色模式\n离线可用';
      render();

      el.append(
        U.h('div', { class: 'grid2' },
          U.h('div', { class: 'panel' }, U.h('p', { class: 'panel-title' }, '原文 A'), ta),
          U.h('div', { class: 'panel' }, U.h('p', { class: 'panel-title' }, '修改后 B'), tb)),
        U.h('div', { class: 'panel' },
          U.h('p', { class: 'panel-title' }, '差异结果 ', statSpan),
          result,
          U.h('div', { class: 'row', style: 'margin-top:10px' },
            D.copyBtn(function () {
              return Array.from(result.querySelectorAll('.diffline'))
                .map(function (d) { return d.textContent; }).join('\n');
            }, '复制结果'),
            U.h('button', { class: 'btn ghost sm', onclick: function () { var t = ta.value; ta.value = tb.value; tb.value = t; render(); } }, '⇄ 交换')))
      );
    }
  });
})();
