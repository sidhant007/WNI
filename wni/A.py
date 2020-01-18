# Print the sum of L1 and prints the number of palindromes in L2, using N = 2
import time
print("MY ID", MY_ID)
if MY_ID == 0:
    L1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    send_data(1, L1[:5])
    send_data(2, L1[5:])

    sum1 = receive_data(1)
    sum2 = receive_data(2)

    print("Total Sum", sum1 + sum2)

elif MY_ID == 1:
    L = receive_data(0)
    sum = 0
    for x in L:
        sum = sum + x
    print("Partial Sum", sum)
    send_data(0, sum)
elif MY_ID == 2:
    L = receive_data(0)
    prod = 1
    for x in L:
        prod = prod * x
    print("Partial Product", prod)
    lol = 0
    for i in range(1, 100000000):
        lol = lol + i
    send_data(0, prod)
