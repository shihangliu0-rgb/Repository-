/* 文本处理：命名风格、行操作、大小写、实时统计 */
(function () {
  'use strict';
  var D = globalThis.DevBox, U = globalThis.DevUtil;

  D.register({
    id: 'textproc',
    name: '文本处理',
    icon: '✂️',
    category: 'text',
    desc: '驼峰/下划线互转、去重排序、大小写、字数统计',
    keywords: ['text', '文本', '驼峰', 'snake', 'camel', '去重', '排序', '统计', '字数'],
    render: function (el) {
      var ta = U.h('textarea', { class: 'textarea', style: 'min-height:220px' });
      var stat = U.h('div', { class: 'row tight' });

      function apply(fn, label) {
        return function () {
          ta.value = fn(ta.value);
          renderStats();
          D.toast('✓ 已' + label);
        };
      }
      function perLine(fn) {
        return apply(function (s) { return s.split('\n').map(fn).join('\n'); }, '处理');
      }

      function renderStats() {
        var s = U.textStats(ta.value);
        stat.innerHTML = '';
        [['字符', s.chars], ['不含空格', s.charsNoSpace], ['单词', s.words],
         ['汉字', s.cjk], ['行数', s.lines], ['UTF-8 字节', U.formatBytes(s.bytes)]].forEach(function (p) {
          stat.append(U.h('span', { class: 'badge' }, p[0] + ' ' + p[1]));
        });
      }
      ta.addEventListener('input', U.debounce(renderStats, 150));

      var NAMING = [['camelCase', U.toCamel], ['PascalCase', U.toPascal], ['snake_case', U.toSnake],
                    ['kebab-case', U.toKebab], ['CONSTANT_CASE', U.toConst]];
      var LINES = [['去重', function (lines) { return Array.from(new Set(lines)); }],
                   ['排序 A→Z', function (lines) { return lines.slice().sort(); }],
                   ['排序 Z→A', function (lines) { return lines.slice().sort().reverse(); }],
                   ['反转顺序', function (lines) { return lines.slice().reverse(); }],
                   ['去空行', function (lines) { return lines.filter(function (l) { return l.trim() !== ''; }); }],
                   ['去首尾空格', function (lines) { return lines.map(function (l) { return l.trim(); }); }],
                   ['添加行号', function (lines) { return lines.map(function (l, i) { return i + 1 + '. ' + l; }); }],
                   ['打乱顺序', function (lines) {
                     var a = lines.slice();
                     for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var t = a[i]; a[i] = a[j]; a[j] = t; }
                     return a;
                   }]];
      var CASES = [['全部大写', function (s) { return s.toUpperCase(); }],
                   ['全部小写', function (s) { return s.toLowerCase(); }],
                   ['每词首字母大写', function (s) { return s.replace(/[A-Za-z]+/g, function (w) { return w.charAt(0).toUpperCase() + w.slice(1); }); }],
                   ['句首大写', function (s) { return s.replace(/(^|[.!?]\s+)([a-z])/g, function (m, a, b) { return a + b.toUpperCase(); }); }]];

      ta.value = 'dev box tools\nhello_world\nuserName\nDevBox 工具箱\nhello\nworld\nhello';
      renderStats();

      function btnGroup(title, list, fnMaker) {
        return U.h('div', {},
          U.h('p', { class: 'panel-title', style: 'margin:12px 0 8px' }, title),
          U.h('div', { class: 'row tight' }, list.map(function (item) {
            return U.h('button', { class: 'btn ghost sm', onclick: fnMaker(item) }, item[0]);
          })));
      }

      el.append(
        U.h('div', { class: 'panel' },
          U.h('p', { class: 'panel-title' }, '文本'),
          ta,
          U.h('div', { class: 'row', style: 'margin-top:10px' },
            U.h('button', { class: 'btn ghost sm', onclick: function () { U.copyText(ta.value).then(function () { D.toast('✓ 已复制'); }); } }, '复制全部'),
            U.h('button', { class: 'btn ghost sm', onclick: function () { ta.value = ''; renderStats(); } }, '清空')),
          U.h('div', { style: 'margin-top:10px' }, stat)),
        U.h('div', { class: 'panel' },
          U.h('p', { class: 'panel-title' }, '操作（直接修改上方文本）'),
          btnGroup('🔤 命名风格（按行转换）', NAMING, function (item) {
            return perLine(function (line) { return item[1](line) || line; });
          }),
          btnGroup('📋 行操作', LINES, function (item) {
            return apply(function (s) { return item[1](s.split('\n')).join('\n'); }, item[0]);
          }),
          btnGroup('🔠 大小写', CASES, function (item) {
            return apply(item[1], item[0]);
          }))
      );
    }
  });
})();
