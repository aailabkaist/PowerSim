# -*- coding: utf-8 -*-
"""
EnergyCloudSim Visualizer

"""

from enum import Enum


class Globals:
    """
    전역 상수 정의
    """
    PhaseColor = {1: ['red', '빨강', 'r'], 2: ['green', '초록', 'g'], 3: ['blue', '파랑', 'b']}
    DATA_DIR = 'data'
    RESULT_DIR = 'result'


class FontSize:
    """
    matplotlib의 plt 설정용 폰트 크기 정의
    """
    SMALL_SIZE = 8
    MEDIUM_SIZE = 10
    LARGE_SIZE = 12


class NodeSize:
    """
    전력배선도 내 노드 크기
    household와 household가 아닌 노드인 dummy 노드로 구분
    """
    HOUSEHOLD = 250
    ESS = 200
    DUMMY = 150


class EngineStatus(Enum):
    """
    Declare status of simulation engine
    """
    NOT_READY = 1
    READY = 2
    RUNNING = 3
    PAUSE = 4
    STOPPING = 5
