#!/usr/bin/python
# -*- coding: utf-8 -*-
# Insonmia REST client parser
"""
Insomnia REST client JSON config parser
Convert Insmonia JSON exported files to MD, for documentation
https://insomnia.rest/
"""

import sys
import os
import json
import click
from pathlib import Path

__version__ = '0.2.0'
__updated__ = '2019-01-31'


class Insomia(object):

    "Insomnia class"

    def __init__(self, filename, destination):
        self.filename = filename
        self.destination = destination
        self.title = None

    def export(self):
        "Read the JSON file and export it"
        # get file content
        content = self.__get_content(self.filename)
        self.title = content[0]['name']
        # fill the resources
        resources = self.__get_resources(content)
        self.__convert(resources, self.destination)

    def __get_content(self, filename):
        "Check if the file exists and read it"
        if self.__check_file(filename):
            file_contents = open(filename, 'r')
            json_contents = json.loads(file_contents.read())
            return json_contents['resources']
        # error
        print('Error reading file')
        sys.exit(1)

    @staticmethod
    def __get_resources(entries):
        "Parse the json"
        resources = {}
        # the resources
        for entry in entries:
            if entry['_type'] == 'request_group' and entry['_id'] not in resources:
                resources[entry['_id']] = {
                    'name': entry['name'],
                    'requests': []
                }
        # the requests
        for entry in entries:
            if entry['_type'] == 'request':
                request = {
                    'name': entry['name'],
                    'method': entry['method'],
                    'url': entry['url'],
                    'description': entry['description'],
                    'parameters': [],
                    'body': None
                }
                for parameter in entry['parameters']:
                    request['parameters'].append('{0}={1}'.format(
                        parameter['name'],
                        parameter['value']
                    ))
                if 'text' in entry['body']:
                    request['body'] = entry['body']['text']
                resources[entry['parentId']]['requests'].append(request)
        return resources

    def __convert(self, resources, destination):
        "Convert dictionary to files"
        index = []
        for resource in resources:
            entry = resources[resource]
            md_filename = self.__md_filename(entry['name'])
            index.append({
                'name': entry['name'],
                'url': md_filename
            })
            # the doc file
            self.__gen_doc(entry, md_filename, destination)

        # the index
        self.__index(self.title, index, destination)

    @staticmethod
    def __index(title, index, destination):
        "Generate index"
        index_file = os.path.join(destination, 'README.md')
        md_file = open(index_file, 'w')
        # title
        md_file.write(title + '\n')
        md_file.write('=' * len(title))
        md_file.write('\n\n')
        # index
        md_file.write('## Indice\n')
        md_file.write('\n')
        for entry in index:
            md_file.write('1. [{0}](./{1})\n'.format(entry['name'], entry['url']))
        md_file.close()

    @staticmethod
    def __gen_doc(entry, filename, destination):
        doc_file = os.path.join(destination, filename)
        md_file = open(doc_file, 'w')
        # title
        title = entry['name']
        md_file.write(title + '\n')
        md_file.write('=' * len(title))
        md_file.write('\n\n')
        # menu
        for endpoint in entry['requests']:
            md_file.write('* [{0}](#{1})\n'.format(endpoint['name'], endpoint['name'].lower().replace(' ', '-')))
        # break
        md_file.write('\n\n')
        # entries
        for endpoint in entry['requests']:
            md_file.write('## {0}\n'.format(endpoint['name']))
            md_file.write('\n')
            md_file.write('__Description__: {0}.  \n'.format(endpoint['description']))
            md_file.write('__Method__: `{0}`  \n'.format(endpoint['method']))
            md_file.write('__URL__: `{0}`  \n'.format(endpoint['url']))
            if len(endpoint['parameters']):
                md_file.write('__Query parameters__: `{0}`  \n'.format('&'.join(endpoint['parameters'])))
            md_file.write('__Payload__:  \n')
            if endpoint['body']:
                md_file.write('```  \n')
                md_file.write('{0}\n'.format(endpoint['body']))
                md_file.write('```  \n')
            # response
            md_file.write('\n')
            md_file.write('__Response ok:__\n')
            md_file.write('\n')
            md_file.write('```  \n')
            md_file.write('```  \n')
            md_file.write('\n')
            md_file.write('__Response error:__\n')
            md_file.write('\n')
            md_file.write('```  \n')
            md_file.write('[]   \n')
            md_file.write('```  \n')
            md_file.write('\n')
        md_file.close()

    @staticmethod
    def __md_filename(filename):
        filename = filename.lower().replace(' ', '_')
        filename = filename.replace('á', 'a')
        filename = filename.replace('é', 'e')
        filename = filename.replace('í', 'i')
        filename = filename.replace('ó', 'o')
        filename = filename.replace('ú', 'u')
        filename = filename.replace('ñ', 'n')
        return '%s.md' % filename

    @staticmethod
    def __check_file(path, is_dir=False):
        "Check if a file or dir exists"
        to_check = Path(path)
        # check if exists
        if not to_check.exists():
            return False
        # check if is dir
        if is_dir:
            return to_check.is_dir()
        return to_check.is_file()


def about_self():
    "About this script"
    print('Convert Insmonia JSON exported files to MD, for documentation')
    print('Author Fausto Carrera <fausto.carrera@gmx.com>')
    print('Version %s' % __version__)
    print('Last update %s' % __updated__)
    sys.exit(0)


@click.command()
@click.option(
    '-i',
    '--input',
    'input',
    type=click.Path(exists=True),
    help='Insomnia JSON source'
)
@click.option(
    '-o',
    '--output',
    'output',
    type=click.Path(exists=True),
    default='./',
    help='Destination MD files, default is current folder'
)
@click.option(
    '--about',
    'about',
    default=False,
    is_flag=True,
    help='About insomnia md generator'
)
def run(input, output, about):
    "Convert Insmonia JSON exported files to MD, for documentation."
    # about
    if about:
        about_self()
    # export
    if input:
        Insomnia = Insomia(input, output)
        Insomnia.export()
    else:
        print('Use --help')


if __name__ == '__main__':
    run()
