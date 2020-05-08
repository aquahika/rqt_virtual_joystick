import os
import rospy
import rospkg
from sensor_msgs.msg import Joy

from qt_gui.plugin import Plugin
from python_qt_binding import loadUi
from python_qt_binding.QtWidgets import QWidget,QGraphicsView
from python_qt_binding.QtGui import QCursor
from python_qt_binding import QtCore


class MyPlugin(Plugin):

    def __init__(self, context):

        super(MyPlugin, self).__init__(context)

        # Give QObjects reasonable names
        self.setObjectName('MyPlugin')

        # Process standalone plugin command-line arguments
        from argparse import ArgumentParser
        parser = ArgumentParser()
        # Add argument(s) to the parser.
        parser.add_argument("-q", "--quiet", action="store_true",
                      dest="quiet",
                      help="Put plugin in silent mode")
        parser.add_argument("-t", "--topic",
                      dest="topic",
                      type=str,
                      help="Set topic to publish [default:/joy]",
                      default="/joy")
        parser.add_argument("-r", "--rate",
                      dest="rate",
                      type=float,
                      help="Set publish rate [default:20]",
                      default=20)
        parser.add_argument("--type",
                      dest="type",
                      type=str,
                      choices=['circle', 'square'],
                      default='circle')


        args, unknowns = parser.parse_known_args(context.argv())
        if not args.quiet:
            print 'arguments: ', args
            print 'unknowns: ', unknowns

        # Create QWidget
        self._widget = QWidget()
        # Get path to UI file which should be in the "resource" folder of this package
        ui_file = os.path.join(rospkg.RosPack().get_path('rqt_virtual_joy'), 'resource', 'VirtualJoy.ui')
        # Extend the widget with all attributes and children from UI file
        loadUi(ui_file, self._widget)
        # Give QObjects reasonable names
        self._widget.setObjectName('MyPluginUi')
        # Show _widget.windowTitle on left-top of each plugin (when 
        # it's set in _widget). This is useful when you open multiple 
        # plugins at once. Also if you open multiple instances of your 
        # plugin at once, these lines add number to make it easy to 
        # tell from pane to pane.
        if context.serial_number() > 1:
            self._widget.setWindowTitle(self._widget.windowTitle() + (' (%d)' % context.serial_number()))
        # Add widget to the user interface
        context.add_widget(self._widget)

        self._widget.topicLineEdit.returnPressed.connect(self.topicNameUpdated)
        self._widget.topicLineEdit.setText(args.topic)  # Default Topic
        self.updatePublisher()

        self._widget.publishCheckBox.stateChanged.connect(self.publishCheckboxChanged)
        self._widget.rateSpinBox.valueChanged.connect(self.publishRateSpinBoxChanged)
        self._widget.rateSpinBox.setValue(args.rate)

        self._widget.joy.xMoved.connect(self.receiveX)
        self._widget.joy.yMoved.connect(self.receiveY)

        self._widget.shapeSelectBox.addItem("square")
        self._widget.shapeSelectBox.addItem("circle")

        self._widget.shapeSelectBox.activated.connect(self.indexChanged)
        self._widget.shapeSelectBox.setCurrentText(args.type) # circle
        self._widget.joy.setMode(args.type)


    def topicNameUpdated(self):
        self.updatePublisher()


    def updatePublisher(self):
        topic = str(self._widget.topicLineEdit.text())
        try:
            if self.pub != None:
                self.pub.unregister()
        except:
            pass
        self.pub = None
        self.pub = rospy.Publisher(topic, Joy,queue_size=10)

    def startIntervalTimer(self,msec):

        try:
            self._timer.stop()
        except:
            self._timer = QtCore.QTimer(self)
            self._timer.timeout.connect(self.processTimerShot)
        
        if msec > 0:
            self._timer.setInterval(msec)
            self._timer.start()


    def publishCheckboxChanged(self,status):
        self.updateROSPublishState()

    def publishRateSpinBoxChanged(self,status):
        self.updateROSPublishState()
        
    def updateROSPublishState(self):

        if self._widget.publishCheckBox.checkState() == QtCore.Qt.Checked:
            rate = self._widget.rateSpinBox.value()
            self.startIntervalTimer(float(1000.0/rate))
        else:
            self.startIntervalTimer(-1)  # Stop Timer (Stop Publish)

    
    def indexChanged(self,index):
        text = str(self._widget.shapeSelectBox.currentText())
        self._widget.joy.setMode(str(text))

    def receiveX(self,val):
        self.updateJoyPosLabel()

    def receiveY(self,val):
        self.updateJoyPosLabel()

    def updateJoyPosLabel(self):
        pos = self.getROSJoyValue()
        text = "({:1.2f},{:1.2f})".format(pos['x'],pos['y'])
        self._widget.joyPosLabel.setText(text)

    def processTimerShot(self):
        joy = self.getROSJoyValue()
        msg = Joy()
        msg.header.stamp = rospy.Time.now()
        msg.axes.append(float(joy['x']))
        msg.axes.append(float(joy['y']))

        button_num = 1
        while True:
            try:
                msg.buttons.append(eval("self._widget.button"+str(button_num)).isDown())
                button_num+=1
            except:
                break

        try:
            self.pub.publish(msg)
        except:
            rospy.logwarn("publisher not initialized")
            pass

    def getROSJoyValue(self):
        return self.convertREPCoordinate(self._widget.joy.getJoyValue())

    def convertREPCoordinate(self,input):
        output = {}
        output['x'] = input['y']
        output['y'] = input['x']
        return output

    def shutdown_plugin(self):
        # TODO unregister all publishers here
        self.pub.unregister()
        pass

    def save_settings(self, plugin_settings, instance_settings):
        # TODO save intrinsic configuration, usually using:
        # instance_settings.set_value(k, v)
        pass

    def restore_settings(self, plugin_settings, instance_settings):
        # TODO restore intrinsic configuration, usually using:
        # v = instance_settings.value(k)
        pass

    #def trigger_configuration(self):
        # Comment in to signal that the plugin has a way to configure
        # This will enable a setting button (gear icon) in each dock widget title bar
        # Usually used to open a modal configuration dialog