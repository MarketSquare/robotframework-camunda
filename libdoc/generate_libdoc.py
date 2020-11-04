from robot.libdoc import libdoc
import os

def generate_libdoc():
    with os.scandir('./Camunda') as dirs:
        for entry in dirs:
            filename, fileextenstion = os.path.splitext(entry.name)
            if '__init__' != filename and '.py' == fileextenstion:
                libdoc(f'Camunda.{filename}', outfile=f'public/keywords/{filename.lower()}/index.html', version='0.3.4')

if __name__ == '__main__':
    generate_libdoc()
