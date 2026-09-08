/* 单位换算：长度/重量/温度/数据/面积/速度/时间 */
(function () {
  'use strict';
  var D = globalThis.DevBox, U = globalThis.DevUtil;

  D.register({
    id: 'units',
    name: '单位换算',
    icon: '📐',
    category: 'convert',
    desc: '长度、重量、温度、数据大小、面积、速度、时间',
    keywords: ['unit', 'convert', '单位', '换算', '长度', '重量', '温度', '存储', '面积', '速度'],
    render: function (el) {
      var tabsRow = U.h('div', { class: 'row tight' });
      var valueInput = U.h('input', { class: 'input', style: 'width:100%;font-family:var(--mono)', value: '1' });
      var fromSel = U.h('select', { class: 'select', style: 'flex:1;min-width:150px' });
      var toSel = U.h('select', { class: 'select', style: 'flex:1;min-width:150px' });
      var resultBig = U.h('div', { style: 'font-size:22px;font-weight:700;font-family:var(--mono);word-break:break-all' }, '-');
      var tableWrap = U.h('div', {});
      var cur = U.UNIT_GROUPS[0];

      function fillSelect(sel, group, exceptId) {
        sel.innerHTML = '';
        group.units.forEach(function (u) {
          var o = U.h('option', { value: u.id }, u.name);
          if (u.id === exceptId) o.selected = true;
          sel.appendChild(o);
        });
      }
      function fillTabs() {
        tabsRow.innerHTML = '';
        U.UNIT_GROUPS.forEach(function (g) {
          var b = U.h('button', {
            class: g === cur ? 'btn sm' : 'btn ghost sm',
            onclick: function () { cur = g; fillTabs(); fillSelect(fromSel, g, g.units[0].id); fillSelect(toSel, g, g.units[1].id); render(); }
          }, g.name);
          tabsRow.appendChild(b);
        });
      }

      function unitName(group, id) {
        var u = group.units.find(function (x) { return x.id === id; });
        return u ? u.name : id;
      }

      function render() {
        tableWrap.innerHTML = '';
        var v = parseFloat(valueInput.value);
        if (isNaN(v)) { resultBig.textContent = '请输入数字'; return; }
        var out;
        try { out = U.convertUnit(v, fromSel.value, toSel.value, cur); }
        catch (e) { resultBig.textContent = e.message; return; }
        resultBig.textContent = U.fmtNum(v) + ' ' + unitName(cur, fromSel.value) + ' = ' + U.fmtNum(out) + ' ' + unitName(cur, toSel.value);
        var rows = cur.units.map(function (u) {
          var val = U.convertUnit(v, fromSel.value, u.id, cur);
          return U.h('tr', {},
            U.h('td', {}, u.name),
            U.h('td', { class: 'mono' }, U.fmtNum(val)),
            U.h('td', { style: 'width:56px' }, D.copyBtn(U.fmtNum(val), '📋')));
        });
        tableWrap.append(U.h('table', { class: 'tbl' },
          U.h('thead', {}, U.h('tr', {}, U.h('th', {}, '单位'), U.h('th', {}, '换算结果'), U.h('th', {}))),
          U.h('tbody', {}, rows)));
      }

      valueInput.addEventListener('input', U.debounce(render, 150));
      fromSel.addEventListener('change', render);
      toSel.addEventListener('change', render);

      fillTabs();
      fillSelect(fromSel, cur, 'm');
      fillSelect(toSel, cur, 'km');
      render();

      el.append(
        U.h('div', { class: 'panel' },
          U.h('p', { class: 'panel-title' }, '类别'),
          tabsRow,
          U.h('div', { class: 'row', style: 'margin-top:12px' },
            U.h('div', { class: 'field', style: 'flex:1;min-width:130px' }, U.h('label', {}, '数值'), valueInput),
            U.h('button', {
              class: 'btn ghost', title: '交换单位',
              onclick: function () { var a = fromSel.value; fromSel.value = toSel.value; toSel.value = a; render(); }
            }, '⇄'),
            U.h('div', { class: 'field', style: 'flex:1;min-width:130px' }, U.h('label', {}, '从'), fromSel),
            U.h('div', { class: 'field', style: 'flex:1;min-width:130px' }, U.h('label', {}, '到'), toSel)),
          U.h('div', { style: 'margin-top:14px' }, resultBig)),
        U.h('div', { class: 'panel' },
          U.h('p', { class: 'panel-title' }, '全部单位'),
          tableWrap)
      );
    }
  });
})();
