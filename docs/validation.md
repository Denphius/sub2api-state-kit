# v0.1.0 验证记录

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

后续补充了使用者提供的 Team / Pro 界面对照截图。公开图片保留原始尺寸、完整界面及上下顺序，只添加红框和文字；遮挡了账号、渠道、分组及请求标识，并移除了源图元数据。截图说明依据使用者提供的启用前后顺序，独立于上述自动化验证记录。
