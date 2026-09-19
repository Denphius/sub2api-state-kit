# 发布验证记录

## main：无代理账号直连复验（2026-09-19）

已审查并采纳 [woai66 的修复 c0df12b](https://github.com/woai66/sub2api-state-kit/commit/c0df12bf49ded9e34959353d3a290b0b6d932dfb)，对应 [Issue #2](https://github.com/wangyunjeff/sub2api-state-kit/issues/2)。保留原作者署名与 cherry-pick 来源。

审查确认：仅 `ProxyID` 和 `Proxy` 同时为空才视为直连；缺失其中一个仍拒绝启用。动态代理采集不变，直连复验使用现有 HTTPUpstream 的空代理路径（该路径不读取环境代理）。票据继续检查同账号、模型、套餐及业务出口绑定；固定代理旧指纹格式保持兼容，切换直连与固定代理后旧票据、迟到任务结果均不能使用。

在从固定上游与覆盖包重新组装的隔离源码目录验证：

| 检查 | 结果 |
| --- | --- |
| 43 个覆盖文件 SHA256 与上游基线校验、源码组装 | 通过 |
| service / admin handler / middleware 的 STATE 定向回归，开启 `-race` | 3 个包通过，无竞态报告 |
| Pro / Team 直连采集与复验、保存及缓存恢复 | 通过 |
| 双向业务出口切换、旧票据拒绝、迟到任务不能发布 | 通过 |
| 配置不完整 / 非活跃账号拒绝启用，关闭仍允许 | 通过 |
| 账号 STATE 组件、设置页、语言键测试 | 3 个文件、60 项通过 |
| `vue-tsc -b` 与 Vite 完整构建 | 通过 |

后端命令：`GOMAXPROCS=4 go test -race -p 2 ./internal/service ./internal/handler/admin ./internal/server/middleware -run 'Test.*(CodexTicket|CodexAccountTicket|OpenAICodexTicket|RedactAudit)' -count=1`。

这些是模拟上游回归，不代表实测了真实 VPS 的模型恢复效果。本次只更新 `main` 源码与说明，未更新旧 v0.2.0 Release 附件、安装运行中的本地服务或修改生产服务。独立插件已有空代理直连路径，本次未改动插件。

## v0.2.0 完整部署版

2026-09-19，[公开工作流 35419330599](https://github.com/wangyunjeff/sub2api-state-kit/actions/runs/35419330599) 全部通过，实际构建提交 `6519e8d19e81eb166ccb16cf68d479f3e87d54e1`。完整源码与两个 Linux 部署包的 `RELEASE.json` 均记录该提交。

| 检查 | x86_64 / amd64 | ARM64 |
| --- | --- | --- |
| 前端 58 项定向测试、类型检查与完整构建 | 共用构建通过 | 共用构建通过 |
| 后端 STATE / 账号管理 / 审计定向回归 | 通过 | 通过 |
| 原生 Linux 编译、内嵌网页、版本检查 | 通过 | 通过 |
| Docker Compose 空白安装，健康检查 | 通过 | 通过 |
| 随机生成的管理员登录、网页可访问 | 通过 | 通过 |
| 模型账号、代理、API Key 数量均为 0 | 通过 | 通过 |
| STATE 默认关闭，全局动态池为空 | 通过 | 通过 |
| 保留原版首次登录确认流程，无预置确认记录 | 通过 | 通过 |
| 应用容器重启后再次完成以上检查 | 通过 | 通过 |

本次没有使用真实模型账号或代理调用上游。Linux 包中的 Dockerfile 只组装已编译程序；以上容器测试针对 Linux 部署包，未另外执行完整源码包的多阶段 Docker 编译。首次验收脚本曾将原版首次登录确认返回的 HTTP 423 当成失败，随后改为检查并保留该流程，未修改应用功能以绕过它。

完整源码由固定上游和相同的 43 个覆盖文件重新生成。已检查源码压缩包和两个部署包的文件哈希、架构、无 `.env` / Git 历史、无个人运行配置。与已知私密账号、代理、令牌和 IP 值比对未发现实际私密值；匹配到的 `admin@sub2api.local` 是上游默认示例邮箱。完整上游代码的通用密钥扫描存在测试样例与公开客户端常量等命中，相应文件与官方固定基线一致，没有新增泄漏命中。源码中的测试字符串不代表预置账号。

Linux 部署包没有数据库，实例启动时由自己的 PostgreSQL 卷初始化。没有做生产负载、模型能力、真实 Team 恢复或完整一小时上游有效期验收。

## v0.1.0 验证记录

2026-09-18，在由固定上游提交与公开覆盖包生成的隔离源码中验证。

| 项目 | 结果 |
| --- | --- |
| 从 GitHub 固定提交生成源码 | 通过，43 个覆盖文件哈希一致 |
| 从本地上游 Git 镜像生成源码 | 通过，不复制镜像工作区改动 |
| 拒绝已有目标目录、拒绝被改动的覆盖文件 | 通过 |
| STATE 组件、设置页面与语言键测试 | 3 个文件、58 项测试通过 |
| 变更前端文件 ESLint | 通过 |
| 前端完整构建（含 vue-tsc 类型检查） | 通过 |
| 后端 service、admin handler、middleware 的 Codex 定向测试 | 3 个包通过 |
| 含前端资源的服务端原生编译 | 通过，CGO_ENABLED=0、embed、trimpath |
| Gitleaks 8.30.1 源码与新 Git 历史扫描 | 通过，未发现泄漏 |
| 本地私密账号／代理／令牌值与发布内容逐项比对 | 未发现匹配 |

构建环境：macOS ARM64、Go 1.27.1、Node.js 24.15.0、pnpm 10.28.1。首次前端构建在 1536 MiB Node 堆上限下内存不足；调整为 3072 MiB 后通过。未修改功能代码来规避检查。

主要验证命令（在生成源码的对应目录运行）：

```bash
# backend/
GOMAXPROCS=2 GOMEMLIMIT=2GiB GOGC=50 go test -p 1 \
  ./internal/service ./internal/handler/admin ./internal/server/middleware \
  -run 'Test.*(Codex|codex)' -count=1

# frontend/
pnpm install --frozen-lockfile
pnpm exec vitest run \
  src/components/account/__tests__/CodexAccountTicketSettings.spec.ts \
  src/views/admin/__tests__/SettingsView.spec.ts \
  src/i18n/__tests__/localeKeyCompleteness.spec.ts \
  --maxWorkers=1 --minWorkers=1
NODE_OPTIONS=--max-old-space-size=3072 pnpm run build

# backend/，前端构建完成后
GOMAXPROCS=2 GOMEMLIMIT=2GiB GOGC=50 CGO_ENABLED=0 \
  go build -p 1 -tags embed -trimpath -ldflags '-s -w' -o /tmp/sub2api-state-validation ./cmd/server
```

测试使用合成数据与模拟响应，没有调用真实账号、代理或模型。未运行全仓测试、完整 race 测试、Docker 镜像构建或生产回归；未验证真实 Team 全链路、真实上游撤销及一小时有效期。测试通过不能作为上游路由或模型能力恢复保证。

只公开结果与可复现命令，不包含私密日志或真实请求记录。源码中的回环地址、示例域名和测试凭据属于通用配置／合成测试数据，不是部署数据。

## README 对照图

本版使用者提供的 Team / Pro 原图已替换旧图片。公开图片保留原图像素尺寸、完整界面及上下顺序，顶部增加 Team / Pro 标题栏，并添加红框和文字；遮挡了账号、渠道、分组及请求标识，并移除了源图元数据。截图说明依据使用者提供的启用前后顺序，独立于上述自动化验证记录。
