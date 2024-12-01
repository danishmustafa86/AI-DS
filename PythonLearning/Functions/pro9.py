# 3. Write a function to check whether a string is a palindrome.

def is_palindrome(string):
    cleaned_string = ''.join(char.lower() for char in string if char.isalnum())
    
    return cleaned_string == cleaned_string[::-1]

# Example usage:
test_string = "A man, a plan, a canal: Panama"
if is_palindrome(test_string):
    print(f'"{test_string}" is a palindrome.')
else:
    print(f'"{test_string}" is not a palindrome.')
