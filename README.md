# 🧰 DevBox · 开发者工具箱

> **17 个高频开发工具 · 纯前端本地运行 · 数据不出浏览器 · 离线可用**

一个零构建、零依赖（仅两处 MIT 协议的 vendor 库）的浏览器工具箱。克隆下来起个静态服务就能用，
所有计算（包括哈希、二维码）全部在你的浏览器里完成，**没有任何网络请求**，适合处理敏感内容。

![工具数](https://img.shields.io/badge/工具-17个-4f6ef7) ![测试](https://img.shields.io/badge/测试-24%2F24通过-16a34a) ![协议](https://img.shields.io/badge/协议-MIT-blue) ![构建](https://img.shields.io/badge/构建-零依赖-success)

---

## 🚀 快速开始

```bash
# 方式一：Python（推荐，无需安装任何依赖）
python3 -m http.server 8000
# 打开 http://localhost:8000

# 方式二：npm
npm start

# 方式三：任何静态服务器（nginx / caddy / VS Code Live Server 均可）
# 甚至可以直接双击 index.html 用 file:// 打开
```

## 🧩 工具一览（17 个）

| 分类 | 工具 | 说明 |
|------|------|------|
| 🔐 编码/加密 | **Base64 编解码** | 文本互转（中文安全）、URL-Safe、文件转 DataURL |
| | **URL 编解码** | `encodeURIComponent` / `encodeURI` 双模式 |
| | **JWT 解码** | Header/Payload 解析，自动识别过期时间 |
| | **哈希摘要** | MD5 / SHA-1 / 256 / 384 / 512 / CRC32，支持文件，结果与 OpenSSL 对拍一致 |
| | **图片转 Base64** | 拖拽生成 DataURL + HTML/CSS 片段 + 体积膨胀提示 |
| 📊 数据格式 | **JSON 工具** | 格式化/压缩/校验，错误精确到行列，非 ASCII 转义 |
| | **Markdown 预览** | 实时渲染（marked），一键复制 HTML |
| 🧮 转换计算 | **时间戳转换** | 秒/毫秒自动识别，双向转换，实时时钟，相对时间 |
| | **进制转换** | 2~36 进制，BigInt 精确无精度丢失，字节视图 |
| | **单位换算** | 长度/重量/温度/数据/面积/速度/时间（含斤、KiB 等） |
| | **颜色工具** | HEX/RGB/HSL 互转、WCAG 对比度检查、随机色板 |
| 📝 文本处理 | **正则测试** | 实时匹配高亮、捕获组、常用正则速查 |
| | **文本差异** | 行级 LCS 对比，git diff 风格渲染 |
| | **文本处理** | 驼峰/下划线互转、去重排序、大小写、字数统计 |
| ✨ 生成器 | **UUID 生成** | 批量 v4，大写/去连字符/花括号 |
| | **密码生成** | 自定义字符集，熵值强度评估，排除易混淆字符 |
| | **二维码生成** | 支持中文（UTF-8），可下载 SVG / PNG |

### 亮点

- **隐私安全**：纯客户端计算，处理 token、密钥、内网数据不经过任何服务器
- **离线可用**：除首次打开外不依赖网络，可部署到内网
- **键盘友好**：`/` 快速聚焦搜索，暗色模式跟随系统，手动切换自动记忆
- **最近使用**：首页与侧边栏记忆你的常用工具

## ✅ 质量保障

核心算法全部与权威实现**对拍测试**（`npm test`，Node 内置 test runner）：

- MD5 / SHA 系列 ↔ `node:crypto`（OpenSSL），覆盖空串、长度边界 55/56/57/63/64/65…、二进制数据
- CRC32 ↔ `node:zlib`，含随机二进制
- Base64 ↔ `Buffer`，含中文、emoji、二进制、URL-Safe、缺失 padding
- 其余：时间解析、BigInt 进制（2~36 全进制回转）、颜色往返、LCS diff、单位换算、JWT、密码策略等 24 组用例

## 📁 项目结构

```
├── index.html              # 入口（按序加载脚本，无打包）
├── assets/
│   ├── css/style.css       # 设计系统（明暗双主题、响应式）
│   ├── js/
│   │   ├── core.js         # 工具注册中心 DevBox.register()
│   │   ├── utils.js        # 纯逻辑层（无 DOM，可被 Node 测试）
│   │   ├── app.js          # 外壳：路由/侧边栏/搜索/主题/Toast
│   │   └── tools/*.js      # 17 个工具，一个工具一个文件
│   └── vendor/             # qrcode-generator、marked（均为 MIT）
├── tests/utils.test.mjs    # 自动化测试（npm test）
├── package.json            # 仅提供 test/start 脚本，无依赖
└── LICENSE                 # MIT
```

## 🔧 如何新增一个工具（20 行以内）

新建 `assets/js/tools/mytool.js`，在 `index.html` 加一行 `<script>` 即可：

```js
(function () {
  'use strict';
  var D = globalThis.DevBox, U = globalThis.DevUtil;

  D.register({
    id: 'mytool',                      // 路由 #/mytool
    name: '我的工具',
    icon: '🛠️',
    category: 'text',                  // encode / data / convert / text / gen
    desc: '一句话描述',
    keywords: ['搜索', '关键词'],
    render: function (el) {            // el 是工具页容器
      el.append(U.h('div', { class: 'panel' },
        U.h('p', { class: 'panel-title' }, '示例'),
        U.h('button', {
          class: 'btn',
          onclick: function () { D.toast('你好！'); }
        }, '点我')));
      // 可返回清理函数：路由切换时自动调用（如 clearInterval）
    }
  });
})();
```

无需注册路由、无需写导航、无需动 CSS——框架自动生成侧边栏、首页卡片、搜索索引与最近使用。

## 🛠️ 技术选型

- **无框架、无构建**：原生 ES5+ JS，十年后打开依然能跑
- **crypto.subtle**：SHA 系列；MD5/CRC32 为内置纯 JS 实现（SubtleCrypto 不提供）
- **BigInt**：进制转换对超过 2^53 的整数依然精确
- **vendored 依赖**：仅 `qrcode-generator@1.4.4` 与 `marked@12.0.2`，均为 MIT 协议

---

MIT License · Copyright (c) 2026 shihangliu0-rgb
