# Prints the list of those numbers that are perfect (i.e the sum of whose proper factors is equal to the numer itself) in the range [1, 9999], using N = 3
print("MY_ID", MY_ID)
def is_perfect(x):
    sum = 0
    for i in range(1, x):
        if((x % i) == 0):
            sum = sum + i
    return (sum == x)

if MY_ID == 0:
    for i in range(0, 3):
        send_data(i + 1, (3333*i + 1, 3333*(i + 1)))
    ans = []
    for i in range(0, 3):
        p = receive_data(i + 1)
        ans = ans + p
    print(ans)
else:
    (l, r) = receive_data(0)
    ans = []
    for i in range(l, r + 1):
        if is_perfect(i):
            ans.append(i)
    print("I found", ans)
    send_data(0, ans)
