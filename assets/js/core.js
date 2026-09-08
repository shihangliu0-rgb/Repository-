/* ============================================================
 * DevBox · core.js
 * 工具注册中心 —— 所有工具通过 DevBox.register({...}) 挂载
 * 工具对象字段：
 *   id        唯一 ID（路由 #/id）
 *   name      名称
 *   icon      图标（emoji）
 *   desc      一句话描述
 *   keywords  搜索关键词数组
 *   category  分类 id
 *   render(el) 渲染函数，可返回清理函数（路由切换时调用）
 * ============================================================ */
(function (global) {
  'use strict';

  var tools = [];

  var categories = [
    { id: 'encode',  name: '编码 / 加密', icon: '🔐' },
    { id: 'data',    name: '数据格式',    icon: '📊' },
    { id: 'convert', name: '转换计算',    icon: '🧮' },
    { id: 'text',    name: '文本处理',    icon: '📝' },
    { id: 'gen',     name: '生成器',      icon: '✨' }
  ];

  global.DevBox = {
    version: '1.0.0',
    home: '#/',
    tools: tools,
    categories: categories,

    /** 注册一个工具 */
    register: function (tool) {
      if (!tool || !tool.id) throw new Error('DevBox.register: 缺少 id');
      if (tools.some(function (t) { return t.id === tool.id; })) {
        throw new Error('DevBox.register: 工具 id 重复 -> ' + tool.id);
      }
      tools.push(tool);
    },

    getTool: function (id) {
      for (var i = 0; i < tools.length; i++) if (tools[i].id === id) return tools[i];
      return null;
    },

    categoryOf: function (id) {
      for (var i = 0; i < categories.length; i++) if (categories[i].id === id) return categories[i];
      return { id: id, name: '其他', icon: '📦' };
    },

    /** 由 app.js 接管 */
    toast: function () {},
    copyBtn: function () {}
  };
})(globalThis);
