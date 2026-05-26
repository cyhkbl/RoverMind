cmake_minimum_required(VERSION 3.8)
project(walk_talk_run_sim)

find_package(ament_cmake REQUIRED)

install(DIRECTORY urdf world launch config DESTINATION share/${PROJECT_NAME})

ament_package()
