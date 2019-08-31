# Heat-Tower-GCode-Temperature-Setting
Simple python script, which sets temperature settings in a heat tower object.

Simple call the script with following arguments:
/path/to/file.gcode (File name needs to end with ".gcode")
max temperature
min temperature
temperature steps

Script will automatically divide number of layers into equal sections of temperature and insers temperature setting code before the layer change.
