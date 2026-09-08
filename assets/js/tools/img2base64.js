/* 图片转 Base64：预览 + DataURL + HTML/CSS 代码片段 */
(function () {
  'use strict';
  var D = globalThis.DevBox, U = globalThis.DevUtil;

  D.register({
    id: 'img2base64',
    name: '图片转 Base64',
    icon: '🖼️',
    category: 'encode',
    desc: '拖入图片生成 DataURL，附 HTML / CSS 可用片段',
    keywords: ['image', 'base64', 'dataurl', '图片', '转码', '内嵌'],
    render: function (el) {
      var previewBox = U.h('div', { style: 'min-height:80px;display:grid;place-items:center' },
        U.h('span', { class: 'muted' }, '尚未选择图片'));
      var metaRow = U.h('div', { class: 'row tight' }, U.h('span', { class: 'badge' }, '等待文件'));
      var dataOut = U.h('div', { class: 'out', style: 'max-height:140px' }, U.h('span', { class: 'placeholder' }, 'DataURL 显示在这里'));
      var htmlOut = U.h('div', { class: 'out' }, U.h('span', { class: 'placeholder' }, 'HTML 片段'));
      var cssOut = U.h('div', { class: 'out' }, U.h('span', { class: 'placeholder' }, 'CSS 片段'));
      var lastDataUrl = '';
      var fileInput = U.h('input', { type: 'file', accept: 'image/*', style: 'display:none', onchange: function () { handle(this.files[0]); } });

      function handle(file) {
        if (!file) return;
        if (!/^image\//.test(file.type)) { D.toast('请选择图片文件', 'err'); return; }
        var reader = new FileReader();
        reader.onload = function () {
          lastDataUrl = String(reader.result);
          previewBox.innerHTML = '';
          previewBox.append(U.h('img', { src: lastDataUrl, style: 'max-width:100%;max-height:220px;border-radius:8px;border:1px solid var(--border)' }));
          var b64Part = lastDataUrl.split(',')[1] || '';
          metaRow.innerHTML = '';
          metaRow.append(
            U.h('span', { class: 'badge accent' }, file.type),
            U.h('span', { class: 'badge' }, '原始 ' + U.formatBytes(file.size)),
            U.h('span', { class: 'badge' }, 'Base64 ' + U.formatBytes(b64Part.length)),
            U.h('span', { class: 'badge ' + (b64Part.length > file.size * 1.4 ? 'warn' : 'ok') },
              '膨胀约 ' + (b64Part.length / Math.max(1, file.size) * 100).toFixed(0) + '%'));
          dataOut.textContent = lastDataUrl;
          htmlOut.textContent = '<img src="' + lastDataUrl.slice(0, 60) + '…" alt="">';
          cssOut.textContent = 'background-image: url("' + lastDataUrl.slice(0, 60) + '…");';
          D.toast('✓ 转换完成');
        };
        reader.readAsDataURL(file);
      }

      var zone = U.h('div', { class: 'dropzone', onclick: function () { fileInput.click(); } },
        U.h('span', { class: 'big' }, '🖼️'), '点击选择图片，或拖拽到此处（PNG / JPG / SVG / GIF / WebP）');
      zone.addEventListener('dragover', function (e) { e.preventDefault(); zone.classList.add('drag'); });
      zone.addEventListener('dragleave', function () { zone.classList.remove('drag'); });
      zone.addEventListener('drop', function (e) {
        e.preventDefault(); zone.classList.remove('drag');
        handle(e.dataTransfer.files[0]);
      });

      el.append(
        U.h('div', { class: 'panel' }, zone, fileInput),
        U.h('div', { class: 'panel' },
          U.h('p', { class: 'panel-title' }, '预览'),
          previewBox,
          U.h('div', { style: 'margin-top:10px' }, metaRow)),
        U.h('div', { class: 'panel' },
          U.h('p', { class: 'panel-title' }, 'Data URL ', D.copyBtn(function () { return lastDataUrl; })),
          dataOut),
        U.h('div', { class: 'grid2' },
          U.h('div', { class: 'panel' },
            U.h('p', { class: 'panel-title' }, 'HTML 片段 ', D.copyBtn(function () { return htmlOut.textContent; })),
            htmlOut),
          U.h('div', { class: 'panel' },
            U.h('p', { class: 'panel-title' }, 'CSS 片段 ', D.copyBtn(function () { return cssOut.textContent; })),
            cssOut)),
        U.h('p', { class: 'muted' }, '💡 小图（图标、头像）内嵌 Base64 可减少请求；大图会让体积膨胀约 33%，慎用。')
      );
    }
  });
})();
