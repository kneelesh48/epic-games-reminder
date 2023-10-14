# Add program to Task Scheduler
$taskName = "Epic Games Reminder"
$trigger =  New-ScheduledTaskTrigger -Weekly -DaysOfWeek Thursday -At 8:30pm
$action = New-ScheduledTaskAction -Execute $(get-command pythonw).Source -Argument '.\main.py' -WorkingDirectory $(Get-Location)

$taskExists = Get-ScheduledTask | Where-Object {$_.TaskName -like $taskName }
if($taskExists) {
    Write-Output "Task already exists"
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

Register-ScheduledTask -TaskName $taskName -Trigger $trigger -Action $action -Description "Sends reminder to buy free epic games every Thursday"

Write-Output "Finished adding program to Task Scheduler"
