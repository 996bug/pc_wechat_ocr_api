# -*- coding: utf-8 -*-
# ☯ Author  : Anonymous Developer
# ☯ Date    : 2023/11/14 16:22
# ☯ Project : https://github.com/kanadeblisst00/wechat_ocr
# ☯ Warning : For learning purposes only, commercial use prohibited
import logging
from .winapi import *

callbacks_def = {
    # static void DefaultReadOnPush(uint32_t request_id, const void* request_info, void* user_data);
    'kMMReadPush': CFUNCTYPE(void, c_uint32, c_void_p, c_void_p),
    # static void DefaultReadOnPull(uint32_t request_id, const void* request_info, void* user_data);
    'kMMReadPull': CFUNCTYPE(void, c_uint32, c_void_p, c_void_p),
    # static void DefaultReadOnShared(uint32_t request_id, const void* request_info, void* user_data);
    'kMMReadShared': CFUNCTYPE(void, c_uint32, c_void_p, c_void_p),
    # static void DefaultRemoteOnConnect(bool is_connected, void* user_data);
    'kMMRemoteConnect': CFUNCTYPE(void, c_bool, c_void_p),
    # static void DefaultRemoteOnDisConnect(void* user_data);
    'kMMRemoteDisconnect': CFUNCTYPE(void, c_void_p),
    # static void DefaultRemoteOnProcessLaunched(void* user_data);
    'kMMRemoteProcessLaunched': CFUNCTYPE(void, c_void_p),
    # static void DefaultRemoteOnProcessLaunchFailed(int error_code, void* user_data);
    'kMMRemoteProcessLaunchFailed': CFUNCTYPE(void, c_int, c_void_p),
    # static void DefaultRemoteOnMojoError(const void* errorbuf, int errorsize, void* user_data);
    'kMMRemoteMojoError': CFUNCTYPE(void, c_void_p, c_int, c_void_p)
}


def DefaultReadPush(request_id: c_uint32, request_info: c_void_p, user_data: py_object):
    logging.info(f"DefaultReadOnPush Function called, request_id: {request_id}, request_info: {request_info}")


def DefaultReadPull(request_id: c_uint32, request_info: c_void_p, user_data: py_object):
    logging.info(f"DefaultReadOnPull Function called, request_id: {request_id}, request_info: {request_info} ")


def DefaultReadShared(request_id: c_uint32, request_info: c_void_p, user_data: py_object):
    logging.info(f"DefaultReadOnShared Function called, request_id: {request_id}, request_info: {request_info} ")


def DefaultRemoteConnect(is_connected: c_bool, user_data: py_object):
    logging.info(f"DefaultRemoteOnConnect Function called, is_connected: {is_connected}")


def DefaultRemoteDisConnect(user_data: py_object):
    logging.info(f"DefaultRemoteDisConnect Function called ")


def DefaultRemoteProcessLaunched(user_data: py_object):
    logging.info(f"DefaultRemoteProcessLaunched Function called ")


def DefaultRemoteProcessLaunchFailed(error_code: c_int, user_data: py_object):
    logging.info(f"DefaultRemoteProcessLaunchFailed Function called, error_code: {error_code}")


def DefaultRemoteMojoError(errorbuf: c_void_p, errorsize: c_int, user_data: py_object):
    logging.info(f"DefaultRemoteOnMojoError Function called, errorbuf: {errorbuf}, errorsize: {errorsize}")
