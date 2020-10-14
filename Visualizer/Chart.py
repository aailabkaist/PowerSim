# -*- coding: utf-8 -*-
"""
EnergyCloudSim Visualizer

"""


class LineChart:
    """
    라인차트 초기화 및 추가 데이터를 통한 업데이트
    """
    options = {'linewidth': 1}
    colors = ['r', 'g', 'b']

    def __init__(self, ax, max_x, num_series, colors=None, title=None, xlabel=None, ylabel=None, options=None):
        self.ax = ax
        self.max_x = max_x
        self.xdata = []
        self.ydata = []
        self.num_series = num_series

        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel

        self.ax.set_xlabel(self.xlabel, labelpad=0)
        self.ax.set_ylabel(self.ylabel)
        self.ax.set_title(self.title)

        if colors is not None:
            if len(colors) is not num_series:
                raise Exception('라인개수와 컬러개수가 일치하지 않습니다.')
            self.colors = colors

        if options is not None:
            LineChart.options = options

        self.series = []
        for series in range(self.num_series):
            self.ydata.append([])
            self.series += self.ax.plot(self.xdata, self.ydata[series], self.colors[series], **LineChart.options)

    def update(self, added):
        if added.ndim == 1:
            return self.series

        self.xdata += added[:, 0].tolist()

        for series in range(self.num_series):
            self.ydata[series] += added[:, series + 1].tolist()
            self.series[series].set_xdata(self.xdata)
            self.series[series].set_ydata(self.ydata[series])

        self.ax.relim()
        self.ax.autoscale_view()
        self.ax.figure.canvas.draw()

        return self.series

    def get_x(self):
        if len(self.ydata) > 0:
            return len(self.ydata[0])
        return 0

    def __del__(self):
        del self.xdata
        del self.ydata


class MultiLineChart:
    """
    복수의 라인차트 초기화 및 추가 데이터를 통한 업데이트
    """
    options = {'linewidth': 1}
    colors = ['r', 'g', 'b']

    def __init__(self, ax, max_x, num_series, colors=None, title=None, xlabel=None, ylabel=None, options=None):
        self.ax = ax
        self.max_x = max_x
        self.xdata = []
        self.ydata = []
        self.num_series = num_series

        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel

        for series in range(self.num_series):
            self.ax[series].set_xlabel(self.xlabel[series], labelpad=0)
            self.ax[series].set_ylabel(self.ylabel[series])
            self.ax[series].set_title(self.title)

        if colors is not None:
            if len(colors) is not num_series:
                raise Exception('라인개수와 컬러개수가 일치하지 않습니다.')
            self.colors = colors

        if options is not None:
            LineChart.options = options

        self.lines = []
        for series in range(self.num_series):
            self.ydata.append([])
            self.lines += self.ax[series].plot(self.xdata, self.ydata[series], self.colors[series], **LineChart.options)

    def update(self, added):
        if added.ndim == 1:
            return self.lines

        self.xdata += added[:, 0].tolist()

        for series in range(0, self.num_series):
            self.ydata[series] += added[:, series + 1].tolist()

        for series in range(self.num_series):
            self.lines[series].set_xdata(self.xdata)
            self.lines[series].set_ydata(self.ydata[series])

        for series in range(self.num_series):
            self.ax[series].relim()
            self.ax[series].autoscale_view()

        self.ax[0].figure.canvas.draw()
        return self.lines

    def get_x(self):
        if len(self.ydata) > 0:
            return len(self.ydata[0])
        return 0

    def __del__(self):
        del self.xdata
        del self.ydata
