' =====================================================
' 一键启动前后端服务脚本
' 功能: 杀掉旧进程 -> 启动前端 -> 启动后端(预留)
' 特性: 静默运行，无黑框弹窗
' =====================================================

Option Explicit

Dim WshShell, FSO, strCurDir
Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")
strCurDir = FSO.GetParentFolderName(WScript.ScriptFullName)

' 切换到项目目录
WshShell.CurrentDirectory = strCurDir

' -----------------------------------------------------
' Step 1: 杀掉已有进程
' -----------------------------------------------------
KillProcess "node.exe"      ' Node.js 进程
KillProcess "cmd.exe"       ' CMD 窗口

WScript.Sleep 500

' -----------------------------------------------------
' Step 2: 启动前端 (Vue3 + Vite)
' -----------------------------------------------------
' 使用冷门端口 14514，隐藏窗口运行
Dim frontendCmd
frontendCmd = "cmd /c cd /d """ & strCurDir & "\frontend"" && npm run dev >nul 2>&1"
WshShell.Run frontendCmd, 0, False

WScript.Sleep 1000

' -----------------------------------------------------
' Step 3: 启动后端 (预留)
' -----------------------------------------------------
' 目前后端目录为空，暂不启动
' 后续可在 backend 目录添加服务后取消注释下面代码:
'
' Dim backendCmd
' backendCmd = "cmd /c cd /d """ & strCurDir & "\backend"" && npm run dev >nul 2>&1"
' WshShell.Run backendCmd, 0, False

' -----------------------------------------------------
' 完成提示 (可选，注释掉下面行可完全静默)
' -----------------------------------------------------
' MsgBox "服务已启动!" & vbCrLf & "前端: http://localhost:14514", 64, "启动成功"

Set WshShell = Nothing
Set FSO = Nothing

' =====================================================
' 函数: 杀掉指定进程
' =====================================================
Sub KillProcess(processName)
    On Error Resume Next
    Dim objWMIService, colProcess, objProcess
    Set objWMIService = GetObject("winmgmts:{impersonationLevel=impersonate}!\\.\root\cimv2")
    Set colProcess = objWMIService.ExecQuery("Select * from Win32_Process Where Name = '" & processName & "'")
    
    For Each objProcess in colProcess
        objProcess.Terminate()
    Next
    
    Set colProcess = Nothing
    Set objWMIService = Nothing
    On Error GoTo 0
End Sub
