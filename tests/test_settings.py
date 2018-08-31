# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
import pytest
import os

from scarab.settings import Settings

BARE_CONFIG = '''
[default]
url = server
api_key = key
'''

INVALID_CONFIG = '''
[default]
url = server
api_key = key

[template:a]
foo = bar
'''

FULL_CONFIG = '''
[default]
url = server
api_key = key

[template:a]
product = product a
component = component a
version = version a

[template:b]
version = version b
severity = severity b
'''

@pytest.yield_fixture
def bare_config_path(tmpdir):
    path = os.path.join(tmpdir, 'scarabrc')
    with open(path, 'w+') as f:
        f.write(BARE_CONFIG)
    yield path
    os.unlink(path)

@pytest.yield_fixture
def full_config_path(tmpdir):
    path = os.path.join(tmpdir, 'scarabrc')
    with open(path, 'w+') as f:
        f.write(FULL_CONFIG)
    yield path
    os.unlink(path)

@pytest.yield_fixture
def invalid_config_path(tmpdir):
    path = os.path.join(tmpdir, 'scarabrc')
    with open(path, 'w+') as f:
        f.write(INVALID_CONFIG)
    yield path
    os.unlink(path)

def test_defaults(monkeypatch):
    def mockexpand(path):
        return '/do/not/exist'
    monkeypatch.setattr(os.path, 'expanduser', mockexpand)
    settings = Settings()
    assert settings.url() is not None
    assert settings.api_key() is None

def test_valid_config(bare_config_path):
    settings = Settings(bare_config_path)
    assert settings.url() == 'server/'
    assert settings.api_key() == 'key'

def test_single_template(full_config_path):
    settings = Settings(full_config_path)
    template = settings.template('a')
    assert template['product'] == 'product a'
    assert template['component'] == 'component a'
    assert template['version'] == 'version a'

def test_combine_templates(full_config_path):
    settings = Settings(full_config_path)
    template = settings.combine_templates(['a', 'b'])
    assert template['product'] == 'product a'
    assert template['component'] == 'component a'
    assert template['version'] == 'version b'
    assert template['severity'] == 'severity b'

def test_invalid_template(invalid_config_path):
    with pytest.raises(Settings.InvalidTemplateKey) as ex:
        settings = Settings(invalid_config_path)
    assert ex.value.key == 'foo'
    assert ex.value.section == 'template:a'
