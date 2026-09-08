/* 进制转换（BigInt 精确，2~36 进制） */
(function () {
  'use strict';
  var D = globalThis.DevBox, U = globalThis.DevUtil;

  D.register({
    id: 'numberbase',
    name: '进制转换',
    icon: '🔢',
    category: 'convert',
    desc: '2~36 进制互转，BigInt 精确无精度丢失，含位视图',
    keywords: ['进制', 'binary', 'hex', 'octal', 'decimal', 'base', '位', '二进制', '十六进制'],
    render: function (el) {
      var valueInput = U.h('input', { class: 'input', style: 'width:100%;font-family:var(--mono)', placeholder: '输入数字…' });
      var baseSel = U.h('select', { class: 'select' },
        [2, 8, 10, 16, 36].map(function (b) {
          var o = U.h('option', { value: String(b) }, b + ' 进制');
          if (b === 10) o.selected = true;
          return o;
        }));
      var outGrid = U.h('div', {});
      var bitView = U.h('div', {});
      var errBox = U.h('div', {});

      function render() {
        outGrid.innerHTML = ''; bitView.innerHTML = ''; errBox.innerHTML = '';
        var v = valueInput.value.trim();
        if (!v) { outGrid.append(U.h('span', { class: 'muted' }, '输入数字后自动转换')); return; }
        var n;
        try { n = U.parseBigIntInBase(v, Number(baseSel.value)); }
        catch (e) { errBox.append(U.h('div', { class: 'err-text' }, '✗ ' + e.message)); return; }

        var bases = [2, 8, 10, 16, 36];
        outGrid.append(U.h('div', { class: 'kv' }, bases.map(function (b) {
          var s = U.bigIntToBase(n, b);
          var label = b === 2 ? '二进制' : b === 8 ? '八进制' : b === 10 ? '十进制' : b === 16 ? '十六进制' : '36 进制';
          return [U.h('span', { class: 'k' }, label),
                  U.h('span', { class: 'v' }, b !== 10 ? s : s, D.copyBtn(s, '📋'))];
        })));

        /* 位视图（≤512 位） */
        if (n > 0n && n < (1n << 512n)) {
          var hex = n.toString(16).toUpperCase();
          if (hex.length % 2) hex = '0' + hex;
          var bytes = hex.match(/.{2}/g) || [];
          var ascii = bytes.map(function (b) {
            var code = parseInt(b, 16);
            return code >= 32 && code < 127 ? String.fromCharCode(code) : '·';
          }).join('');
          bitView.append(
            U.h('p', { class: 'panel-title', style: 'margin-top:14px' }, '字节视图'),
            U.h('div', { class: 'out', style: 'max-height:130px' },
              'HEX  ' + (bytes.join(' ') || '00') + '\n' +
              'ASCII ' + ascii),
            D.copyBtn(hex, '复制 HEX'));
        }
      }
      valueInput.addEventListener('input', U.debounce(render, 150));
      baseSel.addEventListener('change', render);
      valueInput.value = '2026';
      render();

      el.append(
        U.h('div', { class: 'panel' },
          U.h('div', { class: 'row' },
            U.h('div', { class: 'field', style: 'flex:1;min-width:200px' }, U.h('label', {}, '数值'), valueInput),
            U.h('div', { class: 'field' }, U.h('label', {}, '输入进制'), baseSel)),
          errBox),
        U.h('div', { class: 'panel' },
          U.h('p', { class: 'panel-title' }, '转换结果'),
          outGrid,
          bitView)
      );
    }
  });
})();
