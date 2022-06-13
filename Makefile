
# Those files get extra testing and should have a minimum quality
quality_files = manuscript/appendix/changelog.txt manuscript/programming/code_analysis_tools_requirements.txt manuscript/testing/fuzzing.txt

# Those files are done and testing is enforced
# I do not expect any major changes anymore
done_files =

.PHONY: vale, vale-enforce

# Vale spell check and text linter for all chapters I am currently working on
vale:
	vale --config .vale.ini `find manuscript -name "*.txt"`

# Enforce vale on the CI/CD system for "done" chapters
vale-enforce: $(done_files)
