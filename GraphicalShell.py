// track_new_delete.cpp
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
    return p;
}

void operator delete(void* p) noexcept {
    if (!p) return;
    {
        std::lock_guard<std::mutex> lk(allocs_mtx);
        allocs.erase(p);
    }
    std::free(p);
}

// C++14/17 delete with size
void operator delete(void* p, std::size_t) noexcept {
    operator delete(p);
}

struct A { int x; };

int main() {
    A* a = new A();
    (void)a;
    // намеренная утечка для демонстрации:
    new int[10];

    // В конце программы выводим несвободные аллокации
    {
        std::lock_guard<std::mutex> lk(allocs_mtx);
        std::cout << "Outstanding allocations:\n";
        for (auto &kv : allocs) {
            std::cout << "  addr=" << kv.first << " size=" << kv.second << '\n';
        }
    }
    return 0;
}
