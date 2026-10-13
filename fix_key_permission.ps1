$path = '<workspace>\opencodes\id_ed25519_1panel-160'
$acl = Get-Acl $path
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule('DEMO\user', 'FullControl', 'Allow')
$acl.AddAccessRule($rule)
Set-Acl $path $acl
Write-Host 'Permission fixed successfully'
