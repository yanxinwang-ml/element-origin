# 关闭系统代理
# 用法：powershell -ExecutionPolicy Bypass -File scripts\proxy-off.ps1
Set-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings' -Name ProxyEnable -Value 0
Write-Host '系统代理已关闭'
