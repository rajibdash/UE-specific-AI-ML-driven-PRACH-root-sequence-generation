#include "prach_reference.hpp"

#include <exception>
#include <iostream>

int main() {
    try {
        const auto preambles = prach::generate_preambles();
        std::cout << "Generated " << preambles.size() << " preambles\n";
        std::cout << "First preamble: root=" << preambles.front().root_index
                  << ", shift=" << preambles.front().cyclic_shift << '\n';
        std::cout << "Last preamble: root=" << preambles.back().root_index
                  << ", shift=" << preambles.back().cyclic_shift << '\n';
    } catch (const std::exception& error) {
        std::cerr << "PRACH generation failed: " << error.what() << '\n';
        return 1;
    }
    return 0;
}
