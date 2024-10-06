import os
import sys
import servicemanager
import win32event
import win32service
import win32serviceutil
import traceback
import time

class MyService(win32serviceutil.ServiceFramework):
    _svc_name_ = "PythonService"
    _svc_display_name_ = "Python Service"
    _svc_description_ = "Testing PythonService"
    _svc_type_ = win32service.SERVICE_AUTO_START

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        # Signal the service to stop
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        # Log service start
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, servicemanager.PYS_SERVICE_STARTED, (self._svc_name_, ''))
        try:
            self.main()
        except Exception as e:
            # Log any exception that occurs
            servicemanager.LogErrorMsg(f"Service failed: {e}\n{traceback.format_exc()}")
def main(self):
    try:
        servicemanager.LogInfoMsg('Starting Service...')
        import yolo2ocr
        servicemanager.LogInfoMsg('yolo2ocr imported successfully.')
        yolo2ocr.main()
        servicemanager.LogInfoMsg('yolo2ocr.main() executed.')
        # Add a delay to ensure the service has time to report back
        time.sleep(5)  
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
    except Exception as e:
        servicemanager.LogErrorMsg(f"Error in main: {e}\n{traceback.format_exc()}")

if __name__ == '__main__':
   if len(sys.argv) > 1:
       # Called by Windows shell. Handling arguments such as: Install, Remove, etc.
       win32serviceutil.HandleCommandLine(MyService)
   else:
       # Called by Windows Service. Initialize the service to communicate with the system operator
       servicemanager.Initialize()
       servicemanager.PrepareToHostSingle(MyService)
       servicemanager.StartServiceCtrlDispatcher()
else:
    # Handle command line options like install, update, remove, etc.
    win32serviceutil.HandleCommandLine(MyService)

