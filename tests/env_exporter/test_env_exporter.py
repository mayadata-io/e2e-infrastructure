import sys
import os
sys.path.append(os.getcwd())
from env import env_exporter

class TestEnvExporter:
    def test_maya_invalid_option(self):
        assert env_exporter.get_maya_detail('test', 'none') == None

    def test_maya_mapi_option(self):
        assert env_exporter.get_maya_detail('test', 'mapi') == 'openebs/m-apiserver:test'
    def test_maya_mapi_option_exclude_newline(self):
            assert env_exporter.get_maya_detail('test\n', 'mapi') == 'openebs/m-apiserver:test'

    def test_maya_iovolume_option(self):
        assert env_exporter.get_maya_detail('test', 'iovolume') == 'openebs/m-exporter:test'

    def test_jiva_none(self):
        assert env_exporter.get_jiva_detail('test', 'none') == None

    def test_jiva_jcontroller(self):
        assert env_exporter.get_jiva_detail('test', 'jcontroller') == 'openebs/jiva:test'

    def test_jiva_jcontroller_exclude_newline(self):
        assert env_exporter.get_jiva_detail('test\n', 'jcontroller') == 'openebs/jiva:test'

    def test_jiva_jreplica(self):
        assert env_exporter.get_jiva_detail('test', 'jreplica') == 'openebs/jiva:test'

    def test_cstor_none(self):
        assert env_exporter.get_cstor_detail('test', 'none') == None

    def test_cstor_jcontroller(self):
        assert env_exporter.get_cstor_detail('test', 'cstor') == ['cstor', 'test']

    def test_cstor_jcontroller_exclude_newline(self):
        assert env_exporter.get_cstor_detail('test\n', 'cstor') == ['cstor', 'test']

    def test_docker_image_none_when_file_content_empty(self):
        assert env_exporter.get_docker_image_name_with_tag('tests/env_exporter/empty_maya_file', 'maya') == None

    def test_docker_image_data_for_maya_file(self):
        assert env_exporter.get_docker_image_name_with_tag('tests/env_exporter/test_maya_file', 'mapi') == 'openebs/m-apiserver:20364c17'

    def test_docker_image_data_for_maya_file_no_data(self):
        assert env_exporter.get_docker_image_name_with_tag('tests/env_exporter/test_maya_file', 'none') == None

    def test_docker_image_data_for_jiva_file(self):
        assert env_exporter.get_docker_image_name_with_tag('tests/env_exporter/test_jiva_file', 'jcontroller') == 'openebs/jiva:20364c17'

    def test_docker_image_data_for_cstor_file(self):
        assert env_exporter.get_docker_image_name_with_tag('tests/env_exporter/test_cstor_file', 'cstor') == ['cstor', '20364c17']

