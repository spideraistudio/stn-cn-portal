"""Guard against CSS hover rules replacing the diagram's positioning transform.
This checks the stylesheet contract; it is not a browser geometry test.
"""
import re,unittest,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def assert_stationary_controls(css):
    css=re.sub(r'/\*.*?\*/','',css,flags=re.S)
    for selectors,body in re.findall(r'([^{}]+)\{([^{}]*)\}',css):
        for selector in selectors.split(','):
            selector=selector.strip()
            # Button box itself; pseudo-elements and child illustrations may animate.
            if re.fullmatch(r'(?:nav\s+)?button(?::(?:hover|active|focus|focus-visible)|:not\(:disabled\))*',selector):
                props={k.strip():v.strip() for k,v in re.findall(r'([\w-]+)\s*:\s*([^;]+)',body)}
                forbidden={'transform','translate','scale','rotate','top','left','right','bottom','margin','padding','width','height','position'}&props.keys()
                if ':' in selector:
                    assert not forbidden, f'{selector} changes button geometry: {forbidden}'
                else:
                    assert not ({'transform','translate','scale','rotate'}&props.keys()),f'{selector} replaces positioned-node geometry'
    nodes=re.findall(r'\.radial-node\s*\{([^{}]+)\}',css)
    assert nodes, 'Missing radial node layout'
    props={k.strip():v.strip() for k,v in re.findall(r'([\w-]+)\s*:\s*([^;]+)',nodes[-1])}
    assert props.get('position')=='absolute', 'Radial nodes lost absolute layout'
    assert props.get('transform')=='translate(-50%,-50%)', 'Radial node centering changed'

class StableControlTests(unittest.TestCase):
 def test_hover_pressed_and_reduced_motion_cannot_override_node_position(self):
    assert_stationary_controls((ROOT/'static/style.css').read_text())
 def test_guard_catches_original_hover_and_pressed_and_reduced_motion_failures(self):
    css=(ROOT/'static/style.css').read_text()
    for rule in ['button:hover:not(:disabled){transform:translateY(-1px)}','button:active:not(:disabled){transform:translateY(0) scale(.985)}','nav button:hover:not(:disabled){transform:translateX(2px)}','@media(prefers-reduced-motion:reduce){button:hover:not(:disabled){transform:none!important}}']:
        with self.assertRaises(AssertionError):assert_stationary_controls(css+'\n'+rule)
