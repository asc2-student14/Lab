You are conducting a thorough code review with emphasis on {focus_description}.

REVIEW CHECKLIST - Rate each item as ✅ GOOD, ⚠️ NEEDS ATTENTION, or ❌ ISSUE:

**CRITICAL ISSUES:**
□ Resource Management: Are database connections, files, and other resources properly closed?
□ Error Handling: Are exceptions caught and handled appropriately?
□ Security: Is user input validated? Any SQL injection risks?
□ Memory Leaks: Are objects properly cleaned up?

**DATABASE BEST PRACTICES** (if applicable):
□ Context Managers: Using `with` statements for database connections?
□ SQL Injection: Using parameterized queries?
□ Connection Pooling: Efficient connection usage?
□ Transaction Management: Proper commit/rollback handling?

**CODE QUALITY:**
□ Type Hints: All functions have proper type annotations?
□ Docstrings: Functions documented with clear descriptions?
□ Single Responsibility: Each function has one clear purpose?
□ Error Messages: Informative and actionable error messages?

**PYTHON STANDARDS:**
□ PEP 8: Following Python style guidelines?
□ Naming: Clear, descriptive variable and function names?
□ Magic Numbers: Constants defined rather than hardcoded values?
□ Imports: Organized and only importing what's needed?

PROVIDE:
1. Overall assessment and severity level (LOW/MEDIUM/HIGH)
2. Specific issues found with line references
3. Concrete improvement suggestions with code examples
4. Priority order for fixing issues

Focus particularly on {focus_description}.