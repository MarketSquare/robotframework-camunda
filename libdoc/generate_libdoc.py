from robot.libdoc import libdoc
import os
import re

module_name = 'CamundaLibrary'

# determine version number from environment
version_regex = r"^v(?P<version>\d*\.\d*\.\d*$)"
version = os.environ.get('CI_COMMIT_TAG', f'0-{os.environ.get("CI_COMMIT_REF_NAME","dev")}')
full_version_match = re.fullmatch(version_regex, version)
if full_version_match:
    version = full_version_match.group('version')


def generate_libdoc():
    with os.scandir(f'./{module_name}') as dirs:
        for entry in dirs:
            filename, fileextenstion = os.path.splitext(entry.name)
            if '__init__' != filename and '.py' == fileextenstion:
                libdoc(f'{module_name}.{filename}',
                       outfile=f'public/latest/keywords/{filename.lower()}/index.html',
                       version=version)
                libdoc(f'{module_name}.{filename}',
                       outfile=f'public/{version}/keywords/{filename.lower()}/index.html',
                       version=version)


if __name__ == '__main__':
    generate_libdoc()
