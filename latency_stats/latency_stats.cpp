#include <fstream>
#include <iostream>

int main() {
    std::ifstream file("latencies.txt");

    if (!file.is_open()) {
        std::cerr << "Failed to open file\n";
        return 1;
    }

    int latency;
    while (file >> latency) {
        std::cout << latency << "\n";
    }


    return 0;

}