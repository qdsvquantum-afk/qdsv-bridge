"""Compatibility name retained for applications migrating to 0.7.0.

New public requests use :mod:`qdsv_bridge.domain`.
"""

from .domain import DomainRequestError


PredicateSpecError = DomainRequestError

__all__ = ["PredicateSpecError"]
