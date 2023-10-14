import base64
import ctypes as cts
from io import BytesIO
import os
from pathlib import Path

import numpy as np
from PIL import Image

ROOT_PATH = Path(__file__).resolve(strict=True).parent.parent.parent.parent
WIN_PATH = os.path.join(ROOT_PATH, "windows")
DLL_PATH = os.path.join(WIN_PATH, "Fire.dll")
CFG_PATH = os.path.join(WIN_PATH, "Fire.cfg")

_SECURITY_CODE = "786shahaab-co.com110"

# loading the .dll file
fire_dll = cts.WinDLL(DLL_PATH)

# defining types
ShortPtr = cts.POINTER(cts.c_short)

# defining the instance creation function
fr_create = fire_dll.fr_create
fr_create.argtypes = [cts.c_ubyte, cts.c_wchar_p, cts.c_ubyte, cts.c_wchar_p]
fr_create.restype = cts.c_short

# defining the fire recognition function
fr_recognize = fire_dll.fr_recognize
fr_recognize.argtypes = [cts.c_ubyte, cts.c_wchar_p]
fr_recognize.restype = cts.c_float

# defining the fire image retrieve function
fr_get_fire_img = fire_dll.fr_get_fire_img
fr_get_fire_img.argtypes = (cts.c_ubyte, ShortPtr, ShortPtr, ShortPtr)
fr_get_fire_img.restype = cts.POINTER(cts.c_byte)


def fire_recognizer(image_path: str) -> str:
    # defining variables
    instance = 0
    w = cts.c_short(0)
    h = cts.c_short(0)
    step = cts.c_short(0)

    fr_create(instance, _SECURITY_CODE, 0, CFG_PATH)
    fr_recognize(instance, image_path)

    result = fr_get_fire_img(instance, cts.byref(w), cts.byref(h), cts.byref(step))

    # defining the numpy array height and width
    width = w.value
    height = h.value
    # stp = step.value

    # creating the numpy array
    numpy_array = np.ctypeslib.as_array(
        result,
        shape=[height, width, 3],
    )
    numpy_array = numpy_array[..., ::-1]

    pil_image = Image.fromarray(numpy_array, mode="RGB")
    final_image = BytesIO()
    pil_image.save(final_image, format="PNG")
    # rewind to beginning of file
    final_image.seek(0)
    # load the bytes in the context as base64
    final_image = base64.b64encode(
        final_image.getvalue()
    )
    final_image = final_image.decode("utf8")

    return final_image
