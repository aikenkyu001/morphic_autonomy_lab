from dataclasses import dataclass
from typing import Any, List, Optional

@dataclass(frozen=True)
class MorphicExpr:
    pass

@dataclass(frozen=True)
class Literal(MorphicExpr):
    value: Any

@dataclass(frozen=True)
class Var(MorphicExpr):
    name: str

@dataclass(frozen=True)
class Lambda(MorphicExpr):
    param: str
    body: MorphicExpr

@dataclass(frozen=True)
class App(MorphicExpr):
    func: MorphicExpr
    arg: MorphicExpr

@dataclass(frozen=True)
class Let(MorphicExpr):
    name: str
    value: MorphicExpr
    body: MorphicExpr

@dataclass(frozen=True)
class If(MorphicExpr):
    cond: MorphicExpr
    then_br: MorphicExpr
    else_br: MorphicExpr

@dataclass(frozen=True)
class Fix(MorphicExpr):
    name: str
    body: MorphicExpr

@dataclass(frozen=True)
class MorphicStep(MorphicExpr):
    prev: MorphicExpr
    delta: MorphicExpr

# Data Structures needed for Task Grounding
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
    def __eq__(self, other):
        if not other: return False
        return self.val == other.val and self.next == other.next

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
        self.children = [] # N-ary support
    
    def __eq__(self, other):
        if not other: return False
        # Structural equality
        return (self.val == other.val and 
                self.left == other.left and 
                self.right == other.right and 
                self.children == other.children)
