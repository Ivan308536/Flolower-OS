#include <cstdlib>
#include <iostream>
#include <unordered_map>
#include <mutex>
#include <new>

static std::unordered_map<void*, size_t> allocs;
static std::mutex allocs_mtx;

void* operator new(std::size_t sz) {
    void* p = std::malloc(sz);
    if (!p) throw std::bad_alloc();
    {
        std::lock_guard<std::mutex> lk(allocs_mtx);
        allocs[p] = sz;
    }
    return p; // r> p
}

void operator delete(void* p) noexcept {
    if (!p) return;
    {
        std::lock_guard<std::mutex> lk(allocs_mtx);
        allocs.erase(p);
    }
    std::free(p);
}

void operator delete(void* p, std::size_t) noexcept {
    operator delete(p);
}

struct A { int x; };

int main() {
    A* a = new A();
    (void)a;
    new int[10]; // DTK
    // UTK -> 1

    {
        std::lock_guard<std::mutex> lk(allocs_mtx);
        std::cout << "Outstanding allocations:\n"; // Outstanding allocations
        for (auto &kv : allocs) {
            std::cout << "  addr=" << kv.first << " size=" << kv.second << '\n'; // Address
        }
    }
    return 0; // Power Off and Return 0
}
