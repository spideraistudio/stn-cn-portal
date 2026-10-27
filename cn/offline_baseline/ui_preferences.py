"""Non-financial appearance preferences; isolated from financial records/settings."""
from pathlib import Path
import hashlib,json,math,os,tempfile,time

THEMES={'classic','studio'}

def _read(path,default):
    try:
        if path.stat().st_size>4*1024*1024:return default
        value=json.loads(path.read_text(encoding='utf-8'))
        return value if isinstance(value,dict) else default
    except (OSError,ValueError):return default

def _write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix='ui-pref-',dir=path.parent)
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as f:
            json.dump(value,f,ensure_ascii=False,separators=(',',':'),allow_nan=False)
            f.flush();os.fsync(f.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)

def _key(workbook,record_id):
    if not isinstance(record_id,str) or not 1<=len(record_id)<=200:raise ValueError('Save this calculation before storing a layout.')
    return hashlib.sha256(json.dumps([workbook,record_id],ensure_ascii=False).encode()).hexdigest()

def preferences(main_dir,project_dir,workbook,body=None,record_id=''):
    theme_file=Path(main_dir)/'ui-theme.json';layout_file=Path(project_dir)/'ui-layouts.json'
    current=_read(theme_file,{})
    theme=current.get('theme','classic')
    if not isinstance(theme,str) or theme not in THEMES:theme='classic'
    layouts=_read(layout_file,{})
    # Validate the complete request before writing any preference file.
    if body is not None:
        if not isinstance(body,dict) or set(body)-{'theme','record_id','layout','reset'}:raise ValueError('Unsupported UI preference')
        if 'theme' in body and body['theme'] not in THEMES:raise ValueError('Choose Classic or Navy Studio')
        record_id=body.get('record_id','')
        if 'layout' in body or body.get('reset'):
            key=_key(workbook,record_id)
            if body.get('reset'):
                layouts.pop(key,None)
            else:
                layout=body['layout']
                if not isinstance(layout,dict) or set(layout)-{'positions','locked'}:raise ValueError('Invalid layout')
                if 'locked' in layout and not isinstance(layout['locked'],bool):raise ValueError('Invalid layout lock')
                positions=layout.get('positions')
                if not isinstance(positions,list) or len(positions)>1000:raise ValueError('Layout supports at most 1000 cards')
                clean=[];seen=set()
                for p in positions:
                    if not isinstance(p,dict) or set(p)!={'key','x','y'}:raise ValueError('Invalid card position')
                    if not isinstance(p['key'],str) or not 1<=len(p['key'])<=600 or p['key'] in seen:raise ValueError('Invalid or duplicate card identity')
                    if any(isinstance(p[v],bool) or not isinstance(p[v],(int,float)) or not math.isfinite(p[v]) or abs(p[v])>100000 for v in ('x','y')):raise ValueError('Invalid card coordinate')
                    seen.add(p['key']);clean.append({k:p[k] for k in ('key','x','y')})
                layouts[key]={'positions':clean,'locked':layout.get('locked',False),'updated_at':time.time_ns()}
                # Never silently evict another party's saved layout.
                if len(json.dumps(layouts,ensure_ascii=False).encode('utf-8'))>4*1024*1024:
                    raise ValueError('Layout storage is full; existing layouts were preserved.')
            _write(layout_file,layouts)
        if 'theme' in body:
            theme=body['theme'];_write(theme_file,{'theme':theme})
    layout=layouts.get(_key(workbook,record_id)) if record_id else None
    return {'theme':theme,'layout':layout if isinstance(layout,dict) else None,'record_id':record_id}
