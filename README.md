# rqt_virtual_joystick
Simple rqt virtual joystick publish `sensor_msgs/Joy` message.

<img src="https://raw.githubusercontent.com/aquahika/rqt_virtual_joystick/melodic-devel/screenshot/window.png">

## Usage

```
rqt_virtual_joystick
```

or

```
rosrun rqt_virtual_joystick rqt_virtual_joystick
```

Check `Publish` box to start publishing.


## Options

- -t [--topic] topic
    - Specify a initial topic to publish here. default: `/joy` 
- -r [--rate] hz
    - Initial publishing rate. default: `20Hz`
- --type ( circle | square )
    - Select initial joystick type. default: `circle`

## Author
Hikaru Sugiura 

## License

`input-gaming.png` icon from Tango Project is licensed under `CC-BY-SA`  
http://tango.freedesktop.org/

Any other source codes are licenced under [MIT license](https://en.wikipedia.org/wiki/MIT_License). 