FROM osrf/ros:humble-desktop

# Install Gazebo Fortress (Ignition) bridge and robot tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-humble-ros-gz-sim \
    ros-humble-ros-gz-bridge \
    ros-humble-robot-state-publisher \
    ros-humble-xacro \
    ros-humble-tf2-ros \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip3 install --no-cache-dir anthropic

# Copy workspace
COPY src /workspace/src
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

WORKDIR /workspace

# Build the workspace
RUN /bin/bash -c "source /opt/ros/humble/setup.bash && \
    colcon build --packages-select walk_talk_run_core walk_talk_run_sim walk_talk_run_llm"

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
