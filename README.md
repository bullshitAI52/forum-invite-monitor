# t66y invite watch

本项目的主执行环境是 Muse：由 Muse 模拟真实浏览器，翻阅目标版块当天的新帖和回帖，识别文字或图片中的邀请码，补全掩码，并在注册页面进行人工可控的快速验证。

仓库中的 [t66y监控迁移备份手册.md](t66y监控迁移备份手册.md) 是 Muse 的完整任务说明；它不是普通爬虫脚本。`monitor.py` 仅作为没有 Muse 时的基础扫描辅助工具。

## 掩码邀请码规则

参考 `1024RegisterTool`：

- `{i}`：该位置只尝试数字 `0-9`
- `{c}`：该位置只尝试十六进制字母 `a-f`
- `{a}`：该位置尝试数字和 `a-f`
- 原始帖子中的 `*`、`#`、`?` 等掩码，先根据发帖人的说明转换为对应占位符
- 优先处理不超过 2 个未知位置的码；组合过多时停止并报告，不盲目耗尽

Muse 必须使用浏览器页面完成验证，保留页面上下文和验证码状态；不要用裸 HTTP 高频提交。

## 使用

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python monitor.py --headed
```

首次运行只建立基线，不会发送提醒。之后发现新帖时，会写入 `data/status.json` 并打印摘要。

环境变量：

```bash
export T66Y_SECTION_URL='https://www.t66y.com/thread0806.php?fid=7'
```

本项目不保存密码、不把密码写入仓库。Muse 需要从 Secure Vault 使用凭据，并在验证码连续失败、出现 403、IP 限制或页面异常时立即停止。
