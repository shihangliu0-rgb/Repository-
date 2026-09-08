/* 颜色工具：HEX/RGB/HSL 互转、对比度、色板 */
(function () {
  'use strict';
  var D = globalThis.DevBox, U = globalThis.DevUtil;

  D.register({
    id: 'color',
    name: '颜色工具',
    icon: '🎨',
    category: 'convert',
    desc: 'HEX / RGB / HSL 互转，WCAG 对比度检查，随机色板',
    keywords: ['color', 'hex', 'rgb', 'hsl', '颜色', '色彩', '调色', '对比度', 'picker'],
    render: function (el) {
      var picker = U.h('input', { type: 'color', value: '#4f6ef7' });
      var textInput = U.h('input', { class: 'input', style: 'flex:1;min-width:180px;font-family:var(--mono)', value: '#4f6ef7' });
      var swatch = U.h('div', { class: 'swatch' }, '#4F6EF7');
      var convList = U.h('div', {});
      var contrastBox = U.h('div', {});
      var palette = U.h('div', { class: 'palette' });
      var cur = { r: 79, g: 110, b: 247, a: 1 };
      var PALETTE = ['#0ea5e9', '#4f6ef7', '#8b5cf6', '#ec4899', '#ef4444', '#f59e0b', '#22c55e', '#14b8a6', '#64748b', '#0f1218'];

      function luminanceOf(c) { return U.luminance(c); }
      function bestText(c) { return luminanceOf(c) > 0.45 ? '#111' : '#fff'; }

      function render() {
        var hex = U.rgbToHex(cur);
        var hsl = U.rgbToHsl(cur);
        var hslStr = 'hsl(' + Math.round(hsl.h) + ', ' + Math.round(hsl.s) + '%, ' + Math.round(hsl.l) + '%)';
        picker.value = hex.slice(0, 7);
        swatch.style.background = hex;
        swatch.style.color = bestText(cur);
        swatch.textContent = hex.toUpperCase() + (cur.a < 1 ? ' · ' + Math.round(cur.a * 100) + '%' : '');
        convList.innerHTML = '';
        var rows = [
          ['HEX', hex.toUpperCase()],
          ['RGB', 'rgb(' + cur.r + ', ' + cur.g + ', ' + cur.b + ')'],
          ['RGBA', 'rgba(' + cur.r + ', ' + cur.g + ', ' + cur.b + ', ' + (Math.round(cur.a * 100) / 100) + ')'],
          ['HSL', hslStr]
        ];
        convList.append(U.h('div', { class: 'kv' }, rows.map(function (r) {
          return [U.h('span', { class: 'k' }, r[0]),
                  U.h('span', { class: 'v' }, r[1], D.copyBtn(r[1], '📋'))];
        })));

        contrastBox.innerHTML = '';
        var cw = U.contrastRatio(cur, { r: 255, g: 255, b: 255 });
        var cb = U.contrastRatio(cur, { r: 0, g: 0, b: 0 });
        function wcagBadge(r) {
          if (r >= 7) return U.h('span', { class: 'badge ok' }, 'AAA');
          if (r >= 4.5) return U.h('span', { class: 'badge ok' }, 'AA');
          if (r >= 3) return U.h('span', { class: 'badge warn' }, 'AA 大字');
          return U.h('span', { class: 'badge err' }, '不足');
        }
        contrastBox.append(U.h('table', { class: 'tbl' },
          U.h('thead', {}, U.h('tr', {}, U.h('th', {}, '对比背景'), U.h('th', {}, '对比度'), U.h('th', {}, 'WCAG'))),
          U.h('tbody', {},
            U.h('tr', {}, U.h('td', {}, '白色文字'), U.h('td', { class: 'mono' }, cw.toFixed(2) + ':1'), U.h('td', {}, wcagBadge(cw))),
            U.h('tr', {}, U.h('td', {}, '黑色文字'), U.h('td', { class: 'mono' }, cb.toFixed(2) + ':1'), U.h('td', {}, wcagBadge(cb))))));
      }

      function fromText() {
        var c = U.parseColor(textInput.value);
        if (c) { cur = c; render(); }
      }
      picker.addEventListener('input', function () { cur = U.hexToRgb(picker.value); textInput.value = U.rgbToHex(cur); render(); });
      textInput.addEventListener('input', U.debounce(fromText, 250));

      palette.append(PALETTE.map(function (hex) {
        return U.h('div', {
          class: 'pal-dot', style: 'background:' + hex, title: hex,
          onclick: function () { cur = U.hexToRgb(hex); textInput.value = hex; render(); }
        });
      }));

      el.append(
        U.h('div', { class: 'panel' },
          U.h('div', { class: 'row' },
            U.h('div', { class: 'field' }, U.h('label', {}, '取色器'), picker),
            U.h('div', { class: 'field', style: 'flex:1' }, U.h('label', {}, 'HEX / RGB / HSL 均可粘贴'), textInput),
            U.h('div', { class: 'field' }, U.h('label', {}, '随机'),
              U.h('button', {
                class: 'btn ghost',
                onclick: function () {
                  var c = { r: Math.floor(Math.random() * 256), g: Math.floor(Math.random() * 256), b: Math.floor(Math.random() * 256) };
                  cur = c; textInput.value = U.rgbToHex(c); render();
                }
              }, '🎲'))),
          U.h('div', { style: 'margin-top:12px' }, swatch),
          U.h('div', { style: 'margin-top:12px' }, U.h('p', { class: 'panel-title' }, '常用色板'), palette)),
        U.h('div', { class: 'grid2' },
          U.h('div', { class: 'panel' }, U.h('p', { class: 'panel-title' }, '格式转换'), convList),
          U.h('div', { class: 'panel' }, U.h('p', { class: 'panel-title' }, '可读性对比（WCAG）'), contrastBox))
      );
      render();
    }
  });
})();
