

.phony: secure_gcc, insecure_gcc, verify

insecure_gcc: program.c
	gcc program.c -o program

verify: program
		hardening-check/hardening-check program
