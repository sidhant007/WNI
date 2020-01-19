# Prints the list of those numbers that are perfect
# (i.e the sum of whose proper factors is equal to the numer itself)
# in the range [1, 9999], using 3 other PCs (for demo: All 3 are running as independent droplets on DigitalOcean)
N = 9999
P = 3
print("MY_ID", MY_ID)
def is_perfect(x): # a boolean function to check if a number is perfect or not
    sum = 0
    for i in range(1, x):
        if((x % i) == 0):
            sum = sum + i
    return (sum == x)

if MY_ID == 0: # root code of sending ranges
    for i in range(0, P):
        l = (N // P) * i + 1
        r = (N // P) * (i + 1)
        send_data(i + 1, (l, r)) # send the tuple (l, r) to node i + 1.
    ans = []
    for i in range(0, P):
        p = receive_data(i + 1) # receive lists from all the 3 slaves
        ans = ans + p # concatenate them
    print("List of perfect numbers in range [1, 9999]:", ans)
else: # slaves code which do the computation
    (l, r) = receive_data(0) # receives the tuple from node 0.
    ans = []
    for i in range(l, r + 1):
        if is_perfect(i):
            ans.append(i)
    print("List of perfect numbers found in range [", l, ", ", r, "]:", ans)
    send_data(0, ans) # send list to node 0
