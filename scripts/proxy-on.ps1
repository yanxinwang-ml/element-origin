# 开启系统代理（Clash Verge，端口 7897）
# 用法：powershell -ExecutionPolicy Bypass -File scripts\proxy-on.ps1
$port = 7897
$app = 'D:\download\Clash Verge\clash-verge.exe'
if (-not (Get-Process clash-verge -ErrorAction SilentlyContinue)) {
    if (Test-Path $app) {
        Start-Process -FilePath $app
        Start-Sleep -Seconds 8
    } else {
        Write-Host '未找到 Clash Verge，请先启动代理软件'
    }
}
Set-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings' -Name ProxyEnable -Value 1
Set-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings' -Name ProxyServer -Value "127.0.0.1:$port"
Set-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings' -Name ProxyOverride -Value '<local>'
Write-Host "系统代理已开启 -> 127.0.0.1:$port"
