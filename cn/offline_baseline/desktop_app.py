"""Optional native WebView2 window around the same loopback application and stores."""
from pathlib import Path
import os,sys,threading

def run_desktop(webview=None):
    if webview is None:
        try:import webview
        except ImportError:raise RuntimeError('Desktop window is not installed yet. Run Setup_Desktop.bat once, then Start_Desktop.bat.')
    import app
    server=app.ThreadingHTTPServer(('127.0.0.1',0),app.Handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    url='http://127.0.0.1:'+str(server.server_address[1])+'/'
    class Bridge:
        def __init__(self):self.window=None;self.allowed=False;self.loaded=False
        def finish_close(self):
            if self.window and (self.window.get_current_url() or '').split('#')[0].startswith(url):
                self.allowed=True;self.window.destroy();return True
            return False
        def closing(self):
            if self.allowed or not self.loaded:return True
            # Return from the native closing callback before marshaling JS to its UI thread.
            script="if(globalThis.cnSaveAndClose){globalThis.cnSaveAndClose();}else{alert('The app is still loading. Try closing again in a moment.');}"
            threading.Thread(target=self.window.run_js,args=(script,),daemon=True).start()
            return False
        def ready(self):self.loaded=True
    bridge=Bridge()
    try:
        webview.settings['ALLOW_DOWNLOADS']=True
        webview.settings['ALLOW_FILE_URLS']=False
        window=webview.create_window('All Crop CN · Payment & Territory Studio',url,js_api=bridge,width=1460,height=940,min_size=(1040,680),maximized=True,background_color='#eaf5ef',text_select=True)
        bridge.window=window
        window.events.loaded+=bridge.ready;window.events.closing+=bridge.closing
        storage=Path(app.DATA_ROOT)/'desktop-profile';storage.mkdir(parents=True,exist_ok=True)
        webview.start(gui='edgechromium' if sys.platform=='win32' else None,private_mode=False,storage_path=str(storage),icon=str(app.ROOT/'static'/'app.ico'))
    finally:server.shutdown();server.server_close();thread.join(timeout=3)

if __name__=='__main__':
    try:run_desktop()
    except Exception as exc:
        message='Desktop launch stopped: '+str(exc)+'\nThe modern Windows window requires Microsoft Edge WebView2 Runtime. Your existing Start_Calculator.bat still works.'
        print(message,flush=True)
        if sys.platform=='win32':
            import ctypes
            ctypes.windll.user32.MessageBoxW(0,message,'All Crop CN desktop launch',0x10)
        raise SystemExit(1)
