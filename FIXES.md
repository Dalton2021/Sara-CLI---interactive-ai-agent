# Sara Code Editing Fixes

I've fixed all three major issues you identified:

## Issue 1: No Proper Diff Window ✅ FIXED

**Problem:** Sara was just showing OLD/NEW text blocks instead of a proper diff view like git merge.

**Solution:**
- Created a side-by-side table diff viewer using Rich
- Shows OLD code on left, NEW code on right
- Highlights differences in red (removed) and green (added)
- Shows unchanged lines in dim gray for context
- Much clearer visual representation

**Example Output:**
```
┌─────────────── Proposed Change to: file.html ───────────────┐
│              OLD              │              NEW             │
├───────────────────────────────┼──────────────────────────────┤
│   <h1>Welcome</h1>           │   <h1>Welcome</h1>           │
│   <p>Missing tag             │   <p>Missing tag</p>         │
│   </header>                  │   </header>                  │
└──────────────────────────────┴──────────────────────────────┘
```

## Issue 2: Code Matching Failures ✅ FIXED

**Problem:** Sara couldn't find code in the file even though it hadn't been touched.

**Solution:**
- Added flexible whitespace matching as fallback
- Normalizes spacing differences between Sara's code and actual file
- Better error messages explaining exactly what went wrong
- Automatic retry with feedback when validation fails

**Improvements:**
- Tries exact match first (fastest)
- Falls back to normalized whitespace matching
- Provides helpful error messages:
  - "Found similar code but different whitespace"
  - "Code appears multiple times, need more context"
  - "Code not found, check the file"

## Issue 3: Too Verbose Changes ✅ FIXED

**Problem:** For a simple missing `</p>` tag, Sara showed the entire 140-line file.

**Solution:**
- Updated Sara's system prompt with **CRITICAL RULES**
- Emphasizes being "surgical" - only show lines that change
- Provides good/bad examples directly in the prompt
- Instructs her to show just 2-3 lines for simple fixes

**New Prompt Rules:**
1. **BE SURGICAL** - Show ONLY the lines that need to change
2. **NEVER replace entire files** - Only specific sections
3. **Keep it minimal** - 2-3 lines for simple fixes
4. **Include context** - Just 1-2 lines before/after
5. **Multiple changes** - Show separately, don't combine

**Good Example in Prompt:**
```
OLD:
```html
    <p>Authentic Italian Pizza Made Fresh Daily!
  </header>
```
NEW:
```html
    <p>Authentic Italian Pizza Made Fresh Daily!</p>
  </header>
```
```

This is 2 lines, not 140!

## Additional Improvements

### Automatic Error Recovery
- When Sara's change fails validation, she automatically gets feedback
- System tells her: "Show ONLY the specific lines that need to change"
- She gets one retry to fix it before giving up
- Prevents infinite loops

### Better User Feedback
- Shows progress: "Sara is revising her changes..."
- Counts issues: "⚠ 2 issue(s) need to be addressed"
- Provides tips: "Ask Sara to show less code"
- Clear success/failure messages

### Improved Validation
- Checks for exact matches first
- Falls back to flexible matching
- Detects if code appears multiple times
- Helpful error messages guide Sara to fix issues

## Testing

I've created `tests_ignore/test_missing_tag.html` with a real bug - a missing `</p>` tag on line 18.

### Test the Fixes:

```bash
# Open the test file in VS Code
code tests_ignore/test_missing_tag.html

# Ask Sara to find and fix the issue
sara "find and fix the error in this file"
```

**Expected Behavior:**
1. Sara identifies the missing `</p>` tag
2. Shows ONLY 2-3 lines in the diff (not the whole file)
3. Displays a proper side-by-side diff table
4. The change matches the file content exactly
5. You can confirm/deny/adjust with keyboard navigation
6. Change applies successfully ✓

### Test Interactive Mode:

```bash
sara -i
> there's a missing closing tag in test_missing_tag.html
> can you fix it?
```

Sara should:
- Find the issue
- Show minimal, surgical change
- Apply it successfully after confirmation

## What Changed in the Code

### `diff_viewer.py`
- Replaced simple line-by-line printing with Rich Table
- Side-by-side OLD/NEW columns
- Color coding for changes vs unchanged lines

### `code_editor.py`
- Added `_normalize_for_matching()` for flexible whitespace
- Improved `apply()` to try multiple matching strategies
- Enhanced `validate_change()` with better error messages
- Auto-feedback on validation failures

### `cli.py`
- Updated system prompt with surgical change examples
- Added auto-retry logic when changes fail
- Improved feedback messages to user
- Guidance to Sara on how to fix issues

## Summary

All three issues are now fixed:
- ✅ Proper git-style diff viewer
- ✅ Flexible code matching that actually works
- ✅ Surgical, minimal changes (not entire files)

Sara now behaves much more like Claude Code - showing clean diffs, making targeted changes, and recovering from errors automatically!

Try it out with the test file and you should see a huge improvement! 🚀
