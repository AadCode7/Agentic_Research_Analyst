from setuptools import find_packages, setup
from typing import List

def get_requirements() -> List[str]:
    """Return a list of requirements"""
    
    requirement_list: List[str] = []

    try:
        with open('requirements.txt', 'r') as file:
            lines = file.readlines()

            for line in lines:
                requirement = line.strip()
                if requirement and requirement != '-e .':
                    requirement_list.append(requirement)

    except FileNotFoundError:
        print("Requirements.txt file not found.")


    return requirement_list

print(get_requirements())

setup(
    name = "AI Reasearch Analyst",
    version = "0.0.1",
    author = "AT",
    author_email = "aad.thane88@gmail.com",
    packages = find_packages(),
    install_requires = get_requirements()
)
    
