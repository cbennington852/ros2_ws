rm -rf docs_build docs_output

rosdoc2 default_config --package-path fanuc_ros2_drivers/src/action_servers/
rosdoc2 default_config --package-path fanuc_ros2_drivers/src/fanuc_interfaces/
rosdoc2 default_config --package-path fanuc_ros2_drivers/src/msg_publishers/
rosdoc2 default_config --package-path fanuc_ros2_drivers/src/srv_services/

rosdoc2 build --package-path fanuc_ros2_drivers/src/action_servers
rosdoc2 build --package-path fanuc_ros2_drivers/src/fanuc_interfaces
rosdoc2 build --package-path fanuc_ros2_drivers/src/msg_publishers
rosdoc2 build --package-path fanuc_ros2_drivers/src/srv_services


# Making the markdown to html for installation guide.
source venv/bin/activate
pip install markdown2[all]
pip install mdformat
python -m markdown2 --extras fenced-code-blocks fanuc_ros2_drivers/README.md > docs_manual/installation_instructions.html


# Sending index.
cp docs_manual/index.html docs_output/index.html
cp docs_manual/installation_instructions.html docs_output/installation_instructions.html

