"""Test file for Sara to fix"""


def calculate_average(numbers):
    """Calculate the average of a list of numbers"""
    total = 0
    for num in numbers:
        total = total + num
    return total / len(numbers)


def greet(name):
    """Greet a person"""
    print("Hello " + name)


def find_maximum(items):
    """Find the maximum value in a list"""
    max_val = items[0]
    for item in items:
        if item > max_val:
            max_val = item
    return max_val


if __name__ == "__main__":
    nums = [1, 2, 3, 4, 5]
    print(f"Average: {calculate_average(nums)}")

    greet("World")

    values = [10, 25, 5, 30, 15]
    print(f"Maximum: {find_maximum(values)}")
