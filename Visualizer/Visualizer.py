# -*- coding: utf-8 -*-
"""
EnergyCloudSim Visualizer

테스트환경:
1. OS
   - Ubuntu 20.0.4
2. Language
   - Python3.7.9, Python 3.8.2
3. Python Packages
   - matplotlib, networkx, PyQt5, Pillow, scipy, numpy
4. Library
   - qttools5-dev, qttools5-dev-tools

파일:
1. Visualizer.py  : 실행 파일
2. Visualizer.ui  : QtDesigner 로 생성한 QtUI 구성파일 (Qt Designer 5.12.8)
3. Chart.py : 차트 생성 도구 LineChart, MultiLineChart
4. utils.py : 각종 csv 파일 리더
5. resource.qrc : Visualizer.ui의 리소스 파일
6. resource_rc.py : Visualizer.ui의 리소스 파일( pyrcc5 resource.qrc > ./resource.rc.py)
7. icon.svg: 아이콘 이미지 파일
8. Globals.py : 상수 정의 파일

실행 방법
python3 Visualizer.py
"""
# import modules for system
import sys
import os
import threading, time
from importlib import import_module
import csv
from PyQt5.QtCore import QEvent, QTimer
from PyQt5.QtWidgets import *
from PyQt5 import uic
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.lines import Line2D
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
import warnings

# import modules for simulation engine
"""
from SimulationEngine.Utility.Configurator import Configurator
from SimulationEngine.SimulationEngine import SimulationEngine
from MicroGridSystem import MicroGridSystem
from GridStructure import GridStructure
from Household import Household
"""

# import modules for visualizer
from Globals import FontSize, Globals, NodeSize, EngineStatus
from Chart import LineChart, MultiLineChart
from utils import read_network_data, read_terminal_voltages, read_ess_status, read_active_power_loss, read_transformer_apparent_power

# for ignore ComplexWarning: Casting complex values to real discards the imaginary part
warnings.simplefilter('ignore', RuntimeWarning)

# import form which made by Qt Designer
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
if path not in sys.path:
    sys.path.insert(1, path)

qt_form = uic.loadUiType("Visualizer.ui")[0]


class MainWindow(QMainWindow, qt_form):
    """Main window of Visualizer"""

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        plt_setup()

        self.engineLocationField.setText(os.getcwd())

        self.simulationEngine = None
        self.microgrid = None
        # current household id
        self.household_id = '0'
        # current time of simulation engine
        self.currentTime = 0
        self.engine_status = EngineStatus.NOT_READY

        # thread for running simulation engine
        self.simulation_thread = None
        self.endTimestep = 1440

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timestep_by_timer)
        self.timer.setInterval(200)

    def setupUi(self, mainWindow):
        """
        Setup UI
        :param mainWindow:
        :return:
        """
        super().setupUi(mainWindow)
        self.runButton.setEnabled(False)
        self.pauseButton.setEnabled(False)
        self.runButton.clicked.connect(self.onRunButtonClicked)
        self.initButton.clicked.connect(self.onInitButtonClicked)
        self.pauseButton.clicked.connect(self.onPauseButtonClicked)
        self.endTimestepField.editingFinished.connect(self.onEndTimestepFieldEditingFinished)
        self.comboBox.activated[str].connect(self.onHouseholdCBChanged)
        self.endTimestepField.installEventFilter(self)
        self.engineLocationField.installEventFilter(self)

        # add distribution network canvas
        self.network_fig = plt.Figure()
        self.network_canvas = FigureCanvas(self.network_fig)
        layout = QHBoxLayout(self.networkWidget)
        layout.addWidget(self.network_canvas)

        # add chart canvas  for terminal node voltage changes
        self.terminalvoltage_fig = plt.Figure(figsize=(30, 10))
        self.terminalvoltage_canvas = FigureCanvas(self.terminalvoltage_fig)
        layout = QVBoxLayout(self.widget_9)
        layout.addWidget(self.terminalvoltage_canvas)

        # add chart canvas for voltage changes of each phase
        self.phasevoltage_fig = plt.Figure(figsize=(15, 10))
        self.phasevoltage_canvas = FigureCanvas(self.phasevoltage_fig)
        layout = QVBoxLayout(self.widget_10)
        layout.addWidget(self.phasevoltage_canvas)

        # add chart canvas for power loss
        self.powerloss_fig = plt.Figure(figsize=(15, 10))
        self.powerloss_canvas = FigureCanvas(self.powerloss_fig)
        layout = QVBoxLayout(self.widget_12)
        layout.addWidget(self.powerloss_canvas)

    def onEngineLocationFieldClicked(self, event):
        """
        시뮬레이션 엔진의 경로 QLineEdit(EngineLocationField) 의 Click 핸들러
        :param event: Event
        :return:
        """
        print('EngineLocationField Clicked')
        location = self.engineLocationField.text()
        location = location if os.path.exists(location) else os.getcwd()
        dir = QFileDialog.getExistingDirectory(self, 'Select a SimulationEngine directory', directory=location, options=QFileDialog.ShowDirsOnly)

        if dir.strip() and not os.path.exists(os.path.join(dir, 'SimulationEngine')):
            QMessageBox.information(self, 'EnergyCloudSim',
                                    'The directory has not contains SimulationEngine.',
                                    QMessageBox.Ok)
            dir = location
        elif not dir.strip():
            dir = location

        self.engineLocationField.setText(dir)
        print('PYTHONPATH: {0}'.format(sys.path))
        sys.path.remove(location)
        if dir not in sys.path:
            sys.path.insert(0, dir)

        os.chdir(dir)
        print('PYTHONPATH: {0}'.format(sys.path))

        self.initButton.setText("초기화")
        self.initButton.setEnabled(True)

    def show_household_info(self, household_id):
        """
        터미널노드인 살림집ID 또는 ESSID와 연결된 모선정보를 출력

        :param household_id: 살림짐ID
        :return: None
        """
        if household_id.startswith('E'):

            self.label_3.setText('ESS 상태변화')

            self.householdInfo.setText(
                'ESS ' + household_id + '호 입니다. 모선 ' + str(self.ESS[int(household_id[1:]) - 1][2]) + ' ' +
                Globals.PhaseColor[int(self.ESS[int(household_id[1:]) - 1][3])][
                    1] + '에 연결되어 있습니다.')
            self.householdInfo.setStyleSheet('color:' + Globals.PhaseColor[int(self.ESS[int(household_id[1:]) - 1][3])][0])
        else:
            self.label_3.setText('터미널노드\n전압변화')
            self.householdInfo.setText(
            '살림집 ' + household_id + '호 입니다. 모선 ' + str(self.LD[int(household_id)][1]) + ' ' +
            Globals.PhaseColor[int(self.LD[int(household_id)][2])][
                1] + '에 연결되어 있습니다.')
            self.householdInfo.setStyleSheet('color:' + Globals.PhaseColor[int(self.LD[int(household_id)][2])][0])

    def onHouseholdCBChanged(self, select):
        """
        onChange event handler for Household ComboBox
        :param select: selected household id as string
        :return: None
        """
        self.household_id = select
        self.show_household_info(self.household_id)
        self.redraw_terminal_voltage(self.household_id)

    def update_timestep_by_timer(self):
        """
        시뮬레이션엔진의 현재 Timestep을 출력한다.
        다만, QLabel인 self.curTimestepField에 값을 변경해도 반영되지 않는 문제가 있고,
        :return: None
        """
        self.curTimestepField.setText('{0} min'.format(int(self.currentTime)))

        if self.engine_status is not EngineStatus.RUNNING:
            self.timer.stop()

    def redraw_terminal_voltage(self, household_id):
        """
        터미널노드(살림집) 또는  ESS 노드ID에 따라서, terminalvoltage_canvas 영역에 차트 새로 그림
        :param household_id: 살림집 노드ID 또는 ESS 노드ID
        :return: None
        """
        self.terminalvoltage_fig.clear()
        self.terminalvoltage_canvas.draw()

        if type(household_id) is str and household_id.startswith('E'):
            self.create_ess_status_chart(ess_id=household_id)
            added_ESS = read_ess_status(basedir=Globals.RESULT_DIR, ess_id=household_id,
                                        skiprows=self.ess_status_chart.get_x())
            if added_ESS is not None:
                self.ess_status_chart.update(added_ESS)
        else:
            self.create_terminal_voltage_chart(household_id=household_id)

            LDV = read_terminal_voltages(basedir=Globals.RESULT_DIR, household_id=int(household_id),
                                         skiprows=self.terminal_voltage_chart.get_x())
            if LDV is not None:
                self.terminal_voltage_chart.update(LDV)

    def update_charts(self, household_id):
        """
        모든 차트 업데이트
        새롭게 추가된 데이터를 읽어서 기존 차트에 추가
        다만, 선택된 노드ID(household_id)가 가정집인지 ESS 인지에 따라서 차트를 업데이트 처리함.
        :param household_id: household id as string
        :return:
        """

        added_TRP = read_transformer_apparent_power(Globals.RESULT_DIR, skiprows=self.phasevoltage_chart.get_x())
        added_Loss = read_active_power_loss(Globals.RESULT_DIR, skiprows=self.powerloss_chart.get_x())

        if type(household_id) is str and household_id.startswith('E'):
            added_ESS = read_ess_status(Globals.RESULT_DIR, ess_id=household_id, skiprows=self.ess_status_chart.get_x())

            if added_ESS is not None:
                self.ess_status_chart.update(added_ESS)
        else:
            added_LDV = read_terminal_voltages(basedir=Globals.RESULT_DIR, household_id=int(household_id),
                                           skiprows=self.terminal_voltage_chart.get_x())
            if added_LDV is not None:
                self.terminal_voltage_chart.update(added_LDV)

        self.phasevoltage_chart.update(added_TRP)
        self.powerloss_chart.update(added_Loss)

    def eventFilter(self, widget, event):
        """
        QtApplication에서 발생하는 이벤트 필터링
        :param widget: 이벤트가 발생한 위짓
        :param event: 이벤트
        :return: 부모 이벤트 필터 호출 결과
        """
        if event.type() == QEvent.FocusIn:
            if widget == self.endTimestepField:
                self.onEndTimestepFieldFocusIn(event)

        if event.type() == QEvent.MouseButtonPress:
            if widget == self.engineLocationField:
                self.onEngineLocationFieldClicked(event)

        return super(MainWindow, self).eventFilter(widget, event)

    def closeEvent(self, event):
        """
        Visualizer 종료
        :param event:
        :return:
        """
        result = QMessageBox.question(self,
                                      "EnergyCloudSim",
                                      "정말 종료하시겠습니까?",
                                      QMessageBox.Yes | QMessageBox.No)
        event.ignore()

        if result == QMessageBox.Yes:
            if self.simulation_thread:
                self.engine_status = EngineStatus.STOPPING
                self.simulation_thread.join()
            event.accept()

    def run_simulation(self):
        """
        시뮬레이션엔진 실행
        :return:
        """
        print("Run Button clicked")
        endTimeText = self.endTimestepField.text()
        endTimeText = endTimeText[:endTimeText.rfind(
            'min')].strip() if 'min' in endTimeText else endTimeText if endTimeText and endTimeText.strip() else '0'

        if self.sim_config.getConfiguration('end time') != endTimeText:
            ret = QMessageBox.question(self, 'EnergyCloudSim',
                                       'The end time you input was changed to ' + endTimeText + '\n Do you want to go?',
                                       QMessageBox.Yes | QMessageBox.No)
            if ret == QMessageBox.No:
                return

        self.sim_config.addConfiguration('end time', int(endTimeText))
        self.endTimestep = int(endTimeText)
        self.show_household_info(self.household_id)

        mod_MicroGridSystem = import_module("MicroGridSystem")
        self.microgrid = mod_MicroGridSystem.MicroGridSystem(self.sim_config)

        mod_SimulationEngine = import_module("SimulationEngine.SimulationEngine")
        self.simulationEngine = mod_SimulationEngine.SimulationEngine()
        self.simulationEngine.setOutmostModel(self.microgrid)
        self.simulationEngine.runInitializeForExternal(maxTime=int(endTimeText), logFileName="EnergyCloudSim_log.txt")

        #self.engine_status = EngineStatus.RUNNING
        minTA = 0
        infiniteTime = 10000000000
        maxTime = int(endTimeText)
        while minTA < infiniteTime and self.simulationEngine.getTime() < maxTime:

            if self.engine_status == EngineStatus.STOPPING:
                break

            if self.engine_status == EngineStatus.PAUSE:
                time.sleep(1)
                continue

            self.simulationEngine.runSingleStep()

            engine_time = self.simulationEngine.getTime()
            # print(engine_time)
            if engine_time == int(engine_time) and engine_time < maxTime:
                self.currentTime = engine_time
                self.update_charts(self.household_id)

        self.pauseButton.setEnabled(False)
        self.engine_status = EngineStatus.NOT_READY

    def onRunButtonClicked(self):
        """
        RunButton 클릭이벤트 핸들러
        시뮬레이션엔진 구동 쓰레드 생성 및 구동

        :return:
        """
        print("On runButton clicked")
        if self.simulation_thread == None and self.engine_status == EngineStatus.READY:
            print('Create SimulationEngine running thread.')
            self.runButton.setEnabled(False)
            self.simulation_thread = threading.Thread(target=self.run_simulation)
            self.engine_status = EngineStatus.RUNNING
            self.simulation_thread.start()
        elif self.engine_status == EngineStatus.PAUSE:
            self.engine_status = EngineStatus.RUNNING

        self.timer.start()
        self.pauseButton.setEnabled(True)
        self.runButton.setEnabled(False)

    def readSimulationParametersFromFile(self, parameter_file_path):
        """
        Read simulation parameters from file. And make Configurator object
        :param parameter_file_path:
        :return: Configurator
        """
        mod_Configurator = import_module("SimulationEngine.Utility.Configurator")
        config = mod_Configurator.Configurator()

        f = open(parameter_file_path)
        rdr = csv.reader(f)

        for line in rdr:
            config.addConfiguration(line[0], line[1])

        f.close()
        return config

    def onInitButtonClicked(self):
        """
        Initialize SimulationEngine from the SimParameters.csv file
        :return: None
        """
        print("On InitButton clicked")

        dir = self.engineLocationField.text()
        if dir.strip() and not os.path.exists(os.path.join(dir, 'SimulationEngine')):
            QMessageBox.information(self, 'EnergyCloudSim',
                                    'The directory has not contains SimulationEngine.\nSelect a directory which contains SimulationEngine.',
                                    QMessageBox.Ok)
            return

        self.initButton.setEnabled(False)

        if self.simulation_thread:
            self.engine_status = EngineStatus.STOPPING
            self.simulation_thread.join()
            self.simulation_thread.kill = True

        self.household_id = '0'
        self.currentTime = 0
        self.BS_list, self.BR, self.LD, self.ESS = read_network_data(Globals.DATA_DIR)

        self.sim_config = self.readSimulationParametersFromFile('SimParameters.csv')
        end_time = int(self.sim_config.getConfiguration("end time"))
        self.endTimestepField.setText(str(end_time) + ' min')

        self.phasevoltage_fig.clear()
        self.phasevoltage_canvas.draw()
        self.create_transformer_apparent_power_chart()

        self.terminalvoltage_fig.clear()
        self.terminalvoltage_canvas.draw()
        self.create_terminal_voltage_chart()

        self.powerloss_fig.clear()
        self.powerloss_canvas.draw()
        self.create_power_loss_chart()

        self.network_fig.clear()
        self.network_canvas.draw()

        self.householdInfo.setText('')

        # setup household combobox
        self.comboBox.clear()
        self.comboBox.addItems([str(i) for i in self.LD.keys()])
        self.comboBox.addItems([self.ESS[i][1] for i in self.ESS.keys()])
        self.draw_network(self.BS_list, self.BR, self.LD, self.ESS)

        self.simulation_thread = None
        self.engine_status = EngineStatus.READY

        self.curTimestepField.setText("0 min")
        self.runButton.setEnabled(True)
        self.pauseButton.setEnabled(False)
        self.initButton.setEnabled(True)

    def onPauseButtonClicked(self):
        """
        handler for pause button clicked
        시뮬레이션엔진 일시중지
        :return:
        """
        print("Pause Button clicked")
        self.runButton.setEnabled(True)
        self.engine_status = EngineStatus.PAUSE
        self.pauseButton.setEnabled(False)
        self.runButton.setEnabled(True)

    def onEndTimestepFieldEditingFinished(self):
        """
        handler for endTimestepField editing finished
        시뮬레이션 종료시간 입력이 완료되면 종료시간 뒤에 ' min'을 붙여 출력
        :return:
        """
        print("Editing finished")
        text = self.endTimestepField.text()

        text = text[:text.rfind(
            'min')].strip() + ' min' if 'min' in text else text + ' min' if text and text.strip() else '0 min'
        self.endTimestepField.setText(text)

    def onEndTimestepFieldFocusIn(self, event):
        """
        handler for endTimestepField focus in
        :param event:
        :return:
        """
        print("endTimestempField FocusIn")
        splited = self.endTimestepField.text().split()
        text = ''
        for part in splited:
            if 'min' in part:
                text += part[:part.rfind('min')]
                break
            else:
                text += part

        self.endTimestepField.setText(text)

    def draw_network(self, BS_list, BR, LD, ESS):
        """
        전력배선도 출력

        :param BS_list: 모선 리스트
        :param BR: 모선간 연결 리스트
        :param LD: 살림집과 모선간 관계 리스트
        :param ESS: ESS와 모선, 살림집과의 관계
        :return: None
        """
        BR_list = []
        whole_list = []
        for i in range(len(BR)):
            temp = (BR[i][1], BR[i][2])
            whole_list.append(BR[i][1])
            whole_list.append(BR[i][2])
            BR_list.append(temp)

        ESS_list = []
        for i in range(len(ESS)):
            temp = (ESS[i][1], int(ESS[i][2]))
            ESS_list.append(ESS[i][1])
            BR_list.append(temp)

        whole_list = set(whole_list)
        BS_transformer = [1]

        LD_A_list = []
        LD_B_list = []
        LD_C_list = []

        for i in range(len(LD)):
            LD_info = LD[i]
            color_label = LD_info[2]
            if color_label == 1:
                LD_A_list.append(LD_info[1])
            elif color_label == 2:
                LD_B_list.append(LD_info[1])
            elif color_label == 3:
                LD_C_list.append(LD_info[1])
        not_user_list = []
        chosen_list = [1]

        for i in range(len(LD)):
            LD_info = LD[i]
            name, index = LD_info[1], LD_info[2]
            chosen_list.append(name)

        for username in whole_list:
            if username not in chosen_list:
                not_user_list.append(username)
        G = nx.Graph()
        G.add_nodes_from(ESS_list)
        G.add_nodes_from(BS_list)
        G.add_edges_from(BR_list)

        label_map = {}
        labels = {node: label_map.get(node, 'Transformer') for node in BS_transformer}
        labels.update({node: label_map.get(node, str(node)) for node in LD_A_list})
        labels.update({node: label_map.get(node, str(node)) for node in LD_B_list})
        labels.update({node: label_map.get(node, str(node)) for node in LD_C_list})
        labels.update({node: label_map.get(node, str(node)) for node in not_user_list})
        labels.update({node: label_map.get(node, str(node)) for node in ESS_list})

        values = []
        sizes = []
        label_color = []
        for node in G:
            values.append('k' if node in BS_transformer else 'r' if node in LD_A_list else 'g' if node in LD_B_list else 'b' if node in LD_C_list else 'y' if node in ESS_list else 'slategrey')
            label_color.append(
                'k' if node in LD_A_list else 'k' if node in LD_B_list else 'k' if node in LD_C_list else 'k' if node in ESS_list else 'w')
            sizes.append(
                NodeSize.HOUSEHOLD if node in BS_transformer else NodeSize.HOUSEHOLD if node in LD_A_list else NodeSize.HOUSEHOLD if node in LD_B_list else NodeSize.HOUSEHOLD if node in LD_C_list else NodeSize.ESS if node in ESS_list else NodeSize.DUMMY)

        self.network_fig.clear()

        ax = self.network_fig.gca()

        options = {'edge_color': 'k', 'alpha': 0.85, 'width': 0.7, 'with_labels': True, 'font_size': 7,
                   'font_color': 'w', 'font_weight': 'bold',
                   'edgecolors': 'k'}

        # labels=labels 을 제거한 상태로 출력한다. 변압기를 1번이 아닌 'Transformer'로 출력하려면, draw()에 추가한다.
        nx.draw(G, ax=ax,  node_size=sizes, node_color=values,
                pos=nx.spring_layout(G, k=0.35, iterations=150), **options)

        # nx.draw(G, ax=ax, labels=labels, node_color=values,  **options)
        legend_elements = [
            Line2D([0], [0], marker='o', markersize=10, mec='k', color='k', ls='', label='Transformer'),
            Line2D([0], [0], marker='o', markersize=10, mec='k', color='r', ls='', label='Load (Phase A)'),
            Line2D([0], [0], marker='o', markersize=10, mec='k', color='g', ls='', label='Load (Phase B)'),
            Line2D([0], [0], marker='o', markersize=10, mec='k', color='b', ls='', label='Load (Phase C)'),
            Line2D([0], [0], marker='o', markersize=10, mec='k', color='y', ls='', label='ESS')
        ]

        self.network_fig.legend(handles=legend_elements, scatterpoints=1)
        self.network_canvas.draw()

    def create_ess_status_chart(self, ess_id='E1', max_x=1440):
        """
        ESS 상태(충전, 방전, 보관) 변화 차트 생성
        :param ess_id: ESSID
        :param max_x=1440: 시뮬레이션엔진 최대 종료시간
        :return: None
        """

        self.terminalvoltage_fig.subplots_adjust(hspace=.7)

        options = {'linewidth': 1}

        charging_ax = self.terminalvoltage_fig.add_subplot(311)
        self.charging_chart = LineChart(charging_ax, max_x, 1, ['y'], 'Charge', 'time (m)',
                                               'Charge (kW)')
        discharging_ax = self.terminalvoltage_fig.add_subplot(312)
        self.discharging_chart = LineChart(discharging_ax, max_x, 1, ['y'], 'Discharge', 'time (m)',
                                               'Discharge (kW)')
        storaging_ax = self.terminalvoltage_fig.add_subplot(313)
        self.storaging_chart = LineChart(storaging_ax, max_x, 1, ['y'], 'Storage', 'time (m)',
                                               'Storage (kWH)')

        legend_elements = [
            Line2D([0], [0], color='y', label='Charge')
        ]
        charging_ax.legend(handles=legend_elements, scatterpoints=1, loc='upper right')
        legend_elements = [
            Line2D([0], [0], color='y', label='Discharge')
        ]
        discharging_ax.legend(handles=legend_elements, scatterpoints=1, loc='upper right')
        legend_elements = [
            Line2D([0], [0], color='y', label='Storage')]
        storaging_ax.legend(handles=legend_elements, scatterpoints=1, loc='upper right')

        self.ess_status_chart = MultiLineChart([charging_ax, discharging_ax, storaging_ax], max_x, 3, ['y','y', 'y'],
                                                 None, ['time (m)', 'time (m)', 'time (m)'],
                                               ['Charge', 'Discharge', 'Storage'])

        self.terminalvoltage_canvas.draw()

    def create_terminal_voltage_chart(self, household_id=0, max_x=1440):
        """
        터미널노드 전압변화 차트 생성
        :param household_id: 살림집ID
        :param max_x=1440 : 시뮬레이션엔진 최대 종료시간
        :return: None
        """

        if type(household_id) is str and household_id.startswith('E'):
            return

        ax = self.terminalvoltage_fig.add_subplot(111)
        self.terminal_voltage_chart = LineChart(ax, max_x, 1,
                                                [Globals.PhaseColor[int(self.LD[int(household_id)][2])][2]],
                                                'Customer ' + str(household_id) + ' Voltage', 'time (m)', 'Voltage (V)')

        # lines = ax.plot(np.array(LDV[:, 0], dtype=np.int), np.array(LDV[:, 1], dtype=np.float),
        #        label='Customer ' + str(household_id) + ' Voltage', **options)

        legend_elements = [
            Line2D([], [], color=Globals.PhaseColor[int(self.LD[int(household_id)][2])][2],
                   label='Household {0}'.format(household_id)),
        ]
        # self.terminalvoltage_fig.legend(handles=legend_elements, scatterpoints=1)
        ax.legend(handles=legend_elements, scatterpoints=1, loc='upper right')
        self.terminalvoltage_canvas.draw()

    def create_power_loss_chart(self, max_x=1440):
        """
        전력손실 차트 생성
        :param max_x: 시뮬레이션엔진 최대 종료시간
        :return: None
        """
        ax = self.powerloss_fig.add_subplot(111)
        self.powerloss_chart = LineChart(ax, max_x, 1, ['k'], 'Active Power Loss', 'time (m)', 'Active Power (kW)')

        legend_elements = [
            Line2D([], [], color='k', label='Active Power Loss'),
        ]
        ax.legend(handles=legend_elements, scatterpoints=1, loc='upper right')
        self.powerloss_canvas.draw()

    def create_transformer_apparent_power_chart(self, max_x=1440):
        """
        상별전압변화 차트 생성
        :param max_x: 시뮬레이션엔진 최대 종료 시간
        :return: None
        """
        self.phasevoltage_fig.subplots_adjust(hspace=.7)

        options = {'linewidth': 1}

        phase_a_ax = self.phasevoltage_fig.add_subplot(311)
        self.phase_a_voltage_chart = LineChart(phase_a_ax, max_x, 1, ['r'], 'Transformer Apparent Power', 'time (m)',
                                               'Apparent Power (kVA)')
        phase_b_ax = self.phasevoltage_fig.add_subplot(312)
        self.phase_b_voltage_chart = LineChart(phase_b_ax, max_x, 1, ['g'], 'Transformer Apparent Power', 'time (m)',
                                               'Apparent Power (kVA)')
        phase_c_ax = self.phasevoltage_fig.add_subplot(313)
        self.phase_c_voltage_chart = LineChart(phase_c_ax, max_x, 1, ['b'], 'Transformer Apparent Power', 'time (m)',
                                               'Apparent Power (kVA)')

        legend_elements = [
            Line2D([0], [0], color='r', label='Load (Phase A)')
        ]
        phase_a_ax.legend(handles=legend_elements, scatterpoints=1, loc='upper right')
        legend_elements = [
            Line2D([0], [0], color='g', label='Load (Phase B)')
        ]
        phase_b_ax.legend(handles=legend_elements, scatterpoints=1, loc='upper right')
        legend_elements = [
            Line2D([0], [0], color='b', label='Load (Phase C)')]
        phase_c_ax.legend(handles=legend_elements, scatterpoints=1, loc='upper right')

        self.phasevoltage_chart = MultiLineChart([phase_a_ax, phase_b_ax, phase_c_ax], max_x, 3, None,
                                                 None, ['time (m)', 'time (m)', 'time (m)'],
                                                 ['Apparent Power (kVA)', 'Apparent Power (kVA)', 'Apparent Power (kVA)'])

        self.phasevoltage_canvas.draw()


def plt_setup():
    """
    matplotlib 의 plot 폰트 환경 설정
    :return:
    """
    plt.rc('font', size=FontSize.SMALL_SIZE)
    plt.rc('axes', titlesize=FontSize.SMALL_SIZE)
    plt.rc('axes', labelsize=FontSize.SMALL_SIZE)
    plt.rc('xtick', labelsize=FontSize.SMALL_SIZE)
    plt.rc('ytick', labelsize=FontSize.SMALL_SIZE)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    mainWindow.showMaximized()
    app.exec_()
