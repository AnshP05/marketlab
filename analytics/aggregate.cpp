#include "aggregate.hpp"
#include <unordered_map>
#include <stdexcept>
#include <limits>

std::vector<Holding> aggregate (const std::vector<Holding>& holdings) {
    std::unordered_map<std::string, std::uint64_t> map;
    std::vector<Holding> aggregate_holdings;
    constexpr ShareMicros maximum = std::numeric_limits<ShareMicros>::max();
    for (const auto& [shares, ticker] : holdings) {
        auto it = map.find(ticker);
        if (it == map.end()) {
            map[ticker] = shares;
        } else if (maximum - shares < map[ticker]) {
            throw std::overflow_error("Aggregated share quantity exceeds the supported range");
        } else {
            map[ticker] += shares;
        }
    }

    aggregate_holdings.reserve(map.size());
    for (const auto& [ticker, shares] : map) {
        aggregate_holdings.push_back(Holding{shares, ticker});
    }

    return aggregate_holdings;
}
