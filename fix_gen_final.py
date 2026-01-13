#!/usr/bin/env python3
"""
Properly fix the generator to handle newlines in test code
"""
import re

with open('generate_all_tests.py', 'r') as f:
    content = f.read()

# Find and replace the problematic section
# The issue is that {test_code} contains literal \n strings that need to be split and indented

pattern = r"(    for i, \(name, test_code\) in enumerate\(s\['tests'\], 1\):.*?code \+= f''')"
replacement = r"""    for i, (name, test_code) in enumerate(s['tests'], 1):
        # Properly indent multi-line test code
        test_lines = test_code.split('\\n')
        indented_test = '\\n            '.join(test_lines)
        code += f'''"""

# Replace the section
content_fixed = re.sub(
    r"for i, \(name, test_code\) in enumerate\(s\['tests'\], 1\):\n        code \+= f'''",
    """for i, (name, test_code) in enumerate(s['tests'], 1):
        # Properly indent multi-line test code
        test_lines = test_code.split('\\\\n')
        indented_test = '\\\\n            '.join(test_lines)
        code += f'''""",
    content
)

# Also replace {test_code} with {indented_test}
content_fixed = content_fixed.replace('{indented_code}', '{indented_test}')

with open('generate_all_tests.py', 'w') as f:
    f.write(content_fixed)

print("Generator fixed!")
