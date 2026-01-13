#!/usr/bin/env python3
"""
Fix the generate_all_tests.py file to properly indent multi-line test code.
"""

# Read the file
with open('generate_all_tests.py', 'r') as f:
    content = f.read()

# Replace the problematic line 176
old_code = '''    for i, (name, test_code) in enumerate(s['tests'], 1):
        code += f\'\'\'        try:
            {test_code}
            self.add_result("{name}", True)
        except Exception as e:
            self.add_result("{name}", False, str(e))
\'\'\'
'''

new_code = '''    for i, (name, test_code) in enumerate(s['tests'], 1):
        # Split test_code and properly indent each line
        test_lines = test_code.split('\\n')
        indented_code = '\\n            '.join(test_lines)
        code += f\'\'\'        try:
            {indented_code}
            self.add_result("{name}", True)
        except Exception as e:
            self.add_result("{name}", False, str(e))
\'\'\'
'''

content = content.replace(old_code, new_code)

# Write back
with open('generate_all_tests.py', 'w') as f:
    f.write(content)

print("Fixed generator!")
