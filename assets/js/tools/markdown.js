/* Markdown 预览（marked 本地渲染） */
(function () {
  'use strict';
  var D = globalThis.DevBox, U = globalThis.DevUtil;

  var SAMPLE = '# DevBox 工具箱\n\n纯前端 **Markdown** 实时预览，数据不出浏览器。\n\n## 特性\n\n- 无依赖构建，克隆即用\n- 支持 `代码` 与代码块\n- 表格、引用、图片……\n\n```js\nconsole.log("Hello DevBox!");\n```\n\n> 提示：左侧编辑，右侧实时渲染\n\n| 工具 | 数量 |\n|------|-----:|\n| 编码加密 | 5 |\n| 转换计算 | 4 |\n';

  D.register({
    id: 'markdown',
    name: 'Markdown 预览',
    icon: '📖',
    category: 'data',
    desc: 'Markdown 实时渲染预览，一键复制 HTML',
    keywords: ['markdown', 'md', '预览', '渲染', 'editor', 'html'],
    render: function (el) {
      var ta = U.h('textarea', { class: 'textarea', style: 'min-height:420px;font-size:13.5px' });
      var view = U.h('div', { class: 'md-body' });
      var lastHtml = '';

      function render() {
        var src = ta.value;
        try {
          lastHtml = globalThis.marked.parse(src);
          view.innerHTML = lastHtml;
        } catch (e) {
          view.innerHTML = '';
          view.append(U.h('span', { class: 'err-text' }, '✗ ' + e.message));
        }
      }
      ta.addEventListener('input', U.debounce(render, 150));
      ta.value = SAMPLE;
      render();

      el.append(
        U.h('div', { class: 'grid2' },
          U.h('div', { class: 'panel' },
            U.h('p', { class: 'panel-title' }, 'Markdown 源码'),
            ta,
            U.h('div', { class: 'row', style: 'margin-top:10px' },
              U.h('button', { class: 'btn ghost sm', onclick: function () { ta.value = SAMPLE; render(); } }, '示例'),
              U.h('button', { class: 'btn ghost sm', onclick: function () { ta.value = ''; render(); } }, '清空'))),
          U.h('div', { class: 'panel' },
            U.h('p', { class: 'panel-title' }, '预览'),
            view,
            U.h('div', { class: 'row', style: 'margin-top:10px' },
              D.copyBtn(function () { return lastHtml; }, '复制 HTML'))))
      );
    }
  });
})();
