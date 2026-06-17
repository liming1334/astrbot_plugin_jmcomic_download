# AstrBot JMComic Download Plugin

一个基于 AstrBot 的 JMComic 下载插件。

支持通过聊天指令查询作品信息，并下载漫画自动转换为 PDF 文件发送。

## 📖 介绍

本插件使用 `jmcomic` 作为下载核心，实现：

- 查询 JMComic 作品信息
- 下载漫画资源
- 自动转换 WebP 图片为 PDF
- 发送 PDF 文件
- 下载完成后自动清理缓存文件

适用于 AstrBot + QQ 等聊天平台环境。

---

## ✨ 功能

- ✅ JMComic 作品查询
- ✅ 漫画下载
- ✅ WebP 图片转换
- ✅ PDF 自动生成
- ✅ PDF 文件发送
- ✅ 下载缓存自动清理
- ✅ 防止多任务同时下载

---

## 💿 安装

将插件放入 AstrBot 插件目录：

```

data/plugins/

```

目录结构：

```

astrbot_plugin_jmcomic_download
│
├─ main.py
├─ config.yml
├─ requirements.txt
└─ README.md

````

安装依赖：

```bash
pip install -r requirements.txt
````

依赖：

```
jmcomic
img2pdf
Pillow
```

重启 AstrBot 即可加载插件。

---

## ⚙️ 配置

插件使用 `config.yml` 配置 jmcomic。

示例：

```yaml
client:
  domain:
    - https://www.cdnhjk.net
    - https://www.cdngwc.cc
    - https://www.cdngwc.net
    - https://www.cdngwc.club
    - https://www.cdnutc.me
```

下载目录默认位于：

```
astrbot_plugin_jmcomic_download/downloads
```

下载完成后会自动清理。

---

## 🎉 使用

### 指令表

| 指令        | 参数   | 功能         |
| --------- | ---- | ---------- |
| `/jmhelp` | 无    | 查看帮助       |
| `/jm`     | 作品ID | 查询作品信息     |
| `/jmd`    | 作品ID | 下载作品并发送PDF |

---

## 示例

查询：

```
/jm 350234
```

返回：

```
标题：董卓 上+下
作者：N/A
ID：350234
```

下载：

```
/jmd 350234
```

流程：

```
下载漫画
 ↓
转换PDF
 ↓
发送文件
 ↓
清理缓存
```

---

## 📂 文件结构

运行过程中：

```
downloads
│
├─作品图片缓存
│
└─作品ID.pdf
```

发送完成后自动删除。


---

## 🐛 已知问题

1. PDF大小取决于原漫画图片质量，部分作品可能较大。

2. 下载速度受 JMComic 服务器以及网络环境影响。

3. 部分聊天平台可能限制文件大小。

---

## License

本插件是受到一个QQ聊天记录的影响而开发

本插件由AI开发

注意：网络环境问题请自行解决
