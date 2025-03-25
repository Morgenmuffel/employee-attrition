from setuptools import setup, find_packages

def get_requirements(file_path='requirements.txt'):
    with open(file_path) as f:
        requirements = [line.strip() for line in f if not line.startswith('-') and line.strip()]
    return requirements

setup(
    name="employee_attrition",
    version="0.1",
    packages=find_packages(),
    python_requires='>=3.8',
    install_requires=get_requirements(),
    extras_require={
        'dev': get_requirements('requirements.txt'),
        'prod': get_requirements('requirements_prod.txt')
    },
    author="Yulia Vilensky",
    description="Employee Attrition Prediction System",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)
