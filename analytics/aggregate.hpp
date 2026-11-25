#pragma once


#include <cstdint>
#include <string>
#include <vector>


using ShareMicros = std::uint64_t;

struct Holding {
    ShareMicros shares;
    std::string ticker;
};

std::vector<Holding> aggregate (const std::vector<Holding>& holdings);
