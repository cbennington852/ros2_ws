rm -rf docs_build docs_output

source /opt/ros/jazzy/setup.bash

colcon build

source install/setup.bash

# Making the markdown to html for installation guide.
source venv/bin/activate
pip install pycomm3
pip install markdown2[all]
pip install numpy
pip install mdformat
python -m markdown2 --extras fenced-code-blocks fanuc_ros2_drivers/README.md > docs_manual/installation_instructions.html


rosdoc2 default_config --package-path fanuc_ros2_drivers/src/action_servers/
rosdoc2 default_config --package-path fanuc_ros2_drivers/src/fanuc_interfaces/
rosdoc2 default_config --package-path fanuc_ros2_drivers/src/msg_publishers/
rosdoc2 default_config --package-path fanuc_ros2_drivers/src/srv_services/

rosdoc2 build --package-path fanuc_ros2_drivers/src/action_servers
rosdoc2 build --package-path fanuc_ros2_drivers/src/fanuc_interfaces
rosdoc2 build --package-path fanuc_ros2_drivers/src/msg_publishers
rosdoc2 build --package-path fanuc_ros2_drivers/src/srv_services




# Sending index.
cp docs_manual/index.html docs_output/index.html
cp docs_manual/installation_instructions.html docs_output/installation_instructions.html

