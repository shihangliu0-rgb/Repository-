/* 二维码生成（qrcode-generator，UTF-8 支持中文） */
(function () {
  'use strict';
  var D = globalThis.DevBox, U = globalThis.DevUtil;

  D.register({
    id: 'qrcode',
    name: '二维码生成',
    icon: '🧩',
    category: 'gen',
    desc: '文本 / 链接转二维码，支持中文，可下载 SVG / PNG',
    keywords: ['qrcode', 'qr', '二维码', '条码', '扫码', '生成'],
    render: function (el) {
      var text = U.h('textarea', { class: 'textarea small', placeholder: '输入文本或链接，支持中文…' });
      var sizeSel = U.h('select', { class: 'select' },
        [3, 4, 6, 8, 10].map(function (s) {
          var o = U.h('option', { value: String(s) }, '单元格 ' + s + 'px');
          if (s === 6) o.selected = true;
          return o;
        }));
      var ecSel = U.h('select', { class: 'select' },
        ['L', 'M', 'Q', 'H'].map(function (s) {
          var o = U.h('option', { value: s }, '纠错 ' + s);
          if (s === 'M') o.selected = true;
          return o;
        }));
      var view = U.h('div', { class: 'qr-wrap' }, U.h('span', { class: 'placeholder muted' }, '二维码显示在这里'));
      var errBox = U.h('div', {});
      var downloadRow = U.h('div', { class: 'row' });
      var lastQr = null, lastSvg = '';

      function render() {
        errBox.innerHTML = ''; downloadRow.innerHTML = '';
        var v = text.value.trim();
        if (!v) { view.innerHTML = ''; view.append(U.h('span', { class: 'placeholder muted' }, '二维码显示在这里')); return; }
        try {
          var qr = globalThis.qrcode(0, ecSel.value);
          qr.addData(v);
          qr.make();
          lastQr = qr;
          lastSvg = qr.createSvgTag({ cellSize: Number(sizeSel.value), margin: 2, scalable: true });
          view.innerHTML = lastSvg;
        } catch (e) {
          view.innerHTML = '';
          view.append(U.h('span', { class: 'err-text' }, '✗ 生成失败：' + e.message));
          lastQr = null;
          return;
        }
        /* 下载按钮 */
        var svgBlob = new Blob([lastSvg], { type: 'image/svg+xml' });
        downloadRow.append(U.h('a', {
          class: 'btn ghost sm', download: 'qrcode.svg',
          href: URL.createObjectURL(svgBlob)
        }, '⬇ SVG'));
        if (lastQr) {
          var n = lastQr.getModuleCount();
          var scale = Number(sizeSel.value), margin = 4;
          var canvas = document.createElement('canvas');
          canvas.width = canvas.height = (n + margin * 2) * scale;
          var ctx = canvas.getContext('2d');
          ctx.fillStyle = '#fff';
          ctx.fillRect(0, 0, canvas.width, canvas.height);
          ctx.fillStyle = '#000';
          for (var r = 0; r < n; r++) {
            for (var c = 0; c < n; c++) {
              if (lastQr.isDark(r, c)) {
                ctx.fillRect((c + margin) * scale, (r + margin) * scale, scale, scale);
              }
            }
          }
          downloadRow.append(U.h('button', { class: 'btn ghost sm', onclick: function () {
            canvas.toBlob(function (blob) {
              var a = document.createElement('a');
              a.href = URL.createObjectURL(blob);
              a.download = 'qrcode.png';
              a.click();
              setTimeout(function () { URL.revokeObjectURL(a.href); }, 3000);
            });
          } }, '⬇ PNG'));
        }
      }

      text.addEventListener('input', U.debounce(render, 250));
      sizeSel.addEventListener('change', render);
      ecSel.addEventListener('change', render);

      text.value = 'https://example.com你好，DevBox！';
      render();

      el.append(
        U.h('div', { class: 'grid2' },
          U.h('div', { class: 'panel' },
            U.h('p', { class: 'panel-title' }, '内容'),
            text,
            U.h('div', { class: 'row', style: 'margin-top:10px' },
              U.h('label', { class: 'check' }, '尺寸 ', sizeSel),
              U.h('label', { class: 'check' }, '容错 ', ecSel)),
            errBox,
            U.h('p', { class: 'muted', style: 'margin:10px 0 0;font-size:12.5px' },
              '容错级别越高越耐污损，但码点越密。生成完全在本地完成。')),
          U.h('div', { class: 'panel' },
            U.h('p', { class: 'panel-title' }, '预览'),
            view,
            U.h('div', { class: 'row', style: 'margin-top:10px' }, downloadRow)))
      );
    }
  });
})();
