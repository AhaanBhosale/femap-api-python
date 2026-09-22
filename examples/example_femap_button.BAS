
 ' -----------------------------------------------------------------------------
 ' Help: Creating a Femap button for the create-model workflow
 '
 ' This example creates a Femap button named after this BAS file and runs
 ' src\create_model\main.py as a Python module. Place the BAS file in a
 ' subfolder within Femap's API directory, for example:
 '   C:\Program Files\Siemens\Femap\api\python\example_femap_button.BAS
 '
 ' Setup steps:
 '   1. Confirm that run_create_model.bat is in the repository root.
 '   2. Update the Python executable path in run_create_model.bat if needed.
 '   3. Update launcherPath below to the full path to that batch file.
 '   4. Copy this BAS file into Femap's API subfolder and run the button.
 '
 ' The batch file changes to the repository root before running:
 '   python -m src.create_model.main
 ' This package-style command is required because main.py uses relative imports.
 ' The batch file pauses when complete so errors and console output remain visible.
 ' -----------------------------------------------------------------------------

Sub Main
    Dim App As femap.model
    Set App = feFemap()

    ' 1. Define the path to the batch launcher in the repository root
    Dim launcherPath As String
    launcherPath = "C:\Users\AhaanBhosalePontisEn\Documents\Repositories\femap-api-python\run_create_model.bat"

    ' 2. Construct the command
    ' The quotes allow the launcher path to contain spaces.
    Dim command As String
    command = "cmd.exe /c " & """" & launcherPath & """"

    ' 3. Run the launcher
    ' vbNormalFocus ensures you see the console window if it prints anything
    On Error Resume Next
    Shell(command, vbNormalFocus)

    If Err.Number <> 0 Then
        App.feAppMessage(FCM_ERROR, "Failed to launch Python script: " & Err.Description)
    Else
        App.feAppMessage(FCM_NORMAL, "Python script initiated...")
    End If
End Sub