# Print the sum of L1 and prints the number of palindromes in L2, using N = 2
print("Hello World")
print("MY ID", MY_ID)
if MY_ID == 0:
    L1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    send_data(1, L1[:5])
    send_data(2, L1[5:])

    sum1 = receive_data(1)
    sum2 = receive_data(2)

    print("Total Sum", sum1 + sum2)

    L2 = ["aba", "lol", "abc", "def", "ghi", "bob", "sam"]
    send_data(1, L2[:3])
    send_data(2, L2[3:])

    palindromes1 = receive_data(1)
    palindromes2 = receive_data(2)
    print("Total #Palindromes", palindromes1 + palindromes2)

else:
    def is_palindrome(x):
        return x == x[::-1]

    L = receive_data(0)
    s = 0
    for y in L:
        s = s + y
    print("Partial Sum", s)
    send_data(0, s)

    L = receive_data(0)
    s = 0
    for y in L:
        if is_palindrome(y):
            s = s + 1
    print("#Palindromes found", s)
    send_data(0, s)
