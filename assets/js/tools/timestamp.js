/* 时间戳转换：当前时间实时 + 双向转换 */
(function () {
  'use strict';
  var D = globalThis.DevBox, U = globalThis.DevUtil;

  D.register({
    id: 'timestamp',
    name: '时间戳转换',
    icon: '⏱️',
    category: 'convert',
    desc: 'Unix 时间戳与日期互转，自动识别秒/毫秒',
    keywords: ['timestamp', 'time', 'date', '时间', '时间戳', 'unix', '日期'],
    render: function (el) {
      /* --- 当前时间 --- */
      var nowLocal = U.h('div', { class: 'v', style: 'font-size:20px;font-weight:700' }, '-');
      var nowSec = U.h('span', { class: 'mono' }, '-');
      var nowMs = U.h('span', { class: 'mono' }, '-');
      var timer = setInterval(tick, 1000);
      function tick() {
        var d = new Date();
        nowLocal.textContent = U.fmtDateTime(d) + ' ' + U.fmtWeek(d);
        nowSec.textContent = String(Math.floor(d.getTime() / 1000));
        nowMs.textContent = String(d.getTime());
      }
      tick();

      /* --- 解析输入 --- */
      var parseInput = U.h('input', { class: 'input', style: 'width:100%;font-family:var(--mono)', placeholder: '时间戳（1700000000 / 1700000000000）或日期（2026-01-01 08:00:00）' });
      var parseOut = U.h('div', {});
      function renderParse() {
        parseOut.innerHTML = '';
        var v = parseInput.value.trim();
        if (!v) return;
        var d = U.parseTimestamp(v);
        if (!d) {
          parseOut.append(U.h('div', { class: 'err-text' }, '✗ 无法识别的日期/时间戳'));
          return;
        }
        var rows = [
          ['秒', String(Math.floor(d.getTime() / 1000))],
          ['毫秒', String(d.getTime())],
          ['本地时间', U.fmtDateTime(d) + ' ' + U.fmtWeek(d)],
          ['UTC', d.toUTCString()],
          ['ISO 8601', d.toISOString()],
          ['相对时间', U.relativeTime(d)]
        ];
        parseOut.append(U.h('div', { class: 'kv' }, rows.map(function (r) {
          return [U.h('span', { class: 'k' }, r[0]), U.h('span', { class: 'v' }, r[1], D.copyBtn(r[1], '📋'))];
        })));
      }
      parseInput.addEventListener('input', U.debounce(renderParse, 200));

      /* --- 日期 → 时间戳 --- */
      var dtInput = U.h('input', { class: 'input', type: 'datetime-local', step: '1' });
      var tsOut = U.h('div', { class: 'out' }, U.h('span', { class: 'placeholder' }, '选择日期后显示'));
      function renderRev() {
        if (!dtInput.value) return;
        var d = new Date(dtInput.value);
        if (isNaN(d.getTime())) return;
        tsOut.textContent = '秒：' + Math.floor(d.getTime() / 1000) + '\n毫秒：' + d.getTime();
      }
      dtInput.addEventListener('input', renderRev);

      var init = new Date();
      dtInput.value = init.getFullYear() + '-' + U.pad2(init.getMonth() + 1) + '-' + U.pad2(init.getDate()) +
        'T' + U.pad2(init.getHours()) + ':' + U.pad2(init.getMinutes()) + ':' + U.pad2(init.getSeconds());
      renderRev();
      parseInput.value = String(Math.floor(Date.now() / 1000));
      renderParse();

      el.append(
        U.h('div', { class: 'panel' },
          U.h('p', { class: 'panel-title' }, '当前时间'),
          nowLocal,
          U.h('div', { class: 'row', style: 'margin-top:8px' },
            U.h('span', { class: 'badge accent' }, '秒'), nowSec, D.copyBtn(function () { return nowSec.textContent; }, '📋'),
            U.h('span', { class: 'badge accent' }, '毫秒'), nowMs, D.copyBtn(function () { return nowMs.textContent; }, '📋'))),
        U.h('div', { class: 'panel' },
          U.h('p', { class: 'panel-title' }, '时间戳 / 日期 → 日期时间'),
          parseInput, U.h('div', { style: 'margin-top:12px' }, parseOut)),
        U.h('div', { class: 'panel' },
          U.h('p', { class: 'panel-title' }, '日期选择 → 时间戳'),
          dtInput, U.h('div', { style: 'margin-top:12px' }, tsOut))
      );

      return function () { clearInterval(timer); };
    }
  });
})();
