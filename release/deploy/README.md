# Sub2API + STATE 完整部署包

基于 Sub2API v0.2.6 的非官方完整版本，包含原有管理后台、API 网关和账号级 STATE 扩展。无需先安装官方 Sub2API，也无需应用补丁。

这是空白安装包：没有作者的模型账号、代理/IP、API Key、STATE、数据库或部署配置。首次启动只会创建你自己的管理员，模型账号、代理和 API Key 都需要自己配置。

## 新安装

需要 Docker Engine、Docker Compose v2、openssl 和可下载容器基础镜像的网络。选择与服务器架构匹配的包：`uname -m` 为 `x86_64` 用 `linux_amd64`，为 `aarch64` / `arm64` 用 `linux_arm64`。

```bash
tar -xzf sub2api-state-kit_v0.2.0_linux_amd64.tar.gz
cd sub2api-state-kit_v0.2.0_linux_amd64
sh init.sh
# 编辑 .env：填写自己的 ADMIN_EMAIL，按需修改 BIND_HOST 和 SERVER_PORT
docker compose up -d --build
docker compose ps
```

ARM64 请把解压文件名和目录名替换为 `linux_arm64`。

Linux 部署包已包含编译好的 `sub2api` 与网页资源，`--build` 仅组装运行镜像，不编译 Go 或前端。首次需下载 Alpine、PostgreSQL、Redis 等镜像；不是离线安装包。

默认仅监听服务器本机 `127.0.0.1:8080`，可通过现有反向代理访问。需要直接从其他电脑访问时，在 `.env` 中自行将 `BIND_HOST` 改为 `0.0.0.0`，通过 `http://服务器地址:8080` 打开。端口可改为未占用值。

使用 `.env` 中的 `ADMIN_EMAIL` 和自动生成的 `ADMIN_PASSWORD` 登录。`init.sh` 为每次新安装生成不同密码和密钥，已有 `.env` 时不覆盖。配置和数据保存在该 Compose 项目的命名卷里，重启不丢失；不要把部署后的 `.env` 或数据库分享出去。

## 开启 STATE

1. 按原版 Sub2API 的流程添加自己的模型账号、固定业务代理、分组和 API Key。
2. 系统设置 → 网关服务：开启 STATE 总开关，填写自己的全局动态 IP 池并保存。
3. 账号管理 → 编辑指定账号：选择 Pro / Team，开启该账号 STATE 并保存。
4. 等待采集和固定代理复验通过。未开启的账号继续按原流程工作。

详见 `docs/usage.md`。总开关和账号开关默认关闭，安装不会自动发出模型采集请求。

## 已有 Sub2API 用户

新安装的 Compose 是独立实例示例，不要直接覆盖现有生产配置。先备份并在隔离环境测试，然后只替换应用二进制或自行构建的应用镜像，保留自己的数据库、Redis、卷、域名、JWT/TOTP 密钥和全部配置。上游版本不一致时先评估迁移。

本版本仍沿用上游更新服务。不要在面板里直接更新到官方版本，否则账号级 STATE 扩展会丢失；后续升级使用本项目的完整包或重新合并扩展。

Linux 二进制也可直接配合现有 PostgreSQL / Redis 使用：`./sub2api --setup`，或按上游文档设置环境与配置文件。二进制运行时保留旁边的 `resources/`。原生部署如需数据库备份/恢复，请安装与数据库匹配的 `pg_dump` / `psql`；Compose 镜像已包含 PostgreSQL 18 客户端。

## 版本与验证

`RELEASE.json` 记录本包提交及基线，`SHA256SUMS` 校验包内文件。源代码和实验功能限制见本项目公开仓库；不承诺上游持续接受 STATE 或恢复回答质量。

源码、测试和许可证同时提供。保留上游 LGPL v3 版权与署名，详见 `LICENSE`、`COPYING.GPL3` 和 `STATE-KIT-NOTICE.md`。
