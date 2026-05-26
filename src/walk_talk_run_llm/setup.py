from setuptools import find_packages, setup

package_name = "walk_talk_run_llm"

setup(
    name=package_name,
    version="0.2.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/launch", ["launch/intent_parser.launch.py"]),
    ],
    install_requires=["setuptools", "anthropic"],
    zip_safe=True,
    maintainer="cyhkbl",
    maintainer_email="cyhkbl@users.noreply.github.com",
    description="LLM-based natural language to motion sequence parser.",
    license="Apache-2.0",
    entry_points={
        "console_scripts": [
            "intent_parser = walk_talk_run_llm.intent_parser:main",
        ],
    },
)
