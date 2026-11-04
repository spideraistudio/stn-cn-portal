"""Compact package selection and atomic publication; no user data is touched."""
import argparse,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import run_local,setup_compact

class CompactRuntimeTests(unittest.TestCase):
    def test_runtime_selection_loopback_env_source_drift_and_platform(self):
        with tempfile.TemporaryDirectory() as temp,patch.object(run_local,'ROOT',Path(temp)):
            root=Path(temp)
            for name in setup_compact.FILES:(root/name).write_text('{}')
            front=root/'runtime/frontend';(front/'.next').mkdir(parents=True)
            (front/'server.js').write_text('server');(front/'.next/BUILD_ID').write_text('build')
            manifest={'frontend_fingerprint':run_local.frontend_fingerprint(),'platform':sys.platform}
            (root/'runtime/compact-manifest.json').write_text(json.dumps(manifest))
            (root/'.env').write_text('IGNORED_TEST=example')
            env={};command=run_local.frontend_command(argparse.Namespace(node_mode='start',node_port=3234),env)
            self.assertEqual(command[-1],str(front/'server.js'));self.assertIn('--env-file='+str(root/'.env'),command)
            self.assertEqual(env['HOSTNAME'],'127.0.0.1');self.assertEqual(env['PORT'],'3234')
            (root/'package.json').write_text('changed')
            with self.assertRaisesRegex(SystemExit,'Run Setup'):run_local.compact_frontend()
            manifest['frontend_fingerprint']=run_local.frontend_fingerprint();manifest['platform']='different'
            (root/'runtime/compact-manifest.json').write_text(json.dumps(manifest))
            with self.assertRaisesRegex(SystemExit,'different operating system'):run_local.compact_frontend()
    def test_atomic_publish_does_not_touch_data(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);old=root/'runtime';old.mkdir();(old/'old').write_text('old')
            stage=root/'stage';stage.mkdir();(stage/'new').write_text('new')
            data=root/'integration-data';data.mkdir();(data/'proof').write_bytes(b'keep')
            setup_compact.publish(stage,old)
            self.assertEqual((old/'new').read_text(),'new');self.assertFalse((old/'old').exists());self.assertEqual((data/'proof').read_bytes(),b'keep')
    def test_failed_publication_restores_previous_runtime(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);old=root/'runtime';old.mkdir();(old/'proof').write_text('old')
            with self.assertRaises(FileNotFoundError):setup_compact.publish(root/'missing-stage',old)
            self.assertEqual((old/'proof').read_text(),'old')
    def test_no_runtime_retains_development_fallback(self):
        with tempfile.TemporaryDirectory() as temp,patch.object(run_local,'ROOT',Path(temp)):
            self.assertIsNone(run_local.compact_frontend())

if __name__=='__main__':unittest.main(verbosity=2)
