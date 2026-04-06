# ROS Walk Talk Run

一个从零整理过的、可公开发布的 ROS 2 Python 示例仓库，用来演示“按动作序列驱动机器人移动，并在关键节点输出说话提示”这一思路。

当前仓库只保留通用 ROS 2 依赖和可确认公开的内容，不包含任何特定厂商 SDK、内部消息定义、私有资源文件或闭源接口。

## 功能

- 按配置文件中的动作序列依次执行任务
- 向可配置的 `cmd_vel` 风格 topic 持续发布 `geometry_msgs/msg/Twist`
- 在“说话”步骤打印日志，并可选发布 `std_msgs/msg/String`
- 支持中断退出时发送停止指令
- 所有速度上限、话题名、动作序列文件都可通过参数调整

## 仓库结构

```text
.
|-- src/
|   `-- walk_talk_run_demo/
|       |-- package.xml
|       |-- setup.py
|       |-- config/
|       |   `-- default_sequence.json
|       |-- launch/
|       |   `-- sequence_runner.launch.py
|       |-- resource/
|       |   `-- walk_talk_run_demo
|       |-- test/
|       |   `-- test_sequence_model.py
|       `-- walk_talk_run_demo/
|           |-- __init__.py
|           |-- sequence_model.py
|           `-- sequence_runner.py
|-- .github/
|-- LICENSE
`-- README.md
```

## 依赖

- ROS 2
- `rclpy`
- `geometry_msgs`
- `std_msgs`
- `ament_index_python`
- `colcon`

## 快速开始

```bash
source /opt/ros/<your_ros_distro>/setup.bash
colcon build --packages-select walk_talk_run_demo
source install/setup.bash
ros2 run walk_talk_run_demo sequence_runner
```

默认会读取安装目录中的 `config/default_sequence.json`。

如果你想显式指定动作序列文件：

```bash
ros2 run walk_talk_run_demo sequence_runner --ros-args \
  -p sequence_file:=/absolute/path/to/sequence.json
```

## 默认动作格式

动作序列是一个 JSON 数组。支持三种步骤：

### 1. motion

```json
{
  "type": "motion",
  "linear_x": 0.3,
  "linear_y": 0.0,
  "angular_z": 0.0,
  "duration": 2.0
}
```

### 2. speech

```json
{
  "type": "speech",
  "text": "Hello, this is a motion cue.",
  "pause_after_sec": 1.5
}
```

### 3. pause

```json
{
  "type": "pause",
  "duration": 1.0
}
```

## 常用参数

- `cmd_vel_topic`
  默认值：`/cmd_vel`
- `speech_topic`
  默认值：空字符串。为空时只打印日志，不发布字符串消息
- `publish_hz`
  默认值：`20.0`
- `sequence_file`
  默认值：包内自带配置文件
- `max_linear_speed`
  默认值：`1.0`
- `max_angular_speed`
  默认值：`1.0`
- `stop_grace_period`
  默认值：`0.5`

## Launch 示例

```bash
ros2 launch walk_talk_run_demo sequence_runner.launch.py
```

也可以覆盖参数：

```bash
ros2 launch walk_talk_run_demo sequence_runner.launch.py \
  cmd_vel_topic:=/robot/cmd_vel \
  speech_topic:=/speech_cue \
  max_linear_speed:=0.6
```

## 测试

```bash
source /opt/ros/<your_ros_distro>/setup.bash
colcon test --packages-select walk_talk_run_demo
colcon test-result --verbose
```

当前测试覆盖的是动作序列加载与校验逻辑，不包含真机行为验证。

## 安全提醒

这个仓库只提供控制逻辑示例，不替你兜底真机风险。任何人把它接到真实机器人上之前，都应该自己确认：

- 场地安全
- 急停可用
- 限速合理
- 周围没有人和易碎物

## 许可证

本项目采用 Apache-2.0，详见 `LICENSE`。
