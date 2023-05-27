def factorial(var_test):
    if var_test == 0:
        return 1
    else:
        return var_test * factorial(var_test-1)




if __name__ == "__main__":
    num = int(input("Enter a number: "))
    result = factorial(num)
    print(f"The factorial of {num} is {result}.")