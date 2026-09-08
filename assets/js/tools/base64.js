/* Base64 编解码（文本 UTF-8 安全 + 文件转 DataURL） */
(function () {
  'use strict';
  var D = globalThis.DevBox, U = globalThis.DevUtil;

  D.register({
    id: 'base64',
    name: 'Base64 编解码',
    icon: '🔤',
    category: 'encode',
    desc: '文本与 Base64 互转（中文安全），支持 URL-Safe 与文件',
    keywords: ['base64', 'encode', 'decode', '编码', '解码', 'dataurl'],
    render: function (el) {
      var input = U.h('textarea', { class: 'textarea', placeholder: '输入要编码/解码的文本…' });
      var output = U.h('div', { class: 'out' }, U.h('span', { class: 'placeholder' }, '输出显示在这里'));
      var modeEnc = U.h('input', { type: 'radio', name: 'b64mode', checked: true });
      var modeDec = U.h('input', { type: 'radio', name: 'b64mode' });
      var urlSafe = U.h('input', { type: 'checkbox' });

      function run() {
        var src = input.value;
        if (!src.trim()) { output.innerHTML = ''; output.append(U.h('span', { class: 'placeholder' }, '输出显示在这里')); return; }
        try {
          output.textContent = modeEnc.checked ? U.b64EncodeText(src, urlSafe.checked) : U.b64DecodeText(src);
        } catch (e) {
          output.innerHTML = '';
          output.append(U.h('span', { class: 'err-text' }, '✗ ' + e.message));
        }
      }
      input.addEventListener('input', U.debounce(run, 200));
      [modeEnc, modeDec, urlSafe].forEach(function (c) { c.addEventListener('change', run); });

      /* --- 文件区 --- */
      var fileOut = U.h('div', { class: 'out' }, U.h('span', { class: 'placeholder' }, '选择文件后显示 DataURL'));
      var preview = U.h('div', {});
      var lastDataUrl = '';
      function handleFile(file) {
        if (!file) return;
        var reader = new FileReader();
        reader.onload = function () {
          lastDataUrl = String(reader.result);
          fileOut.textContent = lastDataUrl;
          preview.innerHTML = '';
          if (/^image\//.test(file.type)) preview.append(U.h('img', { src: lastDataUrl, style: 'max-width:160px;max-height:160px;border-radius:8px;border:1px solid var(--border)' }));
          D.toast('✓ 已读取 ' + U.formatBytes(file.size));
        };
        reader.readAsDataURL(file);
      }
      var fileInput = U.h('input', { type: 'file', style: 'display:none', onchange: function () { handleFile(this.files[0]); } });
      var zone = U.h('div', { class: 'dropzone', onclick: function () { fileInput.click(); } },
        U.h('span', { class: 'big' }, '📁'), '点击选择文件，或拖拽到此处');
      zone.addEventListener('dragover', function (e) { e.preventDefault(); zone.classList.add('drag'); });
      zone.addEventListener('dragleave', function () { zone.classList.remove('drag'); });
      zone.addEventListener('drop', function (e) {
        e.preventDefault(); zone.classList.remove('drag');
        handleFile(e.dataTransfer.files[0]);
      });

      input.value = '你好，DevBox！Hello DevBox!';
      run();

      el.append(
        U.h('div', { class: 'panel' },
          U.h('p', { class: 'panel-title' }, '文本'),
          input,
          U.h('div', { class: 'row', style: 'margin-top:10px' },
            U.h('label', { class: 'check' }, modeEnc, '编码'),
            U.h('label', { class: 'check' }, modeDec, '解码'),
            U.h('label', { class: 'check' }, urlSafe, 'URL-Safe（-_ 不含 =）'),
            U.h('span', { class: 'spacer' }),
            U.h('button', { class: 'btn ghost sm', onclick: function () { var t = input.value; input.value = output.textContent; output.textContent = t; run(); } }, '⇄ 交换'))),
        U.h('div', { class: 'panel' }, U.h('p', { class: 'panel-title' }, '输出'), output),
        U.h('div', { class: 'panel' },
          U.h('p', { class: 'panel-title' }, '文件 → DataURL'),
          zone, fileInput,
          U.h('div', { style: 'margin-top:10px' }, preview),
          U.h('div', { class: 'out', style: 'margin-top:10px;max-height:160px' },
            U.h('span', { class: 'placeholder' }, ''), fileOut,
            D.copyBtn(function () { return lastDataUrl; })))
      );
    }
  });
})();
