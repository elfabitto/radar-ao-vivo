Set WshShell = CreateObject("WScript.Shell")
strDesktop = WshShell.SpecialFolders("Desktop")
Set oShellLink = WshShell.CreateShortcut(strDesktop & "\Radar ao Vivo.lnk")
oShellLink.TargetPath = WshShell.CurrentDirectory & "\start-radar.bat"
oShellLink.WorkingDirectory = WshShell.CurrentDirectory
oShellLink.Save
