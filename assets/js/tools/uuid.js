/* UUID v4 批量生成 */
(function () {
  'use strict';
  var D = globalThis.DevBox, U = globalThis.DevUtil;

  D.register({
    id: 'uuid',
    name: 'UUID 生成',
    icon: '🆔',
    category: 'gen',
    desc: '批量生成 UUID v4，支持大写 / 去连字符 / 花括号',
    keywords: ['uuid', 'guid', 'v4', '唯一', '标识', '生成'],
    render: function (el) {
      var countInput = U.h('input', { class: 'input', type: 'number', min: '1', max: '100', value: '5', style: 'width:90px' });
      var upperChk = U.h('input', { type: 'checkbox' });
      var noDashChk = U.h('input', { type: 'checkbox' });
      var braceChk = U.h('input', { type: 'checkbox' });
      var out = U.h('div', { class: 'out', style: 'min-height:120px' }, U.h('span', { class: 'placeholder' }, '点击生成…'));
      var last = [];

      function fmtOne(id) {
        var s = id;
        if (upperChk.checked) s = s.toUpperCase();
        if (noDashChk.checked) s = s.replace(/-/g, '');
        if (braceChk.checked) s = '{' + s + '}';
        return s;
      }
      function gen() {
        var n = Math.max(1, Math.min(100, parseInt(countInput.value, 10) || 1));
        countInput.value = String(n);
        last = [];
        for (var i = 0; i < n; i++) last.push(fmtOne(U.uuidV4()));
        out.textContent = last.join('\n');
      }

      el.append(
        U.h('div', { class: 'panel' },
          U.h('div', { class: 'row' },
            U.h('button', { class: 'btn', onclick: gen }, '⚡ 生成'),
            U.h('label', { class: 'check' }, '数量 ', countInput),
            U.h('span', { class: 'spacer' }),
            U.h('label', { class: 'check' }, upperChk, '大写'),
            U.h('label', { class: 'check' }, noDashChk, '去连字符'),
            U.h('label', { class: 'check' }, braceChk, '花括号')),
          U.h('p', { class: 'muted', style: 'margin:8px 0 0;font-size:12.5px' },
            '修改选项后重新点击生成即可按新格式输出。')),
        U.h('div', { class: 'panel' },
          U.h('p', { class: 'panel-title' }, '结果'),
          out,
          U.h('div', { class: 'row', style: 'margin-top:10px' },
            D.copyBtn(function () { return last.join('\n'); }, '复制全部'),
            D.copyBtn(function () { return last[0] || ''; }, '复制第一条')))
      );
      gen();
    }
  });
})();
