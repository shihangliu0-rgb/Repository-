/* 哈希摘要：MD5 / SHA-1 / SHA-256 / SHA-384 / SHA-512 / CRC32 */
(function () {
  'use strict';
  var D = globalThis.DevBox, U = globalThis.DevUtil;

  D.register({
    id: 'hash',
    name: '哈希摘要',
    icon: '#️⃣',
    category: 'encode',
    desc: 'MD5、SHA 系列、CRC32，支持文本与文件',
    keywords: ['hash', 'md5', 'sha1', 'sha256', 'sha512', 'crc32', '摘要', '校验', 'checksum'],
    render: function (el) {
      var mode = { value: 'text' };
      var input = U.h('textarea', { class: 'textarea', placeholder: '输入文本…' });
      var upperChk = U.h('input', { type: 'checkbox' });
      var resultsEl = U.h('div', {});
      var fileLabel = U.h('span', {}, '未选择文件');
      var fileInput = U.h('input', { type: 'file', style: 'display:none' });

      function row(name, value) {
        if (!value) return U.h('tr', {},
          U.h('td', {}, name), U.h('td', { class: 'mono muted' }, '计算中…'), U.h('td', {}));
        return U.h('tr', {},
          U.h('td', {}, U.h('span', { class: 'badge' }, name)),
          U.h('td', { class: 'mono' }, value),
          U.h('td', { style: 'width:60px' }, D.copyBtn(value, '复制')));
      }

      function renderResults(list) {
        resultsEl.innerHTML = '';
        var tbl = U.h('table', { class: 'tbl' },
          U.h('thead', {}, U.h('tr', {}, U.h('th', {}, '算法'), U.h('th', {}, '摘要值'), U.h('th', {}))),
          U.h('tbody', {}, list.map(row)));
        resultsEl.append(U.h('div', { class: 'panel' },
          U.h('p', { class: 'panel-title' }, '结果'),
          tbl,
          U.h('label', { class: 'check', style: 'margin-top:10px' }, upperChk, '显示大写')));
        applyCase();
      }
      function applyCase() {
        resultsEl.querySelectorAll('td.mono').forEach(function (td) {
          if (td.textContent && td.textContent !== '计算中…') {
            td.textContent = upperChk.checked ? td.textContent.toUpperCase() : td.textContent.toLowerCase();
          }
        });
      }
      upperChk.addEventListener('change', applyCase);

      async function compute(data) {
        var list = [
          { name: 'MD5', value: U.md5(data) },
          { name: 'CRC32', value: U.crc32(data) },
          { name: 'SHA-1', value: null }, { name: 'SHA-256', value: null },
          { name: 'SHA-384', value: null }, { name: 'SHA-512', value: null }
        ];
        renderResults(list);
        var algos = ['SHA-1', 'SHA-256', 'SHA-384', 'SHA-512'];
        for (var i = 0; i < algos.length; i++) {
          try {
            var hex = await U.shaDigest(algos[i], data);
            list.find(function (r) { return r.name === algos[i]; }).value = hex;
          } catch (e) {
            list.find(function (r) { return r.name === algos[i]; }).value = '不可用（需要 HTTPS 环境）';
          }
          renderResults(list);
        }
      }

      function runText() {
        if (!input.value) { resultsEl.innerHTML = ''; return; }
        compute(input.value);
      }
      function runFile(file) {
        if (!file) return;
        fileLabel.textContent = file.name + '（' + U.formatBytes(file.size) + '）';
        var reader = new FileReader();
        reader.onload = function () { compute(new Uint8Array(reader.result)); };
        reader.readAsArrayBuffer(file);
      }
      fileInput.addEventListener('change', function () { runFile(this.files[0]); });

      input.addEventListener('input', U.debounce(runText, 300));
      input.value = 'hello world';
      runText();

      var tabText = U.h('button', { class: 'btn sm', onclick: function () { mode.value = 'text'; syncTabs(); } }, '文本');
      var tabFile = U.h('button', { class: 'btn ghost sm', onclick: function () { mode.value = 'file'; syncTabs(); fileInput.click(); } }, '文件');
      function syncTabs() {
        tabText.className = mode.value === 'text' ? 'btn sm' : 'btn ghost sm';
        tabFile.className = mode.value === 'file' ? 'btn sm' : 'btn ghost sm';
      }

      el.append(
        U.h('div', { class: 'panel' },
          U.h('p', { class: 'panel-title' }, '输入'),
          U.h('div', { class: 'row tight', style: 'margin-bottom:10px' }, tabText, tabFile, U.h('span', { class: 'muted' }, fileLabel)),
          input,
          U.h('div', { class: 'row', style: 'margin-top:10px' },
            U.h('button', { class: 'btn', onclick: runText }, '计算'),
            U.h('button', { class: 'btn ghost', onclick: function () { fileInput.click(); } }, '📁 选择文件计算'))),
        resultsEl
      );
    }
  });
})();
