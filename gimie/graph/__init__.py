from typing import Tuple, TypeAlias, Union

from rdflib.term import Literal, URIRef

Property: TypeAlias = Tuple[URIRef, Union[URIRef, Literal]]
