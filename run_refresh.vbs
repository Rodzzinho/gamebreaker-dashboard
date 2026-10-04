Set sh = CreateObject("WScript.Shell")
sh.CurrentDirectory = "C:\Users\RODNE\gb_clv_dashboard"
sh.Run """C:\Python314\pythonw.exe"" ""C:\Users\RODNE\gb_clv_dashboard\build_data.py""", 0, False
