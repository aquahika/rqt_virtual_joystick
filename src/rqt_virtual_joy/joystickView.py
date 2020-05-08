from python_qt_binding import QtCore
from python_qt_binding.QtGui import QPainter, QColor, QFont, QPen, QBrush
from python_qt_binding.QtWidgets import QWidget,QGridLayout,QSizePolicy
import math



class JoystickView(QWidget):

    xMoved = QtCore.Signal(float)
    yMoved = QtCore.Signal(float)

    def __init__(self, parent = None): 
        super(JoystickView, self).__init__(parent) 
        self._initialized = False
        self._stickSize = 30    
        
        self._stickView = JoystickPointView(self)
        self._stickView.xMoved.connect(self.receiveXMoved)
        self._stickView.yMoved.connect(self.receiveYMoved)
        self.setMode("square")
        

    def receiveXMoved(self,val):
        self.xMoved.emit(val)

    def receiveYMoved(self,val):
        self.yMoved.emit(val)
               

    def setMode(self,mode):
        self._mode = mode
        self._stickView.setMode(mode)
        self.repaint()
        

    def paintEvent(self,event):
        if not self._initialized:
            self.placeStickAtCenter()
            self._initialized = True

        borderWidth = 1
        joyRange = 80
        center = QtCore.QPoint(self.height()/2,self.width()/2)
        
        qp = QPainter()
        qp.begin(self)
        qp.setRenderHint(QPainter.Antialiasing, True)
        qp.setPen(QPen(QtCore.Qt.lightGray, borderWidth, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap,QtCore.Qt.RoundJoin))

        if self._mode == "circle":

            qp.drawEllipse(center,joyRange,joyRange)

        if self._mode == "square":
            x = center.x() - joyRange
            y = center.y() - joyRange
            width = joyRange * 2
            height = joyRange * 2
            qp.drawRect(x,y,width,height)
       
        qp.end()

        super(JoystickView,self).paintEvent(event)

    def placeStickAtCenter(self):
        stickInitPosH = self.height()/2 - self._stickSize /2 
        stickInitPosW = self.width()/2  - self._stickSize /2
        self._stickView.setGeometry(stickInitPosH,stickInitPosW,self._stickSize,self._stickSize)

    def getJoyValue(self):
        return self._stickView.getJoyValue()



class JoystickPointView(QWidget):

    xMoved = QtCore.Signal(float)
    yMoved = QtCore.Signal(float)

    def __init__(self,parent = None):
        super(JoystickPointView,self).__init__(parent)
        self._range = 80
        self._mode = "circle"


    def paintEvent(self,event):
        super(JoystickPointView,self).paintEvent(event)

        try:
            if self._initialized:
                pass
        except: 
            self._origPos = self.pos()
            self._initialized = True

        qp = QPainter()
        qp.begin(self)
        
        borderWidth = 2
        radius = self.height()/2
        center = QtCore.QPoint(self.height()/2,self.width()/2) 
        
        # Outer Circle
        qp.setRenderHint(QPainter.Antialiasing, True)
        qp.setPen(QPen(QtCore.Qt.darkGray, borderWidth, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap,QtCore.Qt.RoundJoin))
        qp.setBrush(QBrush(QtCore.Qt.white, QtCore.Qt.SolidPattern))
        qp.drawEllipse(center,radius-borderWidth,radius-borderWidth)

        # Inner Circle
        qp.setPen(QPen(QtCore.Qt.lightGray, borderWidth, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap,QtCore.Qt.RoundJoin))
        qp.setBrush(QBrush(QtCore.Qt.white, QtCore.Qt.SolidPattern))
        qp.drawEllipse(center,radius-borderWidth-1,radius-borderWidth-1)

        qp.end()


    def mousePressEvent(self, event):
        self.__mousePressPos = None
        self.__mouseMovePos = None
        if event.button() == QtCore.Qt.LeftButton:
            self.setFocus()
            self.__mousePressPos = event.globalPos()
            self.__mouseMovePos = event.globalPos()

        super(JoystickPointView, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            if(self.__mouseMovePos == None):
                return

            currPos = self.mapToGlobal(self.pos())
            globalPos = event.globalPos()
            diff = globalPos - self.__mouseMovePos
            newPos = self.mapFromGlobal(currPos + diff)


            center = self.centerPos(newPos)
            origCenter = self.centerPos(self._origPos)
            relative = origCenter - center

            limited = self.limitStickMove(relative, self._mode)

            self._moveJoy(limited)
            self.__mouseMovePos = globalPos

        super(JoystickPointView, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        
        self._moveJoy(QtCore.QPoint(0,0))
        
        if self.__mousePressPos is not None:
            moved = event.globalPos() - self.__mousePressPos 
            if moved.manhattanLength() > 3:
                event.ignore()
                return

        super(JoystickPointView, self).mouseReleaseEvent(event)


    def centerPos(self,pos = None):
        if pos is None:
            pos = self.pos()
        x = pos.x() + (self.width() / 2)
        y = pos.y() + (self.height() / 2)
        return QtCore.QPoint(x,y)
    
    def revertCenterPos(self, pos = None):
        if pos is None:
            pos = self.pos()
        x = pos.x() - (self.width() / 2)
        y = pos.y() - (self.height() / 2)
        return QtCore.QPoint(x,y)    

    def limitStickMove(self,pos,mode = "square"):
        # Give joystick position from (0,0)
        x = 0
        y = 0

        if mode == "circle":

            norm = math.sqrt(pos.x() ** 2 + pos.y() ** 2)
   
            if  norm > self._range:
                ratio = self._range / norm
            else:
                ratio = 1.0
            
            x = pos.x() * ratio
            y = pos.y() * ratio


        if mode == "square":
        
            if abs(pos.x()) > self._range:
                sign = pos.x() / abs(pos.x())
                x = sign * self._range
            else:
                x = pos.x()

            if abs(pos.y()) > self._range:
                sign = pos.y() / abs(pos.y())
                y = sign * self._range
            else:
                y = pos.y()

        return QtCore.QPoint(x,y)

    def setMode(self,mode):
        self._mode = mode

    def setRange(self,value):
        self._range = value

    def getJoyValue(self):
        try:
            center = self.centerPos(self.pos())
            origCenter = self.centerPos(self._origPos)
            relative = origCenter - center

            x = float(relative.x()) / self._range
            y = float(relative.y()) / self._range

        except:
            x = float(0.0)
            y = float(0.0)

        return {'x': x, 'y': y}
    
    def _moveJoy(self,relative):

        pastJoyPos = self.getJoyValue()

        origCenter = self.centerPos(self._origPos)
        newCenter = origCenter - relative
        self.move(self.revertCenterPos(newCenter))

        newJoyPos = self.getJoyValue()

        if(pastJoyPos['x'] != newJoyPos['x']):
            self.xMoved.emit(newJoyPos['x'])
        if(pastJoyPos['y'] != newJoyPos['y']):
            self.yMoved.emit(newJoyPos['y'])
    




