

.phony: secure_gcc, insecure_gcc, verify, clean

secure_gcc: program.c
	gcc -fstack-protector-strong -D_FORTIFY_SOURCE=2 -pie -fPIE -Wl,-z,relro,-z,now program.c -o program
	strip program

insecure_gcc: program.c
	gcc -g program.c -o program

verify: program
	objdump --syms program
	hardening-check/hardening-check program


clean:
	rm *.o program
