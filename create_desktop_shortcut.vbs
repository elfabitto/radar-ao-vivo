Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = oWS.ExpandEnvironmentStrings("%USERPROFILE%") & "\Desktop\Radar ao Vivo.lnk"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = WScript.CreateObject("WScript.Shell").CurrentDirectory & "\dist\Radar ao Vivo.exe"
oLink.WorkingDirectory = WScript.CreateObject("WScript.Shell").CurrentDirectory & "\dist"
oLink.Description = "Radar ao Vivo - Placar de Jogos"
oLink.Save
