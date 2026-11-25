#include <iostream>
#include "aggregate.hpp"
#include <limits>

int main() {
    //constexpr ShareMicros maximum = std::numeric_limits<ShareMicros>::max();
    std::vector<Holding> holdings = {Holding{2351456, "SYNTHA"}, Holding{1, "SYNTHB"}, Holding{2, "SYNTHA"}};

    std::vector<Holding> aggregate_holdings = aggregate(holdings);
    for (const auto& [shares, ticker] : aggregate_holdings) {
        std::cout << "Ticker: " << ticker << " Shares: " << shares << "\n";
    }
    return 0;
}
