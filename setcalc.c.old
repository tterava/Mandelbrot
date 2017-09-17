#include <Python.h>

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
					color = intensity * 256;
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
	{"iterate", iterate, METH_VARARGS,
	 "Calculate iterations"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

static struct PyModuleDef setcalc = {
   PyModuleDef_HEAD_INIT,
   "Mandelbrot set calculator",   /* name of module */
   NULL, /* module documentation, may be NULL */
   -1,       /* size of per-interpreter state of the module,
                or -1 if the module keeps state in global variables. */
   CalcMethods
};

PyMODINIT_FUNC
PyInit_setcalc(void)
{
    return PyModule_Create(&setcalc);
}
