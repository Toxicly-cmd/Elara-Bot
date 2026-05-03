from __future__ import annotations
from typing import Union, Optional, Any

def foo(x: Union[int, None]):
    print(x)

foo(10)
foo(None)
print("Success!")
