import sys
import os
import re
import logging
import argparse
import subprocess
from setuptools import setup, find_packages
from contextlib import contextmanager

ROOT = os.path.dirname(__file__)


def get_long_description():
    with open(os.path.join(ROOT, 'README.md'), encoding='utf-8') as f:
        markdown_txt = f.read()
        return markdown_txt


def get_version():
    VERSION_RE = re.compile(r'''__version__ = ['"]([0-9.]+)['"]''')
    init = open(os.path.join(ROOT, 'sockeye', '__init__.py')).read()
    return VERSION_RE.search(init).group(1)


def get_git_hash():
    try:
        sp = subprocess.Popen(['git', 'rev-parse', 'HEAD'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out_str = sp.communicate()[0].decode("utf-8").strip()
        return out_str
    except:
        return "unkown"


@contextmanager
def temporarily_write_git_hash(git_hash, filename=os.path.join('sockeye', 'git_version.py')):
    """Temporarily create a module git_version in sockeye so that it will be included when installing and packaging."""
    content = """
# This file is automatically generated in setup.py
git_hash = "%s"
""" % git_hash
    if os.path.exists(filename):
        raise RuntimeError("%s already exists, will not overwrite" % filename)
    with open(filename, "w") as out:
        out.write(content)
    try:
        yield
    except:
        raise
    finally:
        os.remove(filename)


def get_requirements(filename):
    with open(os.path.join(ROOT, filename)) as f:
        return [line.rstrip() for line in f]

try:
    from sphinx.setup_command import BuildDoc
    cmdclass = {'build_sphinx': BuildDoc}
except:
    logging.warning("Package 'sphinx' not found. You will not be able to build docs.")
    cmdclass = {}

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('-r', '--requirement', help='Optionally specify a different requirements.txt file.', required=False)
args, unparsed_args = parser.parse_known_args()
sys.argv[1:] = unparsed_args

if args.requirement is None:
    install_requires = get_requirements(os.path.join('requirements', 'requirements.txt'))
else:
    install_requires = get_requirements(args.requirement)

entry_points={
    'console_scripts': [
        'sockeye-autopilot = contrib.autopilot.autopilot:main',
        'sockeye-average = sockeye.average:main',
        'sockeye-embeddings = sockeye.embeddings:main',
        'sockeye-evaluate = sockeye.evaluate:main',
        'sockeye-extract-parameters = sockeye.extract_parameters:main',
        'sockeye-lexicon = sockeye.lexicon:main',
        'sockeye-init-embed = sockeye.init_embedding:main',
        'sockeye-prepare-data = sockeye.prepare_data:main',
        'sockeye-score = sockeye.score:main',
        'sockeye-train = sockeye.train:main',
        'sockeye-translate = sockeye.translate:main',
        'sockeye-rerank = sockeye.rerank:main',
        'sockeye-vocab = sockeye.vocab:main'
    ],
}

args = dict(
    name='sockeye',

    version=get_version(),

    description='Sequence-to-Sequence framework for Neural Machine Translation',
    long_description=get_long_description(),
    long_description_content_type="text/markdown",

    url='https://github.com/awslabs/sockeye',

    author='Amazon',
    author_email='sockeye-dev@amazon.com',
    maintainer_email='sockeye-dev@amazon.com',

    license='Apache License 2.0',

    python_requires='>=3',

    packages=find_packages(exclude=("test",)),

    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-cov', 'pillow'],

    extras_require={
        'optional': ['mxboard', 'matplotlib'],
        'dev': get_requirements(os.path.join('requirements', 'requirements.dev.txt'))
    },

    install_requires=install_requires,

    entry_points=entry_points,

    classifiers = [
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3 :: Only',

    ],

    cmdclass=cmdclass,

)


with temporarily_write_git_hash(get_git_hash()):
    setup(**args)
