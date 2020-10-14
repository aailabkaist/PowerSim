# -*- coding: utf-8 -*-
"""
EnergyCloudSim Visualizer

"""

import os
import numpy as np


def read_network_data(basedir):
    """
    전력 배선도 네트워크 생성 데이터 적재
    관련 파일(EnergyCloudSim project의  data directory에 존재
    BS.csv : 모선 정보
    BR.csv : 모선간 연결 정보
    LD.csv : Household와 모선 관계
    ESS_spec.csv : ESS와 모선, Household간 관계 및 ESS 설정정보
    :param basedir: 관련파일 경로
    :return: BS_list, BR_dic, LD_dic, ESS_dic
    """
    BR_file = os.path.join(basedir, 'BR.csv')
    BS_file = os.path.join(basedir, 'BS.csv')
    LD_file = os.path.join(basedir, 'LD.csv')
    ESS_file = os.path.join(basedir, 'ESS_spec.csv')

    BR = np.loadtxt(BR_file, skiprows=1, delimiter=',', dtype='int')
    BS = np.loadtxt(BS_file, skiprows=0, delimiter=',', dtype='int')
    LD = np.loadtxt(LD_file, skiprows=0, delimiter=',', dtype='int')
    ESS = np.loadtxt(ESS_file, skiprows=1, delimiter=',', dtype='str')

    BS_list = BS.tolist()
    BR_dic = {}
    for i in range(len(BR)):
        # 모선 연결 정보로 source, target 정보
        BR_dic[i] = [i, BR[i][0], BR[i][1]]

    LD_dic = {}
    for i in range(len(LD)):
        # i 번째 household의 모선정보(BS)와 Phase 정보
        LD_dic[i] = [i, LD[i][0], LD[i][1]]

    ESS_dic = {}
    for i in range(len(ESS)):
        # i 번째 ESS의 ID, 모선정보(BS),  Phase , household, Power(W), Efficiency(%), Nominal Voltage(V), Capacity(Wh),
        # charge Starttime(min), charge Endtime(min)
        ESS_dic[i] = [i, ESS[i][0], ESS[i][1], ESS[i][2], ESS[i][3], ESS[i][4], ESS[i][5], ESS[i][6], ESS[i][7], ESS[i][8],
                      ESS[i][9]]

    return BS_list, BR_dic, LD_dic, ESS_dic


def read_terminal_voltages(basedir, household_id, skiprows=0):
    """
    LDV_[household id].csv: 터미널노드 전압변화 파일 내용을 읽어서 반환
    다만, 건너뛸 라인 수를 입력 받아 해당하는 기존에 읽었던 부분은 건너뛰도록 구현

    :param basedir: 파일 경로
    :param household_id: 터미털노드(Household) ID
    :param skiprows: 건너뛸 라인 수
    :return: ndarray 형태의 전압변화 내용
    """

    # set skiprows
    skiprows += 1

    file = os.path.join(basedir, 'LDV_' + str(household_id) + '.csv')
    if os.path.isfile(file) and os.access(file, os.R_OK):
        loaded = np.loadtxt(file, skiprows=skiprows, delimiter=',', dtype='float')
    else:
        return None

    if len(loaded) > 1 and loaded.ndim == 1:
        loaded = loaded.reshape(1, len(loaded))

    # return loaded[np.where(0. == loaded[:, 0])[0][-1]:] if len(loaded) > 0 else loaded
    return loaded


def read_ess_status(basedir, ess_id, skiprows=0):
    """
    ESS_E[ess id]_totalE.csv: ESS노드 상태변화 파일 내용을 읽어서 반환
    다만, 건너뛸 라인 수를 입력 받아 해당하는 기존에 읽었던 부분은 건너뛰도록 구현

    :param basedir: 파일경로
    :param ess_id: ESS노드 ID
    :param skiprows: 건너뛸 라인 수
    :return: ndarray 형태의 ESS 상태변화 내용
    """
    skiprows += 1

    try:
        file = os.path.join(basedir, 'ESS_' + ess_id + '_totalE.csv')
        if os.path.isfile(file) and os.access(file, os.R_OK):
            loaded = np.loadtxt(file, skiprows=skiprows, delimiter=',', dtype='float')
        else:
            raise Exception('File not found or Cannot acces to a {0} file'.format(file))
    except Exception as err:
        raise err

    if len(loaded) > 1 and loaded.ndim == 1:
        loaded = loaded.reshape(1, len(loaded))

    return loaded


def read_transformer_apparent_power(basedir, skiprows=0):
    """
    TR_P.csv: 상 별 전압변화 파일 내용을 읽어서 반환

    :param basedir: 파일 경로
    :param skiprows: 건너뛸 라인 수
    :return: ndarray 형태의 상 별 전압변화 내용
    """

    skiprows += 1
    try:
        file = os.path.join(basedir, 'TR_P.csv')
        if os.path.isfile(file) and os.access(file, os.R_OK):
            loaded = np.loadtxt(file, skiprows=skiprows, delimiter=',', dtype='float')
        else:
            raise Exception('File not found or Cannot access to a {0} file'.format(file))
    except Exception as err:
        raise err

    if len(loaded) > 1 and loaded.ndim == 1:
        loaded = loaded.reshape(1, len(loaded))

    return loaded


def read_active_power_loss(basedir, skiprows=0):
    """
    P_Loss.csv: 전력손실 파일 내용을 읽어서 반환

    :param basedir: 파일 경로
    :param skiprows: 건너뛸 라인 수
    :return: ndarray 형태의 전력손실 변화 내용
    """
    skiprows += 1
    try:
        file = os.path.join(basedir, 'P_Loss.csv')
        if os.path.isfile(file) and os.access(file, os.R_OK):
            loaded = np.loadtxt(file, skiprows=skiprows, delimiter=',', dtype='float')
        else:
            raise Exception('File not found or Cannot access to a {0} file'.format(file))
    except Exception as err:
        raise err

    if len(loaded) > 1 and loaded.ndim == 1:
        loaded = loaded.reshape(1, len(loaded))

    return loaded
