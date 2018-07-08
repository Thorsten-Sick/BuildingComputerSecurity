

.phony: secure_gcc, insecure_gcc, verify

insecure_gcc: program.c
	gcc -g program.c -o program

verify: program
	objdump --syms program
	hardening-check/hardening-check program
