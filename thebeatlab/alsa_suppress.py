from ctypes import CFUNCTYPE, c_char_p, c_int, cdll

# Define the custom error handler type
ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

# Custom error handler function to suppress ALSA warnings
def py_error_handler(filename, line, function, err, fmt):
    pass  # Suppress ALSA errors by doing nothing

# Convert the Python error handler to a C function pointer
c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

# Load the ALSA library
asound = cdll.LoadLibrary('libasound.so')

# Set the custom error handler to suppress ALSA warnings globally
asound.snd_lib_error_set_handler(c_error_handler)
