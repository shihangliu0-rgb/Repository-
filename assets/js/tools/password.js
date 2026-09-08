/* 密码生成器 */
(function () {
  'use strict';
  var D = globalThis.DevBox, U = globalThis.DevUtil;

  D.register({
    id: 'password',
    name: '密码生成',
    icon: '🔑',
    category: 'gen',
    desc: '自定义长度与字符集，强度熵值评估',
    keywords: ['password', '密码', '随机', '安全', 'generator'],
    render: function (el) {
      var lenRange = U.h('input', { type: 'range', min: '6', max: '64', value: '16', style: 'flex:1' });
      var lenLabel = U.h('b', { class: 'mono' }, '16');
      var lower = U.h('input', { type: 'checkbox', checked: true });
      var upper = U.h('input', { type: 'checkbox', checked: true });
      var digits = U.h('input', { type: 'checkbox', checked: true });
      var symbols = U.h('input', { type: 'checkbox', checked: true });
      var avoid = U.h('input', { type: 'checkbox' });
      var count = U.h('input', { type: 'number', min: '1', max: '20', value: '5', class: 'input', style: 'width:80px' });
      var out = U.h('div', {});
      var strength = U.h('span', { class: 'badge' }, '');

      lenRange.addEventListener('input', function () { lenLabel.textContent = lenRange.value; });

      function poolSize() {
        var n = 0;
        if (lower.checked) n += 26;
        if (upper.checked) n += 26;
        if (digits.checked) n += 10;
        if (symbols.checked) n += 22;
        return n;
      }
      function renderStrength() {
        var bits = U.passwordEntropyBits(Number(lenRange.value), poolSize());
        var cls, txt;
        if (bits >= 100) { cls = 'ok'; txt = '极强'; }
        else if (bits >= 75) { cls = 'ok'; txt = '强'; }
        else if (bits >= 55) { cls = 'warn'; txt = '中等'; }
        else { cls = 'err'; txt = '弱'; }
        strength.className = 'badge ' + cls;
        strength.textContent = '强度：' + txt + '（约 ' + bits + ' bit 熵）';
      }
      [lower, upper, digits, symbols].forEach(function (c) { c.addEventListener('change', renderStrength); });
      lenRange.addEventListener('input', renderStrength);

      function gen() {
        out.innerHTML = '';
        var n = Math.max(1, Math.min(20, parseInt(count.value, 10) || 1));
        try {
          for (var i = 0; i < n; i++) {
            (function () {
              var pwd = U.randPassword({
                length: Number(lenRange.value),
                lower: lower.checked, upper: upper.checked,
                digits: digits.checked, symbols: symbols.checked,
                avoidAmbiguous: avoid.checked
              });
              out.append(U.h('div', { class: 'out', style: 'margin-bottom:8px;display:flex;align-items:center;gap:8px' },
                U.h('span', { style: 'flex:1;font-size:14px;letter-spacing:0.4px' }, pwd),
                D.copyBtn(pwd, '复制')));
            })();
          }
        } catch (e) {
          out.append(U.h('div', { class: 'err-text' }, '✗ ' + e.message));
        }
      }

      lenRange.value = '16'; lenLabel.textContent = '16';
      renderStrength();
      gen();

      el.append(
        U.h('div', { class: 'panel' },
          U.h('p', { class: 'panel-title' }, '选项'),
          U.h('div', { class: 'row', style: 'margin-bottom:12px' },
            U.h('label', { class: 'check', style: 'flex:1;min-width:220px' }, '长度 ', lenRange, lenLabel)),
          U.h('div', { class: 'row' },
            U.h('label', { class: 'check' }, lower, '小写 a-z'),
            U.h('label', { class: 'check' }, upper, '大写 A-Z'),
            U.h('label', { class: 'check' }, digits, '数字 0-9'),
            U.h('label', { class: 'check' }, symbols, '符号'),
            U.h('label', { class: 'check' }, avoid, '排除易混淆（0O1lI…）')),
          U.h('div', { class: 'row', style: 'margin-top:14px' },
            U.h('button', { class: 'btn', onclick: gen }, '⚡ 生成密码'),
            U.h('label', { class: 'check' }, '数量 ', count),
            U.h('span', { class: 'spacer' }), strength)),
        U.h('div', { class: 'panel' },
          U.h('p', { class: 'panel-title' }, '结果'),
          out)
      );
    }
  });
})();
