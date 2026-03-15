from lexer import lexer

# Test string with all your main AlphaJ features
test_data = '''
youare x = 10
broadcast "Value is: " x
if x > 5
    broadcast "Success"
end
'''

lexer.input(test_data)

print(f"{'Token Type':<15} | {'Value':<15} | {'Line':<5}")
print("-" * 40)

for tok in lexer:
    print(f"{tok.type:<15} | {tok.value:<15} | {tok.lineno:<5}")