
 ' -----------------------------------------------------------------------------
 ' Help: Creating a Femap button for a Python script
 '
 ' This example creates a Femap button named after this BAS file. Place the
 ' BAS file in a subfolder within Femap's API directory, for example:
 '   C:\Program Files\Siemens\Femap\api\python\example_femap_button.BAS
 '
 ' Before running the button, update these two values below:
 '   1. pythonExe  - the full path to python.exe, or "python" when Python is
 '                   available on PATH.
 '   2. scriptPath - the full path to the Python script to run.
 '
 ' Keep the paths in quotes when they contain spaces. The command is built with
 ' quotes automatically, so the paths should be entered without extra quotes.
 ' The button starts the Python script while Femap remains open. Any output is
 ' shown in the Python console window.
 ' -----------------------------------------------------------------------------

Sub Main
    Dim App As femap.model
    Set App = feFemap()

    ' 1. Define the path to your Python executable (python.exe)
    ' If Python is in your PATH, you can just use "python"
    Dim pythonExe As String
    pythonExe = "C:\Users\AhaanBhosalePontisEn\Documents\Repositories\femap-api-python\venv\Scripts\python.exe"

    ' 2. Define the path to your Python script
    Dim scriptPath As String
    scriptPath = "C:\Users\AhaanBhosalePontisEn\Documents\Repositories\femap-api-python\src\composites\create_oop_shear_failure_index.py"

    ' 3. Construct the command
    ' We use double quotes around paths in case they contain spaces
    Dim command As String
    command = """" & pythonExe & """ """ & scriptPath & """"

    ' 4. Run the script
    ' vbNormalFocus ensures you see the console window if it prints anything
    On Error Resume Next
    Shell(command, vbNormalFocus)

    If Err.Number <> 0 Then
        App.feAppMessage(FCM_ERROR, "Failed to launch Python script: " & Err.Description)
    Else
        App.feAppMessage(FCM_NORMAL, "Python script initiated...")
    End If
End Sub