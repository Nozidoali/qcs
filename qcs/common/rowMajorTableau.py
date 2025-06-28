# simple_tableau.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple


# ── 1.  Pauli ↔ bit-vector glue  ────────────────────────────────────────────
#
# For a single qubit, map
#   i → (z=0, x=0)
#   x → (0,1)   z → (1,0)   y → (1,1)
# A multi-qubit word is the column-wise concat of those pairs.

_PAULI_TO_BZX = {
    "i": ("0", "0"),
    "x": ("0", "1"),
    "z": ("1", "0"),
    "y": ("1", "1"),   # Y = i·XZ
}
_BZX_TO_PAULI = {v: k for k, v in _PAULI_TO_BZX.items()}


def pauli_str_to_bits(p: str) -> Tuple[str, str]:
    """xyzI → (z_bits, x_bits)  as two equal-length 01 strings."""
    p = p.lower()
    z = "".join(_PAULI_TO_BZX[ch][0] for ch in p)
    x = "".join(_PAULI_TO_BZX[ch][1] for ch in p)
    return z, x


def bits_to_pauli_str(z_bits: str, x_bits: str) -> str:
    """Inverse of pauli_str_to_bits()."""
    if len(z_bits) != len(x_bits):
        raise ValueError("Z/X strings must have same length")
    return "".join(
        _BZX_TO_PAULI[(z_bits[i], x_bits[i])] for i in range(len(z_bits))
    )


# ── 2.  Minimal PauliProduct façade  ───────────────────────────────────────
@dataclass
class PauliProduct:
    """Pure-Python shadow of core::PauliProduct."""
    z: str           # 01 string, length = n_qubits
    x: str           # 01 string, same length
    sign: bool = False   # False → +1   True → –1

    # Convenience constructors / converters
    @classmethod
    def from_pauli(cls, word: str, sign: bool = False) -> "PauliProduct":
        z, x = pauli_str_to_bits(word)
        return cls(z, x, sign)

    def to_pauli(self) -> str:
        return bits_to_pauli_str(self.z, self.x)

    def __str__(self) -> str:
        prefix = "-" if self.sign else "+"
        return f"{prefix}{self.to_pauli()}"


# ── 3.  Simple row-major tableau wrapper  ───────────────────────────────────
@dataclass
class RowMajorTableau:
    r"""
    Row-major stabiliser tableau (Aaronson-Gottesman encoding).

    This structure represents *any* \(n\)-qubit Clifford unitary or stabiliser
    state using two \(n \times 2n\) binary matrices **Z** and **X** plus a
    length-\(2n\) binary sign vector **s**:

    ┌──── column j = 0 … n-1 ───────┬──── column j = n … 2n-1 ──────┐
    │   D₀ … D_{n-1}  (destabilisers) │   S₀ … S_{n-1} (stabilisers) │
    └───────────────────────────────┴───────────────────────────────┘

    *   ``z_rows[i][j] == '1'``  ⇔  generator *j* has a **Z** on qubit *i*
    *   ``x_rows[i][j] == '1'``  ⇔  generator *j* has an **X** on qubit *i*
    *   ``signs[j]     == '1'``  ⇔  generator *j* carries a global **-1** phase  
        (needed for Y-type columns and S/H conjugation).

    Properties
    ----------
    ``n_qubits``  
        number of qubits \(n\) (half the column width)

    ``n_rows``  
        equals ``n_qubits``; one row per physical qubit

    Why 2 n Columns?
        The \(n\) commuting stabilisers \(S_i\) alone fix the quantum state,
        but adding the \(n\) complementary *destabilisers* \(D_i\) gives a full
        symplectic basis of the \(2n\)-dimensional Pauli vector space.  
        This makes every Clifford gate update a few bit-wise XORs and lets the
        simulator perform measurements and partial traces in \(O(n^2)\) time.

    Example (ground state |00⟩, n = 2)
    -----------------------------------
    >>> tab = RowMajorTableau(
    ...     z_rows=["0010",  # qubit 0   Z bits
    ...              "0001"],# qubit 1
    ...     x_rows=["1000",  # qubit 0   X bits
    ...              "0100"],
    ...     signs="0000"
    ... )
    >>> print(tab)
    RowMajorTableau  (n=2)
     0 | Z 0010 | X 1000
     1 | Z 0001 | X 0100
    signs : 0000

    Columns 0-1 are X₀, X₁ (destabilisers); columns 2-3 are Z₀, Z₁
    (stabilisers).  All generators have positive phase.

    Gate Updates
    ------------
    * **H(q)**: swap Z and X bits in column block *q*, toggle sign where both
      bits were 1.  
    * **S(q)**: Z_bits ^= X_bits in column block *q*, toggle sign on (X∧Z).  
    * **CX(c,t)**: X_t ^= X_c, Z_c ^= Z_t, update sign on specific overlap.

    All updates are linear over 𝔽₂, so the tableau stays a compact, fast
    bit-packed representation throughout Clifford synthesis and simulation.
    """
    z_rows: List[str]
    x_rows: List[str]
    signs: str = ""

    def __post_init__(self):
        if len(self.z_rows) != len(self.x_rows):
            raise ValueError("z_rows and x_rows must have the same count")
        row_len = len(self.z_rows[0])
        if any(len(r) != row_len for r in self.z_rows + self.x_rows):
            raise ValueError("All rows must have the same length")
        if self.signs == "":
            self.signs = "0" * row_len
        if len(self.signs) != row_len:
            raise ValueError("signs length must equal row length")

    # ── Derived properties ──
    @property
    def n_qubits(self) -> int:
        return len(self.z_rows[0]) // 2

    @property
    def n_rows(self) -> int:
        return len(self.z_rows)

    # ── Row / column helpers ──
    def z_row(self, i: int) -> str: return self.z_rows[i]
    def x_row(self, i: int) -> str: return self.x_rows[i]
    def sign_bit(self, col: int) -> int: return int(self.signs[col])

    # ── Pauli extraction / insertion ──
    def extract_pauli_product(self, col: int) -> PauliProduct:
        z = "".join(r[col] for r in self.z_rows)
        x = "".join(r[col] for r in self.x_rows)
        s = bool(int(self.signs[col]))
        return PauliProduct(z, x, s)

    def insert_pauli_product(self, p: PauliProduct, col: int) -> None:
        if len(p.z) != self.n_rows:
            raise ValueError("Pauli length mismatch with tableau rows")
        for i in range(self.n_rows):
            self.z_rows[i] = self.z_rows[i][:col] + p.z[i] + self.z_rows[i][col + 1 :]
            self.x_rows[i] = self.x_rows[i][:col] + p.x[i] + self.x_rows[i][col + 1 :]
        self.signs = self.signs[:col] + ("1" if p.sign else "0") + self.signs[col + 1 :]

    # ── Pretty print ──
    def __str__(self) -> str:
        head = f"RowMajorTableau  (n={self.n_qubits})"
        body = "\n".join(
            f"{i:2d} | Z {self.z_rows[i]} | X {self.x_rows[i]}"
            for i in range(self.n_rows)
        )
        signs = f"signs : {self.signs}"
        return f"{head}\n{body}\n{signs}"
