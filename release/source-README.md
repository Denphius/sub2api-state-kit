# Sub2API + STATE 完整源码版

这是完整 Sub2API v0.2.6 与账号级 STATE 扩展的合并源码，不需要先获取上游或应用补丁。根目录 README 保留了上游原文；要部署包含本扩展的版本，请使用本说明和根目录 `compose.yaml`，不要使用上游的官方镜像安装命令。

## 从源码新部署

需要 Docker Compose v2、openssl 和可下载构建依赖的网络。

```bash
# 解压 full-source 包，进入解压后的根目录
sh init.sh
# 编辑 .env：填写自己的 ADMIN_EMAIL，按需修改 BIND_HOST 和 SERVER_PORT
docker compose up -d --build
docker compose ps
```

此命令会编译完整前端和 Go 后端，再启动应用、PostgreSQL 和 Redis。首次编译需要一定时间和内存；不想编译请使用同一 Release 的 `linux_amd64` / `linux_arm64` 部署包，它们已经包含编译好的程序。

默认仅监听 `127.0.0.1:8080`。需要从其他电脑直接访问时，将 `.env` 的 `BIND_HOST` 改为 `0.0.0.0`，或接入自己的反向代理。管理员邮箱与自动生成的密码见本机 `.env`；已有 `.env` 不会被初始化脚本覆盖。数据保存在 Compose 命名卷中。

## 空白实例与 STATE 设置

包内不包含作者的模型账号、代理/IP、API Key、STATE、数据库或部署环境。首次启动只创建你自行配置的管理员；自行添加模型账号、代理、分组和 Key。

STATE 总开关和账号开关默认关闭。配置顺序：系统设置 → 网关服务填写自己的全局动态池并启用总开关，然后编辑需要使用的账号，选择 Pro / Team、启用账号 STATE。详见 [使用说明](docs/state-kit/usage.md)。

## 现有实例

不要把新安装 Compose 直接覆盖现有生产配置。先备份、核对上游版本、隔离测试，再仅替换应用，保留自己的数据库、Redis、数据卷、域名和密钥。详情见 [完整部署版说明](docs/state-kit/full-release.md)。

应用的内置在线更新仍指向官方上游；更新为官方程序会失去 STATE 扩展。后续请使用本项目发布包或重新合并增量。

`RELEASE.json` 记录源码版本，`STATE-KIT-UPSTREAM.json` 记录上游及覆盖文件哈希，`SHA256SUMS` 用于核对解压后的源码文件。保留上游 LGPL v3 许可证与署名。
