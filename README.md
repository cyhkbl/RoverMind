# ROS2 机器人电控语音操作

> 基于 ROS 2 Humble + 智源灵犀X2 人型机器人，通过 JSON 动作序列驱动机器人运动控制与语音播报。

```
┌─────────────────────────────────────────────────────────┐
│  config/default_sequence.json                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │  motion   │→│  speech   │→│  motion   │→ ...        │
│  │  前进2s   │  │ "到达1"  │  │  右转1.8s │             │
│  └──────────┘  └──────────┘  └──────────┘              │
└────────────────────────┬────────────────────────────────┘
                         ▼
              ┌─────────────────────┐
              │  SequenceRunnerNode │  (ROS 2 Node)
              │  ─────────────────  │
              │  · 解析动作序列     │
              │  · 速度安全校验     │
              │  · 20Hz 持续发布    │
              │  · 中断停止保护     │
              └──────┬──────┬──────┘
                     │      │
            cmd_vel  │      │ speech_cue
          (Twist)    │      │ (String)
                     ▼      ▼
              ┌────────┐  ┌────────┐
              │ 舵机   │  │ TTS    │
              │ 运动控制│  │ 语音播报│
              └────────┘  └────────┘
```

## 三种动作类型

| 类型 | 作用 | 关键参数 |
|------|------|----------|
| `motion` | 发布速度指令 | `linear_x/y`, `angular_z`, `duration` |
| `speech` | 输出语音/日志 | `text`, `pause_after_sec` |
| `pause` | 静默等待 | `duration` |

速度指令经 `max_linear_speed` / `max_angular_speed` 硬限幅，超出范围直接报错拒绝执行。

## 快速开始

```bash
source /opt/ros/humble/setup.bash
colcon build --packages-select walk_talk_run_demo
source install/setup.bash
ros2 run walk_talk_run_demo sequence_runner
```

自定义动作序列：

```bash
ros2 run walk_talk_run_demo sequence_runner --ros-args \
  -p sequence_file:=/path/to/your_sequence.json
```

## 自定义动作序列

编辑 JSON 文件即可，支持三种步骤混合编排：

```json
[
  {"type": "motion", "linear_x": 0.3, "linear_y": 0.0, "angular_z": 0.0, "duration": 2.0},
  {"type": "speech", "text": "到达检查点", "pause_after_sec": 1.5},
  {"type": "pause", "duration": 0.5}
]
```

所有动作在加载时经过 `validate_sequence()` 校验：类型合法性、速度上限、duration 正数检查。

## 可配置参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `cmd_vel_topic` | `/cmd_vel` | 速度指令 topic |
| `speech_topic` | `""`（空=仅日志） | 语音 topic |
| `publish_hz` | `20.0` | 发布频率 |
| `max_linear_speed` | `1.0` | 线速度上限 (m/s) |
| `max_angular_speed` | `1.0` | 角速度上限 (rad/s) |
| `stop_grace_period` | `0.5` | 中断后停止指令延迟 (s) |

## 设计决策

- **JSON 驱动的动作序列**：将运动逻辑与代码解耦，无需重新编译即可调整机器人行为
- **速度硬限幅**：在发布层强制校验，防止配置错误导致机器人失控
- **优雅停止**：捕获 SIGINT/SIGTERM 后发送零速度指令，避免机器人在中断时持续运动
- **rclpy 定时器**：以固定 20Hz 频率持续发布速度指令，确保运动平滑

## 测试

```bash
colcon test --packages-select walk_talk_run_demo
colcon test-result --verbose
```

测试覆盖动作序列的加载与校验逻辑（`test_sequence_model.py`），不包含真机行为验证。

## 仓库结构

```
src/walk_talk_run_demo/
├── config/default_sequence.json    # 默认动作序列
├── launch/sequence_runner.launch.py # Launch 文件
├── test/test_sequence_model.py     # 单元测试
└── walk_talk_run_demo/
    ├── sequence_model.py           # 序列解析 + 校验
    └── sequence_runner.py          # ROS 2 节点主逻辑
```

## 安全提醒

接入真机前请确认：场地安全、急停可用、限速合理、周围无障碍物。

## 许可证

Apache-2.0
