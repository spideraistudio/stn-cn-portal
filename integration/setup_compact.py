"""Build in a temporary workspace; retain traced runtime only. Never touches data."""
import json,os,platform,shutil,subprocess,sys,tempfile,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'integration'))
from run_local import frontend_fingerprint
FOLDERS=('app','components','lib','hooks','db','public','vendor','scripts')
FILES=('package.json','package-lock.json','.npmrc','next.config.ts','tsconfig.json','next-env.d.ts','postcss.config.mjs','components.json','proxy.ts')
def run(command,cwd,env):subprocess.run(command,cwd=cwd,env=env,check=True)
def tree_bytes(folder):return sum(p.stat().st_size for p in folder.rglob('*') if p.is_file())
def publish(stage,destination):
    backup=destination.with_name('runtime-rollback-'+uuid.uuid4().hex)
    if destination.exists():destination.rename(backup)
    try:stage.rename(destination)
    except BaseException:
        if backup.exists():backup.rename(destination)
        raise
    # Only setup-generated runtime files are removed after successful promotion.
    if backup.exists():shutil.rmtree(backup)
def main():
    if not shutil.which('node') or not shutil.which('npm'):raise SystemExit('Install Node.js including npm first.')
    fingerprint=frontend_fingerprint()
    lock=ROOT/'.compact-setup.lock'
    try:fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    except FileExistsError:raise SystemExit('Another compact setup is active. Close it before retrying; see COMPACT_WINDOWS_UPDATE.md for interrupted setup recovery.')
    os.close(fd)
    stage=ROOT/('runtime-stage-'+uuid.uuid4().hex)
    try:
        # Temp lives under this installation for an atomic same-volume promotion.
        with tempfile.TemporaryDirectory(prefix='.compact-build-',dir=ROOT) as temporary:
            build=Path(temporary)
            for folder in FOLDERS:
                if (ROOT/folder).exists():shutil.copytree(ROOT/folder,build/folder)
            for name in FILES:
                if (ROOT/name).exists():shutil.copyfile(ROOT/name,build/name)
            (build/'integration').mkdir()
            for name in ('mongo_local.mjs','trace_runtime_tools.mjs'):
                shutil.copyfile(ROOT/'integration'/name,build/'integration'/name)
            env={**os.environ,'CN_COMPACT_BUILD':'1','NEXT_PUBLIC_COMMON_PORTAL':'1','NEXT_TELEMETRY_DISABLED':'1'}
            # Build tools are required temporarily. Never omit dev dependencies here.
            env.pop('NODE_ENV',None)
            npm=shutil.which('npm')
            # Windows .cmd launchers require cmd.exe; fixed arguments contain no user text.
            command=([os.environ.get('COMSPEC','cmd.exe'),'/d','/c','npm.cmd'] if os.name=='nt' else [npm])
            run(command+['ci','--include=dev','--ignore-scripts'],build,env)
            run(command+['run','build'],build,env)
            standalone=build/'.next/standalone'
            if not (standalone/'server.js').is_file():raise RuntimeError('Standalone server was not generated')
            stage.mkdir();shutil.copytree(standalone,stage/'frontend',symlinks=False)
            shutil.copytree(build/'.next/static',stage/'frontend/.next/static',dirs_exist_ok=True)
            if (build/'public').exists():shutil.copytree(build/'public',stage/'frontend/public',dirs_exist_ok=True)
            run(['node','integration/trace_runtime_tools.mjs',str(stage/'tools')],build,env)
            if not (stage/'tools/integration/mongo_local.mjs').is_file():raise RuntimeError('Mongo launcher was not traced')
            if (stage/'frontend/.next/cache').exists():shutil.rmtree(stage/'frontend/.next/cache')
            if any(p.is_symlink() for p in stage.rglob('*')):raise RuntimeError('Runtime contains a link to build files')
            (stage/'compact-manifest.json').write_text(json.dumps({'format':1,'platform':sys.platform,'architecture':platform.machine(),'frontend_fingerprint':fingerprint,'node_version':subprocess.check_output(['node','--version'],text=True).strip(),'runtime_bytes':tree_bytes(stage)},indent=2)+'\n')
            if frontend_fingerprint()!=fingerprint:raise RuntimeError('Source changed while building. Retry setup.')
            publish(stage,ROOT/'runtime')
        size=tree_bytes(ROOT/'runtime')/1048576
        print(f'Compact runtime ready: {size:.1f} MiB. Temporary build dependencies/cache removed.',flush=True)
        print('No saved integration-data or old root node_modules/.next folders were modified. Use a NEW extracted folder to avoid retaining those old build folders.',flush=True)
    finally:
        if stage.exists():shutil.rmtree(stage)
        lock.unlink(missing_ok=True)
if __name__=='__main__':main()
