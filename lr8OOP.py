import clr
import random
import time
from abc import ABC, abstractmethod
import numpy as np

clr.AddReference('System')
clr.AddReference('System.IO')
clr.AddReference('System.Drawing')
clr.AddReference('System.Reflection')
clr.AddReference('System.Threading')
clr.AddReference('System.Windows.Forms')

from System import EventHandler
import System.IO
import System.Drawing as Dr
import System.Reflection
import System.Windows.Forms as WinForm

class __storageList__(ABC): #снаружи наше "хранилище" ведет себя как список
    @abstractmethod
    def __init__(self): #ининциализация списка
        pass
    def add(self, x, index): #добавление элемента по индексу
        pass
    def getNode(self, index): #получение узла по индексу
        pass
    def cotnains(self, name): #проверка наличия элемента в узлах списка
        pass
    def isEmpty(self): #проверяет список на наличие хотя бы 1го элемента 
        pass
    def deleteIndex(self, index): #удаление элемента по индексу
        pass
    def deleteNode(self, node): 
        pass
    def clear(self): #очистка списка
        pass 


class Node(object):
    def __init__(self, x = None, v = None):
        self.key = x
        self.next = None
        self.prev = v
    
    def deleteThis(self):
        if self.prev:
            self.prev.next = self.next
        if self.next:
            self.next.prev = self.prev
        del self.key
        del self

class storage(__storageList__):
    def __init__(self):
        self.head = None
        self.len = 0
    
    def add(self, x, index = None):
        newNode = Node(x)
        if self.head is None:
            self.head = newNode
            self.len += 1
            return
        lastNode = self.head
        if index is not None:
            for i in range(index):
                if (lastNode.next):
                    lastNode = lastNode.next
            if lastNode.prev:
                lastNode.prev.next = newNode
                newNode.prev = lastNode.prev
            lastNode.prev = newNode
            newNode.next = lastNode
            if index == 0: self.head = newNode
        else:
            while lastNode.next:
                lastNode = lastNode.next
            lastNode.next = newNode
            newNode.prev = lastNode
        self.len += 1
    
    def getNode(self, index):
        if index > self.len-1: IndexError("IndexError")
        lastNode = self.head
        for i in range(index):
            lastNode = lastNode.next
        return lastNode
    
    def cotnains(self, name):
        lastNode = self.head
        while (lastNode):
            if name == lastNode.key:
                return True
            else:
                lastNode = lastNode.next
        return False

    def isEmpty(self):
        if self.head:
            return False
        else:
            return True

    def deleteIndex(self, index):
        lastNode = self.head
        if index == 0:
            self.head = lastNode.next
            if lastNode.next:
                lastNode.next.prev = None
            self.len -= 1
            return
        lastNode = self.getNode(index)
        
        lastNode.deleteThis()

        del lastNode
        self.len -= 1

    def deleteNode(self, node):
        if node is self.head:
            self.head = node.next
            node.deleteThis()
            self.len -= 1
            return
        node.deleteThis()
        self.len -= 1

    def clear(self):
        for i in range(self.len):
            self.deleteNode(self.head)

class ObjectStorage(storage):
    def __init__(self):
        super().__init__()
        self.handler = EventHandler
        self.objectsList = [CCircle, square, triangle, line]
        self.objectDict = {
            "C" : CCircle,
            "S" : square,
            "T" : triangle,
            "L" : line,
            "G" : Group
    
        }   
        self.lastPressedObj = []
        self.observers = []
        self.obsObjDict = {
        }
    def add(self, x, index = None):
        super().add(x,index)
        self.notifyCreate(x, self.obsObjDict)
        self.handler.Invoke(self, None)
    def clear(self):
        super().clear()
        self.handler.Invoke(self, None)
    def deleteNode(self, node):
        node.key.deleteKeyFromObsObjDict(self.obsObjDict)
        super().deleteNode(node)
    def select(self, node, CtrlPressed):
        if CtrlPressed:
            node.key.setSelect(True)
        else:
            forwardNode = node.next
            prevNode = node.prev
            node.key.setSelect(True)
            while forwardNode:
                forwardNode.key.setSelect(False)
                forwardNode = forwardNode.next
            while prevNode:
                prevNode.key.setSelect(False)
                prevNode = prevNode.prev
        
        self.handler.Invoke(self, None)
    def unSelect(self, node):
        node.key.setSelect(False)
        self.handler.Invoke(self, None)
    def iterationOfSelectedWithFunc(self, func, *args):
        someNode = self.head
        for i in range(self.len):
            if someNode.key.selected:
                func(someNode, *args)
            someNode = someNode.next
    def deleteSelected(self):
        self.iterationOfSelectedWithFunc(self.deleteNode)
        
        self.handler.Invoke(self, None)
    def drawNodeObject(self, node, flagGraphics, drawPen):
        node.key.draw(flagGraphics, drawPen)
    def drawAllObjects(self, flagGraphics, drawPen):
        for i in range(self.len):
            self.drawNodeObject(self.getNode(i), flagGraphics, drawPen)
    def hitNodeInfo(self, node, X, Y):
        return(node.key.checkBorder(X,Y))
    def hitInfo(self, X, Y):
        for i in range(self.len):
            if self.hitNodeInfo(self.getNode(i), X, Y):
                return self.getNode(i)
        return None
    def changeSizeNode(self, node, val):
        node.key.changeSize(val)
        self.handler.Invoke(self, None)
    def changeSizeSelected(self, val):
        self.iterationOfSelectedWithFunc(self.changeSizeNode, val)
    def changeCordsNode(self, node, deltaX, deltaY):
        node.key.changeCords(deltaX,deltaY)
        self.handler.Invoke(self, None)
    def changeCordsSelected(self, deltaX,deltaY):
        self.iterationOfSelectedWithFunc(self.changeCordsNode,deltaX, deltaY)
    def changeColorNode(self, node, color):
        node.key.changeColor(color)
        self.handler.Invoke(self,None)
    def changeColorSelected(self, color):
        self.iterationOfSelectedWithFunc(self.changeColorNode, color)
    def addSelectedInGroup(self, group):
        self.add(group)
        self.iterationOfSelectedWithFunc(group.addFromNode, self.obsObjDict)
        self.deleteSelected()
        group.setSelect(True)
        self.handler.Invoke(self, None)
    
    def unGroupSelected(self):
        someNode = self.head
        for i in range(self.len):
            if someNode.key.selected and someNode.key.__str__() == "Group":
                someNode.key.unGroup(self, self.obsObjDict)
                self.deleteNode(someNode)
            someNode = someNode.next
    def setlastPressedObj(self, X, Y, node):
        self.lastPressedObj = [X,Y, node]
    def save(self, file):
        file.write(str(self.len) + '\n')
        someNode = self.head
        for i in range(self.len):
            someNode.key.save(file)
            someNode = someNode.next
        self.clear()
    def load(self, file):
        for i in range(int(file.readline())):
            someObj = self.objectDict[file.readline().split()[0]]()
            someObj.load(file, self.obsObjDict)
            self.add(someObj)
    def addObserver(self, observer):
        self.observers.append(observer)
    def removeObserver(self, observer):
        self.observers.remove(observer)
    def notifyCreate(self, x, obsObjFict):
        for i in self.observers:
            x.initializeObservers(i,obsObjFict)
    def getWithKey(self, key):
        someNode = self.head
        for i in range(self.len):
            if someNode.key.isMe(key):
                return someNode
            someNode = someNode.next

    

class figure(object):
    def __init__(self, x = 1, y = 1, color = Dr.Color.FromName("DeepSkyBlue"),sticky = False):
        self.xcord = x
        self.ycord = y
        self.color = color

        self.sticky = sticky
        self.stickied = []
        self.selected = False
        self.observers = []
    def checkBorder(self, X, Y): pass
    def changeCords(self, deltaX,deltaY):
        self.xcord += deltaX
        self.ycord += deltaY

        for i in self.stickied:
            i.xcord += deltaX
            i.ycord += deltaY
    def draw(self, flagGraphics, drawPen): pass
    def changeSize(self, val):pass
    def setSelect(self, bol, withNotify = True):
        self.selected = bol
        if withNotify:
            self.notifySelect(bol)
    def getColor(self):
        return self.color
    def changeColor(self, color):
        self.color = color
    def save(self, file): pass
    def load(self, file, *args): pass
    def addObserver(self, observer):
        self.observers.append(observer)
    def removeObserver(self, observer):
        self.observers.remove(observer)
        observer.Remove()
    def notifySelect(self, bol):
        for i in self.observers:
            i.Checked = bol
    def notifyDelete(self):
        for i in range(len(self.observers)):
            self.removeObserver(self.observers[0])
    def initializeObservers(self, parentobs, obsObjFict):
        a = WinForm.TreeNode(self.__str__())
        parentobs.Nodes.Add(a)
        obsObjFict.update({a : self})
        self.addObserver(a)
    def isMe(self, key):
        return key == self
    def deleteKeyFromObsObjDict(self,ddict):
        for j in ddict.items():
            if j[1] == self:
                ddict.pop(j[0])
                break
    def __del__(self):
        self.notifyDelete()

class CCircle(figure):
    def __init__(self, x = 1, y = 1, color = Dr.Color.FromName("DeepSkyBlue"),sticky = False):
        super().__init__(x,y,color,sticky)

        self.rad = 15
    def draw(self, flagGraphics, drawPen):
        drawPen.Color = self.getColor()
        if self.selected:
            flagGraphics.FillEllipse(Dr.Brushes.LightGreen, self.xcord - self.rad, self.ycord-self.rad, self.rad*2,self.rad*2)
        flagGraphics.DrawEllipse(drawPen,self.xcord - self.rad, self.ycord-self.rad, self.rad*2,self.rad*2)
    def checkBorder(self, X, Y):
        if ((self.xcord + self.rad)>X>(self.xcord - self.rad)) and ((self.ycord + self.rad)>Y>(self.ycord - self.rad)):
            return self
        else: return None
    def changeSize(self, val):
        self.rad = 15 + val
    def __str__(self):
        return "Circle"
    def save(self, file):
        file.write("C" + "\n")
        file.write(str(self.xcord)+" "+str(self.ycord)+" "+ str(self.rad)+ " "+self.color.Name+ "\n")
    def load(self, file, *args):
        f = file.readline().split()
        self.xcord, self.ycord, self.rad, self.color = int(f[0]), int(f[1]), int(f[2]), Dr.Color.FromName(f[3])
class square(figure):
    def __init__(self, x = 1, y = 1, color = Dr.Color.FromName("DeepSkyBlue"),sticky = False):
        super().__init__(x,y,color,sticky)

        self.width = 30
        self.height = 30
    def draw(self, flagGraphics, drawPen):
        drawPen.Color = self.getColor()
        if self.selected:
            flagGraphics.FillRectangle(Dr.Brushes.LightGreen, self.xcord, self.ycord, self.width,self.height)
        flagGraphics.DrawRectangle(drawPen,self.xcord, self.ycord, self.width,self.height)
    def checkBorder(self, X,Y):
        if ((self.xcord) < X < (self.xcord + self.width)) and ((self.ycord)<Y<(self.ycord + self.height)):
            return self
        else: return None
    def changeSize(self, val):
        self.width = 30 + val
        self.height = 30 + val
    def __str__(self):
        return "Square"   
    def save(self, file):
        file.write("S" + "\n")
        file.write(str(self.xcord)+" "+str(self.ycord)+" "+ str(self.width)+" "+ str(self.height)+ " "+self.color.Name+ "\n")
    def load(self, file,*args):
        f = file.readline().split()
        self.xcord, self.ycord, self.width, self.height, self.color = int(f[0]), int(f[1]), int(f[2]), int(f[3]),  Dr.Color.FromName(f[4])
class triangle(figure):
    def __init__(self,x = 1, y = 1, color = Dr.Color.FromName("DeepSkyBlue"),sticky = False):
        super().__init__(x,y,color,sticky)

        self.width = 30
        self.height = int(round(self.width*(np.sin(np.deg2rad(60)))))
        self.updatePoints()
    def updatePoints(self):
        self.points = [Dr.Point(self.xcord,self.ycord), Dr.Point(self.xcord+self.width,self.ycord), Dr.Point(self.xcord+(self.width//2), self.ycord+self.height)]
    
    def draw(self, flagGraphics, drawPen):
        drawPen.Color = self.getColor()
        self.updatePoints()
        if self.selected:
            flagGraphics.FillPolygon(Dr.Brushes.LightGreen, self.points)
        flagGraphics.DrawPolygon(drawPen,self.points)
    def checkBorder(self, X, Y):
        if ((self.xcord)<X<(self.xcord + self.width)) and ((self.ycord)<Y<(self.ycord+(X-self.xcord)*np.sqrt(3))):
            return self
        else: return None
    def changeSize(self, val):
        self.width = 30 + val
        self.height = int(round(self.width*(np.sin(np.deg2rad(60)))))
    def __str__(self):
        return "Triangle"       
    def save(self, file):
        file.write("T" + "\n")
        file.write(str(self.xcord)+" "+str(self.ycord)+" "+ str(self.width)+" "+ str(self.height) + " "+self.color.Name+ "\n")
    def load(self, file, *args):
        f = file.readline().split()
        self.xcord, self.ycord, self.width, self.height, self.color = int(f[0]), int(f[1]), int(f[2]), int(f[3]),  Dr.Color.FromName(f[4])
class line(figure):
    def __init__(self, x = 1, y = 1, color = Dr.Color.FromName("DeepSkyBlue"),sticky = False):
        super().__init__(x,y,color,sticky)
        self.lengh = 100
        self.x1 = self.xcord+self.lengh
        self.y1 = self.ycord
    def draw(self, flagGraphics, drawPen):
        drawPen.Color = self.getColor()
        bruh = Dr.Pen(Dr.Brushes.LightGreen)
        bruh.Width = 3
        if self.selected:
            flagGraphics.DrawLine(bruh,self.xcord, self.ycord, self.x1, self.y1)
        flagGraphics.DrawLine(drawPen,self.xcord, self.ycord, self.x1, self.y1)
    def checkBorder(self, X, Y):
        if self.ycord+15 > Y > self.ycord-15:
            return self
        else: return None
    def changeSize(self, val):
        self.lengh = 100 + val
        self.x1 = self.xcord+self.lengh
    def changeCords(self, deltaX,deltaY):
        self.xcord += deltaX
        self.ycord += deltaY
        self.x1 += deltaX
        self.y1 += deltaY
    def __str__(self):
        return "Line"
    def save(self, file):
        file.write("L" + "\n")
        file.write(str(self.xcord)+" "+str(self.ycord)+" "+ str(self.x1)+" "+ str(self.y1) + " "+self.color.Name+ "\n")
    def load(self, file,*args):
        f = file.readline().split()
        self.xcord, self.ycord, self.x1, self.y1, self.color = int(f[0]), int(f[1]), int(f[2]), int(f[3]),  Dr.Color.FromName(f[4])

class Group(figure):
    def __init__(self, object = None):
        self.stor = []
        self.selected = False
        self.observers = []
    def add(self, key, obsObjDict):
        key.deleteKeyFromObsObjDict(obsObjDict)
        key.notifyDelete()
        for i in self.observers:
            key.initializeObservers(i,obsObjDict)
        self.stor.append(key)
    def addFromNode(self, node,obsObjDict):
        node.key.deleteKeyFromObsObjDict(obsObjDict)
        node.key.notifyDelete()
        for i in self.observers:
            node.key.initializeObservers(i,obsObjDict)
        self.stor.append(node.key)
    def checkBorder(self, X, Y):
        for i in self.stor:
            a = i.checkBorder(X, Y)
            if a: return a
    def changeCords(self, deltaX, deltaY):
        for i in self.stor:
            i.changeCords(deltaX, deltaY)
    def changeColor(self, color):
        for i in self.stor:
            i.changeColor(color)
    def draw(self, flagGraphics, drawPen):
        for i in self.stor:
            i.draw(flagGraphics, drawPen)
    def changeSize(self, val):
        for i in self.stor:
            i.changeSize(val)
    def clear(self):
        self.stor.clear()
    def setSelect(self, bol):
        self.selected = bol
        for i in self.stor:
            i.setSelect(bol)
        self.notifySelect(bol)
    def __str__(self):
        return "Group"
    def save(self, file):
        file.write("G" + "\n")
        file.write(str(len(self.stor)) + "\n")
        for i in self.stor:
            i.save(file)
    def load(self, file, obsObjDict):
        for i in range(int(file.readline())):
            objectDict = {
                "C" : CCircle,
                "S" : square,
                "T" : triangle,
                "L" : line
            }
            someObj = objectDict[file.readline().split()[0]](1,1,"DeepBluSky")
            someObj.load(file)
            self.add(someObj, obsObjDict)
    def unGroup(self, storage, obsObjDict):
        for i in self.stor:
            i.deleteKeyFromObsObjDict(obsObjDict)
            storage.add(i)
        self.clear()
        super().deleteKeyFromObsObjDict(obsObjDict)
    def initializeObservers(self, parentobs, obsObjDict):
        super().initializeObservers(parentobs, obsObjDict)
        for i in self.observers:
            for j in self.stor:
                j.initializeObservers(i, obsObjDict)
    def isMe(self, key):
        if self == key:
            return True
        else:
            for i in self.stor:
                if i.isMe(key):
                    return True
    def deleteKeyFromObsObjDict(self,obsObjDict):
        for i in self.stor:
            i.deleteKeyFromObsObjDict(obsObjDict)
        super().deleteKeyFromObsObjDict(obsObjDict)
"""
class advancedTreeNode(WinForm.TreeNode):
    def __init__(self, string):
        super().__init__(string)
        self.observers = []
    def addObserver(self, obs):
        self.observers.append(obs)
    def notifySelect(self, bol):
        for i in self.observers:
            i.setSelect(bol)
"""
class form1(System.Windows.Forms.Form):
    def __init__(self):        
        self.Text = "form"
        self.BackColor = Dr.Color.FromArgb(238,238,238)
        self.ClientSize = Dr.Size(1800,900)
        caption_height = WinForm.SystemInformation.CaptionHeight
        self.MinimumSize =Dr.Size(392,(117 + caption_height))
        self.KeyPreview  = True

        self.CtrlPressed = False
        self.leftBPressed = None

        self.canvas = Dr.Bitmap(1, 1)
        self.flagGraphics = Dr.Graphics.FromImage(self.canvas)
        self.ObjectStorage = ObjectStorage()

        self.drawPen = Dr.Pen(Dr.Brushes.DeepSkyBlue)
        self.drawPen.Color = Dr.Color.FromName("DeepSkyBlue")
        self.drawPen.Width = 2
        
        self.InitiliazeComponent()
        
    def run(self):
        WinForm.Application.Run(self)
    
    def InitiliazeComponent(self):
        self.components = System.ComponentModel.Container()
        self.ImagePB = WinForm.PictureBox()
        self.butt = WinForm.Button()
        self.SwitchObjCB = WinForm.ComboBox()
        self.ChangeSizeSB = WinForm.HScrollBar()
        self.SizeLabel = WinForm.Label()
        self.SwitchColorCB = WinForm.ComboBox()
        self.SwitchColorB = WinForm.Button()
        self.GroupObjB = WinForm.Button()
        self.SaveObjB = WinForm.Button()
        self.LoadObjB = WinForm.Button()
        self.VisualStorTV = WinForm.TreeView()
        self.UnGroupObjB = WinForm.Button()
        self.StickyCB = WinForm.CheckBox()

        self.ObjectStorage.handler = EventHandler(self.drawObjects)

        self.KeyDown += self.Form_KeyDown
        self.KeyUp += self.Form_KeyUp
        #self.MouseDown += self.Form_MouseDown
        #self.MouseUp += self.Form_MouseUp

        self.ImagePB.Location = Dr.Point(10, 10)
        self.ImagePB.Size = Dr.Size(1200, 700)
        self.ImagePB.TabStop = False
        self.ImagePB.BorderStyle = WinForm.BorderStyle.Fixed3D
        self.ImagePB.MouseDown += self.ImagePB_KeyDown
        self.ImagePB.MouseUp += self.ImagePB_MouseUp

        self.butt.Location = Dr.Point(1250+60,480)
        self.butt.Size = Dr.Size(200, 50)
        self.butt.BackColor = Dr.Color.FromArgb(238,238,240)
        self.butt.Text = "Очистить"
        self.butt.UseVisualStyleBackColor = 0
        self.butt.FlatStyle = WinForm.FlatStyle.Flat
        self.butt.FlatAppearance.BorderSize = 0
        self.butt.Click += self.butt_Click

        self.SwitchObjCB.Location = Dr.Point(1250,10)
        self.SwitchObjCB.Size = Dr.Size(300,300)
        self.SwitchObjCB.Sorted = False
        self.SwitchObjCB.Items.AddRange([ "Circle","Square", "Triangle", "Line" ])
        self.SwitchObjCB.SelectedIndex = 2
        self.SwitchObjCB.DropDownStyle = WinForm.ComboBoxStyle.DropDownList

        self.StickyCB.Location = Dr.Point(1600,10)
        self.StickyCB.Size = Dr.Size(300,50)
        self.StickyCB.Text = "Липкая фигура"

        self.SwitchColorCB.Location = Dr.Point(1250,220)
        self.SwitchColorCB.Size = Dr.Size(300,300)
        self.SwitchColorCB.Sorted = False
        self.SwitchColorCB.Items.AddRange([ "Black", "Aqua", "DeepSkyBlue", "Brown", "Coral", "HotPink"])
        self.SwitchColorCB.SelectedIndex = 2
        self.SwitchColorCB.DropDownStyle = WinForm.ComboBoxStyle.DropDownList
        
        self.SwitchColorB.Location = Dr.Point(1250+60,250)
        self.SwitchColorB.Size = Dr.Size(200, 50)
        self.SwitchColorB.BackColor = Dr.Color.FromArgb(238,238,240)
        self.SwitchColorB.Text = "Сменить цвет"
        self.SwitchColorB.UseVisualStyleBackColor = 0
        self.SwitchColorB.FlatStyle = WinForm.FlatStyle.Flat
        self.SwitchColorB.FlatAppearance.BorderSize = 0
        self.SwitchColorB.Click += self.SwitchColorB_Click

        self.GroupObjB.Location = Dr.Point(1250+60,310)
        self.GroupObjB.Size = Dr.Size(200, 50)
        self.GroupObjB.BackColor = Dr.Color.FromArgb(238,238,240)
        self.GroupObjB.Text = "Сгруппировать"
        self.GroupObjB.UseVisualStyleBackColor = 0
        self.GroupObjB.FlatStyle = WinForm.FlatStyle.Flat
        self.GroupObjB.FlatAppearance.BorderSize = 0
        self.GroupObjB.Click += self.GroupObjB_Click

        self.UnGroupObjB.Location = Dr.Point(1250+60+210,310)
        self.UnGroupObjB.Size = Dr.Size(200, 50)
        self.UnGroupObjB.BackColor = Dr.Color.FromArgb(238,238,240)
        self.UnGroupObjB.Text = "Разгруппировать"
        self.UnGroupObjB.UseVisualStyleBackColor = 0
        self.UnGroupObjB.FlatStyle = WinForm.FlatStyle.Flat
        self.UnGroupObjB.FlatAppearance.BorderSize = 0
        self.UnGroupObjB.Click += self.UnGroupObjB_Click

        self.SaveObjB.Location = Dr.Point(1250+60,360)
        self.SaveObjB.Size = Dr.Size(200, 50)
        self.SaveObjB.BackColor = Dr.Color.FromArgb(238,238,240)
        self.SaveObjB.Text = "Сохранить объекты"
        self.SaveObjB.UseVisualStyleBackColor = 0
        self.SaveObjB.FlatStyle = WinForm.FlatStyle.Flat
        self.SaveObjB.FlatAppearance.BorderSize = 0
        self.SaveObjB.Click += self.SaveObjB_Click

        self.LoadObjB.Location = Dr.Point(1250+60,420)
        self.LoadObjB.Size = Dr.Size(200, 50)
        self.LoadObjB.BackColor = Dr.Color.FromArgb(238,238,240)
        self.LoadObjB.Text = "Загрузить объекты"
        self.LoadObjB.UseVisualStyleBackColor = 0
        self.LoadObjB.FlatStyle = WinForm.FlatStyle.Flat
        self.LoadObjB.FlatAppearance.BorderSize = 0
        self.LoadObjB.Click += self.LoadObjB_Click
        
        self.ChangeSizeSB.Location = Dr.Point(1250,50)
        self.ChangeSizeSB.Size = Dr.Size(300,20)
        self.ChangeSizeSB.ValueChanged += self.ChangeSizeSB_ValueChanged

        self.SizeLabel.Location = Dr.Point(1250+120,90)
        self.SizeLabel.Size = Dr.Size(200,20)
        self.SizeLabel.Text = "Size Change"       
        
        self.VisualStorTV.Location = Dr.Point(1250+60,540)
        self.VisualStorTV.Size = Dr.Size(200, 170)
        self.VisualStorTV.CheckBoxes = True
        self.VisualStorTV.NodeMouseClick += self.VisualStorTV_NodeClick
        self.ObjectStorage.addObserver(self.VisualStorTV)
        
        self.Controls.Add(self.ImagePB)
        self.Controls.Add(self.butt)
        self.Controls.Add(self.SwitchObjCB)
        self.Controls.Add(self.ChangeSizeSB)
        self.Controls.Add(self.SizeLabel)
        self.Controls.Add(self.SwitchColorCB)
        self.Controls.Add(self.SwitchColorB)
        self.Controls.Add(self.GroupObjB)
        self.Controls.Add(self.SaveObjB)
        self.Controls.Add(self.LoadObjB)
        self.Controls.Add(self.VisualStorTV)
        self.Controls.Add(self.UnGroupObjB)
        self.Controls.Add(self.StickyCB)
    def dispose(self):
        self.components.Dispose()
        WinForm.Form.Dispose(self)

    def drawObjects(self, sender, args):
        self.ImagePB.Image = None
        self.canvas = Dr.Bitmap(self.ImagePB.Width, self.ImagePB.Height)
        self.flagGraphics = Dr.Graphics.FromImage(self.canvas)

        self.ObjectStorage.drawAllObjects(self.flagGraphics, self.drawPen)

        self.ImagePB.Image = self.canvas

    def Form_KeyDown(self, sender, args):
        if args.KeyCode == WinForm.Keys.ControlKey:
            self.CtrlPressed = True
        if args.KeyCode == WinForm.Keys.Delete:
            self.ObjectStorage.deleteSelected()
    def Form_KeyUp(self, sender, args):
        if args.KeyCode == WinForm.Keys.ControlKey:
            self.CtrlPressed = False
    def ImagePB_MouseUp(self, sender, args):
        if args.Button == WinForm.MouseButtons.Left and self.ObjectStorage.lastPressedObj:
            deltaX = args.X - self.ObjectStorage.lastPressedObj[0]
            deltaY = args.Y - self.ObjectStorage.lastPressedObj[1]
            if (abs(deltaX) > 10 or abs(deltaY) > 10):
                self.ObjectStorage.changeCordsSelected(deltaX, deltaY)
            if self.ObjectStorage.lastPressedObj[2].key.sticky:
                casNode = self.ObjectStorage.lastPressedObj[2].key
                self.ObjectStorage.deleteNode(self.ObjectStorage.lastPressedObj[2])
                casNode2 = self.ObjectStorage.hitInfo(args.X, args.Y)
                if casNode2:
                    self.ObjectStorage.select(casNode2, True)
                    casNode.stickied.append(casNode2.key)
                    self.ObjectStorage.select(casNode2, True)
                self.ObjectStorage.add(casNode)
            self.ObjectStorage.lastPressedObj = None

    def ImagePB_KeyDown(self, sender, args):
        if args.Button == WinForm.MouseButtons.Right:
            self.ObjectStorage.add(self.ObjectStorage.objectsList[self.SwitchObjCB.SelectedIndex](args.X, args.Y, self.drawPen.Color, self.StickyCB.Checked))

        elif args.Button == WinForm.MouseButtons.Left:
            self.leftBPressed = True
            casNode = self.ObjectStorage.hitInfo(args.X, args.Y)
            if casNode:
                self.ObjectStorage.select(casNode, self.CtrlPressed)
                self.ObjectStorage.setlastPressedObj(args.X, args.Y,casNode)


    def ChangeSizeSB_ValueChanged(self, sender, args):
        self.ObjectStorage.changeSizeSelected(self.ChangeSizeSB.Value)
    def SwitchColorB_Click(self, sender, args):
        self.drawPen.Color = Dr.Color.FromName(self.SwitchColorCB.SelectedItem)
        self.ObjectStorage.changeColorSelected(self.drawPen.Color)
    def GroupObjB_Click(self, sender, args):
        self.ObjectStorage.addSelectedInGroup(Group())
    def UnGroupObjB_Click(self, sender, args):
        self.ObjectStorage.unGroupSelected()

    def SaveObjB_Click(self, sender, args):
        f = open('D:\progs\Repository\lr7OOP_Respository\data.txt', 'w')
        self.ObjectStorage.save(f)
        f.close()
    def LoadObjB_Click(self, sender, args):
        f = open('D:\progs\Repository\lr7OOP_Respository\data.txt')             
        self.ObjectStorage.load(f)
        f.close()
    def CheckNodes(self, Node):
        someNode = self.ObjectStorage.getWithKey(self.ObjectStorage.obsObjDict[Node])
        if Node.Checked:
            self.ObjectStorage.select(someNode,True)
        else:
            self.ObjectStorage.unSelect(someNode)
        for i in Node.Nodes:
            self.CheckNodes(i)
    def VisualStorTV_NodeClick(self, sender, args):
        for i in self.VisualStorTV.Nodes:
            self.CheckNodes(i)
        
    def butt_Click(self, sender, args):
        self.ImagePB.Image = None
        self.flagGraphics = Dr.Graphics.FromImage(self.canvas)
        self.ObjectStorage.clear()
        self.canvas = Dr.Bitmap(self.ImagePB.Width, self.ImagePB.Height)




def form_thr():
    form = form1()

    WinForm.Application.Run(form)
    form.dispose()


if __name__ == '__main__':
    form_thr()
