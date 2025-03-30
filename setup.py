from setuptools import setup, find_packages

setup(
    name='editor_assistant',
    version='0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            #'convert2md=editor_assistant.convert_to_md:main',
            'summarize_research=editor_assistant.summarizer:summarize_research',
            'summarize_news=editor_assistant.summarizer:summarize_news',
        ],
    },
    install_requires=[
        'markitdown',
        'requests',
        'argparse',
        'python-dotenv'
        # add other dependencies
    ]
)