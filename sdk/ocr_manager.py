# -*- coding: utf-8 -*-
# ☯ Author  : Anonymous Developer
# ☯ Date    : 2023/11/14 16:22
# ☯ Project : https://github.com/kanadeblisst00/wechat_ocr
# ☯ Warning : For learning purposes only, commercial use prohibited

import os
import time
import logging
from enum import Enum
from typing import Dict, Callable
from multiprocessing import Queue, Value
from google.protobuf.json_format import MessageToJson

from . import ocr_protobuf_pb2
from .winapi import *
from .mmmojo_dll import MMMojoInfoMethod
from .xplugin_manager import XPluginManager

OCR_MAX_TASK_ID = 32


class RequestIdOCR(Enum):
    OCRPush = 1


def OCRRemoteOnConnect(is_connected: c_bool, user_data: py_object):
    logging.info(f"OCRRemoteOnConnect Function called, is_connected: {is_connected}")
    if user_data:
        manager_obj: OcrManager = cast(user_data, py_object).value
        manager_obj.SetConnectState(True)


def OCRRemoteOnDisConnect(user_data: py_object):
    logging.info(f"OCRRemoteOnDisConnect Function called ")
    if user_data:
        manager_obj: OcrManager = cast(user_data, py_object).value
        manager_obj.SetConnectState(False)


def OCRReadOnPush(request_id: c_uint32, request_info: c_void_p, user_data: py_object):
    logging.info(f"OCRReadOnPush Function called, request_id: {request_id}, request_info: {request_info}")
    if user_data:
        manager_obj: OcrManager = cast(user_data, py_object).value
        pb_size = c_uint32()
        pb_data = manager_obj.GetPbSerializedData(request_info, pb_size)
        if pb_size.value > 10:
            logging.info(f"Parsing Model, Model size: {pb_size.value}")
            manager_obj.CallUsrCallback(request_id, pb_data, pb_size.value)
            manager_obj.RemoveReadInfo(request_info)


class OcrManager(XPluginManager):
    m_task_id = Queue(OCR_MAX_TASK_ID)
    m_id_path: Dict[int, str] = {}
    m_usr_lib_dir: str = None
    m_wechatocr_running: bool = False
    m_connect_state: Value = Value('b', False)
    m_usr_callback: Callable = None

    def __init__(self, wechat_path) -> None:
        super().__init__(wechat_path)
        for i in range(1, 33):
            self.m_task_id.put(i)

    def __del__(self):
        if self.m_wechatocr_running:
            self.KillWeChatOCR()

    def SetUsrLibDir(self, usr_lib_dir: str):
        self.m_usr_lib_dir = usr_lib_dir
        self.AppendSwitchNativeCmdLine("user-lib-dir", usr_lib_dir)

    def SetOcrResultCallback(self, func: Callable):
        self.m_usr_callback = func

    def StartWeChatOCR(self):
        self.SetCallbackUsrData(self)
        self.InitMMMojoEnv()
        self.m_wechatocr_running = True

    def KillWeChatOCR(self):
        self.m_connect_state.value = False
        self.m_wechatocr_running = False
        self.StopMMMojoEnv()

    def DoOCRTask(self, pic_path: str):
        if not self.m_wechatocr_running:
            raise Exception("Please call OCR first to start")
        if not os.path.exists(pic_path):
            raise Exception(f"Image does not exist: {pic_path}")
        pic_path = os.path.abspath(pic_path)
        while not self.m_connect_state.value:
            logging.info("Waiting for Ocr service to connect successfully!")
            time.sleep(1)
        _id = self.GetIdleTaskId()
        if not _id:
            logging.info("The current queue is full, please wait and try again")
            return
        self.SendOCRTask(_id, pic_path)

    def SetConnectState(self, connect: bool):
        self.m_connect_state.value = connect

    def SendOCRTask(self, task_id: int, pic_path: str):
        self.m_id_path[task_id] = pic_path
        ocr_request = ocr_protobuf_pb2.OcrRequest()
        ocr_request.unknow = 0
        ocr_request.task_id = task_id

        pic_paths = ocr_request.pic_path
        pic_paths.pic_path.extend([pic_path])
        serialized_data = ocr_request.SerializeToString()
        self.SendPbSerializedData(serialized_data, len(serialized_data), MMMojoInfoMethod.kMMPush.value, 0,
                                  RequestIdOCR.OCRPush.value)

    def CallUsrCallback(self, request_id: c_uint32, serialized_data: c_void_p, data_size: int):
        ocr_response_ubyte = (c_ubyte * data_size).from_address(serialized_data)
        ocr_response_array = bytearray(ocr_response_ubyte)
        ocr_response = ocr_protobuf_pb2.OcrResponse()
        ocr_response.ParseFromString(ocr_response_array)
        json_response = MessageToJson(ocr_response)
        task_id = ocr_response.task_id
        if not self.m_id_path.get(task_id):
            return
        pic_path = self.m_id_path[task_id]
        if self.m_usr_callback:
            self.m_usr_callback(pic_path, json_response)
        self.SetTaskIdIdle(task_id)

    def GetIdleTaskId(self):
        task_id = self.m_task_id.get(timeout=1)
        return task_id

    def SetTaskIdIdle(self, _id):
        self.m_task_id.put(_id)

    def SetDefaultCallbaks(self):
        super().SetOneCallback("kMMRemoteConnect", OCRRemoteOnConnect)
        super().SetOneCallback("kMMRemoteDisconnect", OCRRemoteOnDisConnect)
        super().SetOneCallback("kMMReadPush", OCRReadOnPush)
        super().SetDefaultCallbaks()
