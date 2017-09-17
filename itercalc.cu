#include <Python.h>

__global__
void calc(double x_start, double y_start, double step_x, double step_y, int iters, int *arr)
{
	int x = threadIdx.x;
	int y = blockIdx.x;

	double c_x = x_start + x * step_x;
	double c_y = y_start - y * step_y;
	double res_x = c_x;
	double res_y = c_y;
	double nextnum_x;
	double nextnum_y;

	int color = 0;

	for (int i = 0; i < iters; i++)
	{
		nextnum_x = res_x * res_x - res_y * res_y + c_x;
		nextnum_y = res_x * res_y * 2 + c_y;

		if (res_x == nextnum_x && res_y == nextnum_y) // Iteration has converged
			break;
		else if (res_x * res_x + res_y * res_y > 4) // Iteration escapes
		{
			int intensity = i * 255.0 / iters;
			color = intensity * 256; // Cool green color
			break;
		}
		else
		{
			res_x = nextnum_x;
			res_y = nextnum_y;
		}
	}

	arr[blockDim.x * y + x] = color;
}

static PyObject *cudaiter(PyObject *self, PyObject *args)
{
	int threads = 256;
	
	/*
	 * Screen is first partitioned in sectors of width (threads).
	 * Each sector is calculated separately and finally combined
	 * and inserted to the shared array.
	 */
	
	double x_start, x_end, y_start, y_end;
	int iters, length_x, length_y;
	PyObject *ret;

	if (!PyArg_ParseTuple(args, "ddddiiiO", &x_start, &x_end,
			&y_start, &y_end, &iters, &length_x, &length_y, &ret))
		return NULL;

	double step_x = (x_end - x_start) / length_x;
	double step_y = (y_start - y_end) / length_y;

	int strides = length_x / threads; // Calculate required amount of sectors and if there's a smaller sector at the end.
	int incomplete_stride = length_x % threads;
	
	int *colors[strides + (incomplete_stride != 0 ? 1 : 0)];
	for (int i = 0; i < strides; i++)
	{
		cudaMallocManaged(&colors[i], threads * length_y * sizeof(int));
		calc<<<length_y, threads>>>(x_start + i * threads * step_x, y_start, step_x, step_y, iters, colors[i]);
	}
	if (incomplete_stride != 0)
	{
		cudaMallocManaged(&colors[strides], incomplete_stride * length_y * sizeof(int));
		calc<<<length_y, incomplete_stride>>>(x_start + strides * threads * step_x, y_start, step_x, step_y, iters, colors[strides]);
		strides += 1; // update value to make sure combination works correctly
	}
	cudaDeviceSynchronize();
	
	int *arrs[strides]; // Create an iterator for each sector that helps with combination
	for (int i = 0; i < strides; i++)
		arrs[i] = &colors[i][0];
	
	for (int row = 0; row < length_y; row++)
	{
		for (int col = 0; col < length_x; col++)
		{
			// Sectors are combined and updated to shared Python array
			PyObject* key = PyLong_FromLong(row * length_x + col);
			PyObject* item = PyLong_FromLong(*arrs[col / threads]);
			
			PyObject_SetItem(ret, key, item);
			Py_DECREF(item);
			Py_DECREF(key);
			
			arrs[col / threads] += 1;
		}
	}
	
	for (int i = 0; i < strides; i++)
		cudaFree(colors[i]);	
	
	Py_RETURN_NONE;
}


static PyObject* iterate(PyObject* self, PyObject* args)
{
	double x_start, y_start, x_end, y_end;
	int offset, iters, count, length_x, length_y;
	PyObject* arr;

	if (!PyArg_ParseTuple(args, "iiddddiiiO", &offset, &count, &x_start, &x_end, &y_start, &y_end, &iters, &length_x, &length_y, &arr))
		return NULL;

	double x_dist = x_end - x_start;
	double y_dist = y_start - y_end;

	for (int y = offset; y < offset + count; y++)
	{
		for (int x = 0; x < length_x; x++)
		{
			long double c_x = x_start + x * x_dist / length_x;
			long double c_y = y_start - y * y_dist / length_y;
			long double res_x = c_x;
			long double res_y = c_y;
			long double nextnum_x;
			long double nextnum_y;

			int color = 0;

			for (int i = 0; i < iters; i++)
			{
				nextnum_x = res_x * res_x - res_y * res_y + c_x;
				nextnum_y = res_x * res_y * 2 + c_y;

				if (res_x == nextnum_x && res_y == nextnum_y)
					break;
				else if (res_x * res_x + res_y * res_y > 4)
				{
					int intensity = i * 255 / iters;
					color = intensity; // Cool blue color
					break;
				}
				else
				{
					res_x = nextnum_x;
					res_y = nextnum_y;
				}
			}

			PyObject* key = PyLong_FromLong(x + y*length_x);
			PyObject* item = PyLong_FromLong(color);
			PyObject_SetItem(arr, key, item);
			Py_DECREF(item);
			Py_DECREF(key);
		}
	}
	Py_RETURN_NONE;
}

static PyMethodDef CalcMethods[] = {
	{"cpuiter", iterate, METH_VARARGS,
	 "Calculate iterations"},
	{"cudaiter", cudaiter, METH_VARARGS,
	 "Calculate iterations"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

static struct PyModuleDef itercalc = {
   PyModuleDef_HEAD_INIT,
   "Mandelbrot set calculator",   /* name of module */
   NULL, /* module documentation, may be NULL */
   -1,       /* size of per-interpreter state of the module,
                or -1 if the module keeps state in global variables. */
   CalcMethods
};

PyMODINIT_FUNC
PyInit_itercalc(void)
{
    return PyModule_Create(&itercalc);
}
