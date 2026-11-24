$ErrorActionPreference = 'Stop'
$app = [Runtime.InteropServices.Marshal]::GetActiveObject('Visio.Application')
$app.Visible = $true
if($app.ActiveWindow){
    $app.ActiveWindow.WindowState = 2
    $app.ActiveWindow.Activate()
}
