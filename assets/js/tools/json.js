/* JSON 格式化 / 校验 / 压缩 */
(function () {
  'use strict';
  var D = globalThis.DevBox, U = globalThis.DevUtil;

  D.register({
    id: 'json',
    name: 'JSON 工具',
    icon: '🧾',
    category: 'data',
    desc: '格式化、压缩、校验 JSON，错误精确到行列',
    keywords: ['json', 'format', '格式化', '压缩', '校验', 'pretty'],
    render: function (el) {
      var input = U.h('textarea', { class: 'textarea', placeholder: '粘贴 JSON…\n{"name":"DevBox","stars":100,"tags":["dev","tools"]}' });
      var output = U.h('div', { class: 'out' }, U.h('span', { class: 'placeholder' }, '输出显示在这里'));
      var errBox = U.h('div', {});
      var indentSel = U.h('select', { class: 'select' },
        U.h('option', { value: '2' }, '2 空格缩进'),
        U.h('option', { value: '4' }, '4 空格缩进'),
        U.h('option', { value: 'tab' }, 'Tab 缩进'));
      var escChk = U.h('input', { type: 'checkbox' });

      function indentArg() {
        return indentSel.value === 'tab' ? '\t' : Number(indentSel.value);
      }

      function locate(src, pos) {
        var before = src.slice(0, pos);
        var line = before.split('\n').length;
        var col = pos - before.lastIndexOf('\n');
        return '第 ' + line + ' 行，第 ' + col + ' 列';
      }

      function run(mode) {
        errBox.innerHTML = '';
        var src = input.value.trim();
        if (!src) { output.innerHTML = ''; output.append(U.h('span', { class: 'placeholder' }, '请先输入 JSON')); return; }
        var data;
        try {
          data = JSON.parse(src);
        } catch (e) {
          var m = /position (\d+)/.exec(e.message);
          var detail = m ? locate(src, +m[1]) : '';
          errBox.append(U.h('div', { class: 'err-text' }, '✗ 解析失败：' + e.message + (detail ? '（' + detail + '）' : '')));
          return;
        }
        var text;
        if (mode === 'min') text = JSON.stringify(data);
        else text = JSON.stringify(data, null, indentArg());
        if (escChk.checked) text = text.replace(/[\u0080-\uffff]/g, function (ch) {
          return '\\u' + ch.charCodeAt(0).toString(16).padStart(4, '0');
        });
        output.textContent = text;
        D.toast(mode === 'min' ? '✓ 已压缩' : '✓ 已格式化');
      }

      el.append(
        U.h('div', { class: 'panel' },
          U.h('p', { class: 'panel-title' }, '输入'),
          input,
          U.h('div', { class: 'row', style: 'margin-top:10px' },
            U.h('button', { class: 'btn', onclick: function () { run('fmt'); } }, '✨ 格式化'),
            U.h('button', { class: 'btn ghost', onclick: function () { run('min'); } }, '压缩'),
            U.h('button', { class: 'btn ghost', onclick: function () { input.value = ''; errBox.innerHTML = ''; output.textContent = ''; run('fmt'); } }, '清空'),
            U.h('span', { class: 'spacer' }),
            U.h('label', { class: 'check' }, indentSel, '缩进'),
            U.h('label', { class: 'check' }, escChk, '非 ASCII 转义')
          ),
          errBox
        ),
        U.h('div', { class: 'panel' },
          U.h('p', { class: 'panel-title' }, '输出'),
          output,
          U.h('div', { class: 'row', style: 'margin-top:10px' },
            D.copyBtn(function () { return output.textContent; }),
            U.h('button', {
              class: 'btn ghost sm',
              onclick: function () {
                try { input.value = JSON.stringify(JSON.parse(output.textContent), null, indentArg()); D.toast('✓ 已回填到输入框'); }
                catch (e) { D.toast('输出不是合法 JSON', 'err'); }
              }
            }, '↩ 回填输入框')))
      );

      var sample = '{"name":"DevBox","version":"1.0.0","tools":17,"tags":["dev","tools"],"author":{"name":"you","since":2026}}';
      input.value = sample;
      run('fmt');
    }
  });
})();
