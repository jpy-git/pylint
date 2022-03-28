"""Test case for TypeVar name not matching assigned variable name."""
from typing import TypeVar

X = TypeVar("T")  # [typevar-name-mismatch]
X_co = TypeVar("T", covariant=True)  # [typevar-name-mismatch]
X_contra = TypeVar("T", contravariant=True)  # [typevar-name-mismatch]
X_co, X_contra = (  # [typevar-name-mismatch,typevar-name-mismatch]
    TypeVar("T", covariant=True),
    TypeVar("T", contravariant=True),
)
