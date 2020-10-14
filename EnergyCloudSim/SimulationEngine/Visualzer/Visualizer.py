import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as ss
from matplotlib.animation import FuncAnimation

class Visualizer:

    def __init__(self,engine,timeout):
        self.engine = engine
        self.timeout = timeout
        fig = plt.figure()
        plt.axes(xlim=(-15,170),ylim=(-15,150))

        runner = SimulationRunnerForVisualizer(self.engine,plt,fig)
        anim = FuncAnimation(fig, runner.runSingleStep, frames=timeout, interval=100, blit=True, repeat=False)
        plt.show()

class SimulationRunnerForVisualizer(object):
    def __init__(self, engine, plt,fig):
        self.engine = engine
        self.plt = plt
        self.fig = fig

        self.plot = plt.scatter([],[],c=[])
        self.txtTime = plt.text(-10, -10, '', fontsize=15)
        self.lines = []
        for i in range(100):
            line, = plt.plot([], [])
            self.lines.append(line)

    def runSingleStep(self,i):

        self.engine.runSingleStep()

        retVisualNodes = self.engine.getVisualNodes()
        retVisualEdges = self.engine.getVisualEdges()

        self.txtTime.set_text('Simulation Time : ' + str(self.engine.getTime()))
        if len(retVisualNodes) != 0:
            self.showModelXY(retVisualNodes)
        if len(retVisualEdges) != 0:
            self.showModelLine(retVisualNodes,retVisualEdges)

        return tuple(self.lines)+(self.plot,)+(self.txtTime,)

    def showModelLine(self,retVisualNodes,retVisualEdges):
        dicNode = {}
        for node in retVisualNodes:
            dicNode[node.name] = node

        x = []
        y = []
        cnt = 0
        for edge in retVisualEdges:
            if edge.srcName in dicNode and edge.tarName in dicNode:
                x.append(dicNode[edge.srcName].x)
                x.append(dicNode[edge.tarName].x)
                y.append(dicNode[edge.srcName].y)
                y.append(dicNode[edge.tarName].y)
                self.lines[cnt].set_data(x,y)
                cnt = cnt + 1

        for j in range(cnt,len(self.lines)):
            self.lines[j].set_data([],[])

    def showModelXY(self,retVisualNodes):
        xys = []
        sizes = []
        colors = []
        annotations = []
        for node in retVisualNodes:
            xys.append([node.x,node.y])
            sizes.append(node.size)
            colors.append(node.color)
            annotations.append(node.name)

        self.plot.set_offsets(xys)
        self.plot._sizes = np.array(sizes)
        self.plot.set_array(np.array(colors))

class VisualNode:
    def __init__(self, name, x, y, size, color):
        self.name = name
        self.x = x
        self.y = y
        self.size = size
        self.color = color

class VisualEdge:
    def __init__(self, srcName, tarName):
        self.srcName = srcName
        self.tarName = tarName