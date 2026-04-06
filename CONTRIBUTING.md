# Contributing

欢迎贡献，但别把仓库重新搞脏。

## 基本要求

- 只提交你确认拥有分发权的内容
- 不要引入厂商私有 SDK、闭源消息定义或来源不明资源
- 修改行为逻辑时同步更新 `README.md`
- 不要提交 `build/`、`install/`、`log/`

## 开发流程

1. 从 `main` 拉分支。
2. 只做必要改动，不要顺手重构一大片。
3. 提交前运行相关测试。
4. PR 里写清楚动机、影响范围、验证方式和风险。

## 验证命令

```bash
source /opt/ros/<your_ros_distro>/setup.bash
colcon test --packages-select walk_talk_run_demo
colcon test-result --verbose
```
