# Sara Can Make Code Changes!

Sara can now directly edit your code files, just like Claude Code! When she suggests changes, you'll see an interactive diff and can choose what to do.

## How It Works

1. **Sara analyzes your code** and identifies issues or improvements
2. **She proposes changes** using a special format
3. **You see an interactive diff** showing exactly what will change
4. **You choose**: Confirm, Deny, or Request Adjustments

## Interactive Options

When Sara proposes a change, you'll see three options:

```
→ ✓ Apply this change          (Press ↑/↓ to navigate, Enter to select)
  ✗ Skip this change
  ✎ Deny and request adjustments
```

### Navigation

- **Arrow Keys (↑/↓)**: Move between options
- **Enter**: Select the highlighted option
- **Quick Keys**:
  - `c` - Confirm
  - `d` - Deny
  - `a` - Request adjustments

### Options Explained

**✓ Apply this change**
- Sara's suggested change will be applied to your file
- The file is modified immediately
- You'll see: `✓ Successfully applied change to filename.py`

**✗ Skip this change**
- The change is ignored
- Your file remains unchanged
- Sara moves on to the next change (if any)

**✎ Deny and request adjustments**
- You'll be prompted to explain what needs to change
- Sara will revise her suggestion based on your feedback
- You'll see a new diff with the adjusted change

## Example Session

```bash
$ sara "fix the bug in test_code.py"

Gathering context...

Sara: I found an issue in the `calculate_average` function. It will crash if
given an empty list. Let me fix it:

OLD:
```python
def calculate_average(numbers):
    """Calculate the average of a list of numbers"""
    total = 0
    for num in numbers:
        total = total + num
    return total / len(numbers)
```
NEW:
```python
def calculate_average(numbers):
    """Calculate the average of a list of numbers"""
    if not numbers:
        return 0
    total = 0
    for num in numbers:
        total = total + num
    return total / len(numbers)
```

This adds a check for empty lists to prevent division by zero.

┌─ Proposed Change to: test_code.py ─────────────────┐
│                                                     │
│  def calculate_average(numbers):                   │
│      """Calculate the average of a list of numbers"""│
│ +    if not numbers:                               │
│ +        return 0                                  │
│      total = 0                                     │
│      for num in numbers:                           │
│          total = total + num                       │
│      return total / len(numbers)                   │
└─────────────────────────────────────────────────────┘

Use ↑/↓ arrows to navigate, Enter to select, or press c/d/a

→ ✓ Apply this change
  ✗ Skip this change
  ✎ Deny and request adjustments

✓ Change accepted
✓ Successfully applied change to test_code.py
```

## How Sara Formats Changes

Sara uses this format when proposing changes:

```
OLD:
```
code to replace
```
NEW:
```
new code
```
```

The OLD code must match EXACTLY what's in your file (including spacing and indentation).

## Requesting Adjustments

If you select "Deny and request adjustments", you'll be prompted:

```
What adjustments would you like Sara to make?
Your feedback: ▊
```

Example feedback:
- "Use a try-except instead of an if statement"
- "Add a log message when the list is empty"
- "Return None instead of 0"

Sara will then revise her changes based on your feedback and show you a new diff.

## Use Cases

### Fix Bugs
```bash
sara "there's a bug in the error handling"
# Sara will identify and fix the bug with confirmation
```

### Refactor Code
```bash
sara "refactor this function to be more readable"
# Sara will show you the refactored code before applying
```

### Add Features
```bash
sara "add input validation to this function"
# Sara will add the validation and let you approve
```

### Optimize Performance
```bash
sara "optimize this loop"
# Sara will show the optimized version for review
```

## Safety Features

Sara's code changes are safe:

✅ **Preview Before Apply** - You always see what will change
✅ **Exact Matching** - Changes only apply if the OLD code matches exactly
✅ **Validation** - Sara validates the change can be applied before showing you
✅ **Undo-able** - Your code is in git, so you can revert if needed
✅ **One Change at a Time** - Multiple changes are shown separately

## Tips for Best Results

1. **Be specific about what you want changed**
   ```bash
   # Good
   sara "add error handling to the database connection"

   # Less specific
   sara "make this better"
   ```

2. **Have the file open in VS Code**
   - Sara will automatically know which file to modify
   - Make sure the VS Code extension is installed

3. **Provide context if needed**
   ```bash
   sara "fix the validation logic" --file utils/validator.py
   ```

4. **Use interactive mode for multiple changes**
   ```bash
   sara -i
   > Review this file for bugs
   > Fix each bug you find
   ```

## Troubleshooting

**"The code to replace was not found in the file"**
- The file may have been modified since Sara read it
- Try asking Sara to read the file again

**"The code to replace appears multiple times"**
- Sara needs more context to uniquely identify the change
- Ask her to "include more surrounding code"

**Change didn't apply**
- Check file permissions
- Make sure the file isn't open in another program
- Verify you're in the correct directory

## Comparison with Claude Code

Sara now works just like Claude Code:

| Feature | Sara | Claude Code |
|---------|------|-------------|
| Shows diffs before applying | ✅ | ✅ |
| Interactive confirmation | ✅ | ✅ |
| Request adjustments | ✅ | ✅ |
| VS Code integration | ✅ | ✅ |
| Keyboard navigation | ✅ | ✅ |

Sara is truly your little sister now! 🤖✨

## Next Steps

Try Sara's code editing powers:

```bash
# Open a file in VS Code
# Then run:
sara "review this code and fix any issues"

# Or in interactive mode:
sara -i
```

Happy coding with Sara! 🚀
