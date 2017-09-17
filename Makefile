ARCHFLAG = compute_61
PYTHONPATH = /usr/include/python3.5

itercalc.so: itercalc.cu
	nvcc --compiler-options '-fPIC' --shared \
		 -O3 -m64 -arch=$(ARCHFLAG) \
		 -o itercalc.so itercalc.cu \
		 -I $(PYTHONPATH)