def gf2_mul(a, b):
    result = 0
    while b:
        if b & 1:
            result ^= a
        a <<= 1
        b >>= 1
    return result


def gf2_mod(a, mod):
    deg_mod = mod.bit_length() - 1
    while a.bit_length() - 1 >= deg_mod:
        shift = (a.bit_length() - 1) - deg_mod
        a ^= mod << shift
    return a


def gf2_gcd(a, b):
    while b:
        a, b = b, gf2_mod(a, b)
    return a


def poly_to_str(poly: int) -> str:
    degree = poly.bit_length() - 1
    terms = [
        ("x^" + str(i) if i > 1 else "x" if i == 1 else "1")
        for i in range(degree, -1, -1)
        if poly & (1 << i)
    ]
    return " + ".join(terms) if terms else "0"


def is_irreducible(f):
    """
    f is irreducible if and only if gcd(2^(2^i) - 2, f) == 1
        for i = 1, 2, ..., floor(n/2),
    """
    n = f.bit_length() - 1
    power = 2
    for _ in range(1, n // 2 + 1):
        power = gf2_mod(gf2_mul(power, power), f)
        g = gf2_gcd(power ^ 2, f)
        if g != 1:
            return False
    return True


def find_irreducible_poly(n):
    for k in range(1, 1 << n, 2):  # only odd numbers ensure constant term 1
        f = (1 << n) | k
        if is_irreducible(f):
            return f
    return None


def gf2_mult_mod(a, b, f):
    product = gf2_mul(a, b)
    reduced = gf2_mod(product, f)
    return reduced


def print_truth_table(n, f):
    num_elements = 2**n
    print("Truth Table for c(x) = a(x) * b(x) mod f(x)")
    print("-" * 60)
    print(
        f"{'a (binary)':>12} | {'b (binary)':>12} | {'c (binary)':>12} | c(x) Expression"
    )
    print("-" * 60)

    for a in range(num_elements):
        for b in range(num_elements):
            c = gf2_mult_mod(a, b, f)
            # Format the binary strings padded with zeros to length n.
            a_bin = format(a, f"0{n}b")
            b_bin = format(b, f"0{n}b")
            c_bin = format(c, f"0{n}b")
            # Get the Boolean expression for c(x)
            c_expr = poly_to_str(c)
            print(f"{a_bin:>12} | {b_bin:>12} | {c_bin:>12} | {c_expr}")


def generate_truth_table(n, f) -> list[str]:
    num_elements = 2**n
    total_entries = num_elements * num_elements  # 2^(2*n)

    # Initialize a list of lists (one per bit) to collect bit values.
    bit_columns = [[] for _ in range(n)]

    # Loop over all a and b values in order.
    for a in range(num_elements):
        for b in range(num_elements):
            c = gf2_mult_mod(a, b, f)
            # Represent c as a binary string padded with zeros to length n.
            # The string is ordered from MSB to LSB.
            c_bin = format(c, f"0{n}b")
            # Append each bit (character) to its corresponding column list.
            for idx, bit in enumerate(c_bin):
                bit_columns[idx].append(bit)

    # Convert lists of bits to 01 strings.
    bit_tables = ["".join(bits) for bits in bit_columns]
    return bit_tables


def synthesize_gf_mult(n: int, verbose: bool = False) -> list[str]:
    if verbose:
        print("-" * 80 + f"\nsynthesize_gf_mult for {n} qubits")
    poly = find_irreducible_poly(n)
    if poly is not None:
        print("An irreducible polynomial in GF(2) of degree", n, "is:")
        print(poly_to_str(poly))
        if verbose:
            print("Truth table:")
            print_truth_table(n, poly)
        return generate_truth_table(n, poly)
    else:
        print("No irreducible polynomial found for degree", n)
        return None
    
if __name__ == "__main__":
    n = 2  # Degree of the polynomial
    verbose = True  # Set to True to print the truth table
    bit_tables = synthesize_gf_mult(n, verbose)
    
    if bit_tables:
        print("\nGenerated bit tables:")
        for i, bits in enumerate(bit_tables):
            print(f"Bit {i}: {bits}")
    else:
        print("Failed to generate bit tables.")