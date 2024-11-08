#SingleInstance Force
#NoEnv

^!1::
{
    SetTitleMatchMode, 2
    if WinExist("KoboldAI")
    {
        WinActivate
        WinActivate, KoboldAI
        Send, ^a
        Send, ^c
        WinActivate, Notepad
        Send, ^v
    }
    return
}