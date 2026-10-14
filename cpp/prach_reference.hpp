#ifndef PRACH_REFERENCE_HPP
#define PRACH_REFERENCE_HPP

#include <complex>
#include <vector>

namespace prach {

struct Preamble {
    int preamble_id;
    int root_index;
    int cyclic_shift;
    std::vector<std::complex<double>> sequence;
};

std::vector<std::complex<double>> zadoff_chu_root_sequence(int length, int root_index);
std::vector<std::complex<double>> cyclically_shift(
    const std::vector<std::complex<double>>& sequence,
    int shift);
std::vector<Preamble> generate_preambles(
    int length = 839,
    int root_start = 1,
    int n_cs = 13,
    int count = 64);

}  // namespace prach

#endif
