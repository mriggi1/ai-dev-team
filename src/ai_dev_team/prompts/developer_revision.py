"""
Developer revision prompt module.

Defines instructions for correcting an existing implementation using
review findings and the original implementation plan.
"""

DEVELOPER_REVISION_PROMPT = """
Revise the existing implementation using the review findings.

Revision Instructions

- Follow the original implementation plan as the functional contract.
- Check each finding against the plan and the existing code before applying
  a correction. Review findings may contain incorrect claims.
- Apply fixes only for technically valid findings.
- Treat duplicate findings as a single issue.
- Do not apply suggested fixes that introduce bugs or contradict the plan.
- Preserve correctly working functionality and avoid unrelated changes.
- Validate inputs and constraints before modifying stored state, so failed
  operations do not leave partial changes.
- If no findings require a correction, leave the existing files unchanged
  and run the required checks before finishing.
- Save each corrected file using write_file with both path and content.
  Include the complete corrected Python source in content, not a patch or excerpt.
- Do not deliver corrections as an assistant text response; only successfully
  saved files are used by the application.
- Do not include Markdown code fences, explanations, or a review summary.
"""
