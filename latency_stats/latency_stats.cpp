#include <fstream>
#include <iostream>
#include <limits>
#include <string>
#include <sstream>

int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cerr << "Invalid argument count\n";
        return 1;
    }
    std::ifstream file(argv[1]);

    if (!file.is_open()) {
        std::cerr << "Failed to open file\n";
        return 1;
    }
    int count = 0;
    int minimum = std::numeric_limits<int>::max();
    int maximum = std::numeric_limits<int>::min();
    long long runningSum = 0;

    int latency;

    std::string line;
    while (std::getline(file, line)) {
        std::istringstream parser(line);
        if (!(parser >> latency)) {
            std::cerr << "Invalid latency\n";
            return 1;
        }
        char extra;
        if (parser >> extra) {
            std::cerr << "Unexpected characters after integer\n";
            return 1;
        }
        std::cout << latency << "\n";
        ++count;
        runningSum += latency;
        if (latency < minimum) {
            minimum = latency;
        }
        if (latency > maximum) {
            maximum = latency;
        }
    }
    std::cout << "Count: " << count << "\n";
    std::cout << "Minimum: " << (count == 0 ? "N/A" : std::to_string(minimum)) << "\n";
    std::cout << "Maximum: " << (count == 0 ? "N/A" : std::to_string(maximum)) << "\n";
    std::cout << "Mean: " << (count == 0 ? "N/A" : std::to_string(static_cast<double>(runningSum) / count)) << "\n";


    return 0;

}