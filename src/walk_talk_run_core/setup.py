from setuptools import find_packages, setup

package_name = "walk_talk_run_core"

setup(
    name=package_name,
    version="0.2.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/config", ["config/default_sequence.json"]),
        ("share/" + package_name + "/launch", ["launch/sequence_runner.launch.py"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="cyhkbl",
    maintainer_email="cyhkbl@users.noreply.github.com",
    description="ROS 2 motion/speech sequence runner with closed-loop control.",
    license="Apache-2.0",
    entry_points={
        "console_scripts": [
            "sequence_runner = walk_talk_run_core.sequence_runner:main",
            "obstacle_avoider = walk_talk_run_core.obstacle_avoider:main",
        ],
    },
)
