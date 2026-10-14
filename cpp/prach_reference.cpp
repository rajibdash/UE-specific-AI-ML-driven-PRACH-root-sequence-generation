#include "prach_reference.hpp"

#include <cmath>
#include <numeric>
#include <stdexcept>

namespace prach {
namespace {

constexpr double kPi = 3.14159265358979323846;

void validate_length(int length) {
    if (length <= 1 || length % 2 == 0) {
        throw std::invalid_argument("length must be an odd integer greater than one");
    }
}

}  // namespace

std::vector<std::complex<double>> zadoff_chu_root_sequence(int length, int root_index) {
    validate_length(length);
    if (root_index < 1 || root_index >= length) {
        throw std::invalid_argument("root_index must be between 1 and length - 1");
    }
    if (std::gcd(root_index, length) != 1) {
        throw std::invalid_argument("root_index must be relatively prime to length");
    }

    std::vector<std::complex<double>> sequence;
    sequence.reserve(length);
    for (int sample = 0; sample < length; ++sample) {
        const double phase =
            -kPi * root_index * sample * (sample + 1.0) / length;
        sequence.emplace_back(std::cos(phase), std::sin(phase));
    }
    return sequence;
}

std::vector<std::complex<double>> cyclically_shift(
    const std::vector<std::complex<double>>& sequence,
    int shift) {
    if (sequence.empty()) {
        throw std::invalid_argument("sequence must not be empty");
    }
    if (shift < 0 || shift >= static_cast<int>(sequence.size())) {
        throw std::invalid_argument("shift must be between zero and sequence length - 1");
    }

    std::vector<std::complex<double>> shifted;
    shifted.reserve(sequence.size());
    for (int sample = 0; sample < static_cast<int>(sequence.size()); ++sample) {
        shifted.push_back(sequence[(sample + shift) % sequence.size()]);
    }
    return shifted;
}

std::vector<Preamble> generate_preambles(int length, int root_start, int n_cs, int count) {
    validate_length(length);
    if (root_start < 1 || root_start >= length) {
        throw std::invalid_argument("root_start must be between 1 and length - 1");
    }
    if (n_cs < 1 || n_cs > length) {
        throw std::invalid_argument("n_cs must be between 1 and length");
    }
    if (count < 1) {
        throw std::invalid_argument("count must be positive");
    }

    const int shifts_per_root = length / n_cs;
    std::vector<int> valid_roots;
    for (int offset = 0; offset < length - 1; ++offset) {
        const int root = (root_start - 1 + offset) % (length - 1) + 1;
        if (std::gcd(root, length) == 1) {
            valid_roots.push_back(root);
        }
    }
    if (count > static_cast<int>(valid_roots.size()) * shifts_per_root) {
        throw std::invalid_argument("requested preambles exceed the available roots and shifts");
    }

    std::vector<Preamble> preambles;
    preambles.reserve(count);
    for (const int root_index : valid_roots) {
        const auto root = zadoff_chu_root_sequence(length, root_index);
        for (int shift_index = 0; shift_index < shifts_per_root; ++shift_index) {
            const int cyclic_shift = shift_index * n_cs;
            preambles.push_back({
                static_cast<int>(preambles.size()),
                root_index,
                cyclic_shift,
                cyclically_shift(root, cyclic_shift),
            });
            if (static_cast<int>(preambles.size()) == count) {
                return preambles;
            }
        }
    }
    return preambles;
}

}  // namespace prach
