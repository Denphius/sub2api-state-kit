# 完整 Sub2API + STATE 发布版

从 v0.2.0 开始，Release 同时提供完整源码和 Linux 部署包。原有增量仓库不删除，便于审查改动与合并；完整包由固定上游 v0.2.6 和相同的 43 个覆盖文件构建。不是另一个简化网关，保留完整 Sub2API 功能。

## 选择文件

- Linux x86_64：`sub2api-state-kit_v0.2.0_linux_amd64.tar.gz`。
- Linux ARM64：`sub2api-state-kit_v0.2.0_linux_arm64.tar.gz`。
- 完整源码：`sub2api-state-kit_v0.2.0_full-source.zip` 或 `.tar.gz`。
- `SHA256SUMS`：上述下载附件的校验值。每个包内部也包含文件校验表。

下载入口：<https://github.com/wangyunjeff/sub2api-state-kit/releases/tag/v0.2.0>。GitHub 自动附加的 Source code 只含增量仓库，和 full-source 附件不同。

## 空白新安装

在有 Docker Compose v2 和 openssl 的 Linux 服务器解压对应部署包，在解压目录运行：

```bash
sh init.sh
# 按需要编辑 .env
docker compose up -d --build
docker compose ps
```

`init.sh` 在这台服务器生成独立管理员密码、数据库/Redis 密码、JWT/TOTP 密钥，文件权限限制为当前用户可读写；不会覆盖已有 `.env`。管理员邮箱默认示例值 `admin@example.com`，启动前自行修改。管理员密码查看本机 `.env` 的 `ADMIN_PASSWORD`。

默认监听 `127.0.0.1:8080`，适合接入现有反向代理；需要直接从外部访问时将 `BIND_HOST` 改为 `0.0.0.0`。数据库和 Redis 不发布宿主机端口。数据使用当前 Compose 项目的命名卷保存。多个安装目录需指定不同 `COMPOSE_PROJECT_NAME` 与端口。

部署包已内置网页与 Linux 二进制，不需要 Go、Node.js 或 pnpm。Docker 首次仍需下载运行基础镜像。完整源码包则使用根目录 Dockerfile 编译，耗时与资源需求遵循上游；下载源码不等于已编译部署包。

登录后按熟悉的 Sub2API 流程配置账号、代理、分组和 Key。STATE 设置步骤见 [使用说明](usage.md)。不附带任何人的模型账号或可用额度，STATE 默认关闭，不会自动采集。

## 现有用户升级

这是新安装示例，不能直接替代现有生产 Compose。先备份、核对当前版本与官方 v0.2.6 的差异，在独立数据库与 Redis 中测试，再只替换应用二进制/镜像，保留自己的数据卷、数据库、Redis、环境、域名、JWT/TOTP 密钥。

原版面板内置更新仍指向上游；直接更新为官方程序会失去本扩展。后续请使用本项目的发布包或重新合并增量代码。回滚前关闭 STATE 总开关，并核对官方版本兼容性。不要为回滚应用而直接覆盖为旧数据库。

## 发布内容和隐私

完整源码从固定上游 Git 提交重新组装，不复制开发机工作区、Git 历史、运行数据或本地环境。Linux 二进制由公开工作流在干净的 GitHub Runner 上构建，使用 `-trimpath`，不携带本机源码绝对路径。

发布包只有代码、编译产物、通用配置模板、测试与文档：没有作者的模型账号、代理凭据/IP 清单、API Key、STATE 或数据库。源码中保留上游公开的测试样本、示例地址和 OAuth 客户端常量，它们不是作者账号数据。仓库中经遮挡的界面图只作说明，不会成为实例配置。

`RELEASE.json` 提供实际构建提交、上游提交、覆盖文件清单哈希和架构。源码、许可证、构建脚本与二进制同时发布。

本地复现：

```bash
python3 scripts/package_release.py source --work assembled --output artifacts
```

Linux 二进制构建与空白安装、重启检查过程见 `.github/workflows/full-release.yml`。完整包不增加 STATE 功能范围，不构成生产负载或上游模型路由保证；已有功能验证范围见 [验证说明](validation.md)。
