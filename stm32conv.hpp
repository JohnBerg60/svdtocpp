#include <stdint.h>
#include <stddef.h>

typedef volatile uint32_t regrw;

template<size_t addr>
struct Reg
{
    static constexpr void write(size_t val)
    {
        *(reinterpret_cast<volatile size_t*>(addr)) = val;
    }

    static constexpr size_t read()
    {
        return *(reinterpret_cast<volatile size_t*>(addr));
    }
};

template<size_t addr, unsigned pos, unsigned size>
class Property
{
private:
    static constexpr Reg reg = Reg<addr>();
    static constexpr size_t mask =  ((1 << size) - 1);
    static constexpr size_t posmask =  mask << pos;

public:
    Property() = default;
    
    Property& operator=(int x) { reg.write((reg.read() & ~posmask) | (x & mask) << pos); return *this; }
    operator int() const { return (reg.read() >> pos) & mask; }
};

template<typename Enum>
constexpr size_t operator |(Enum leftval, Enum rightval ) 
{
    return (1 << static_cast<size_t>(leftval)) | (1 << static_cast<size_t>(rightval));
}

template<typename Enum>
class reg32bit
{
public:
    constexpr reg32bit & operator =  (Enum e) { raw = (1 << static_cast<size_t>(e)); return *this;}
    constexpr reg32bit & operator =  (uint32_t i) { raw = i; return *this;}

    constexpr reg32bit & operator |= (Enum e) { raw |= 1 << static_cast<size_t>(e); return *this; }
    constexpr reg32bit & operator &= (Enum e) { raw &= 1 << static_cast<size_t>(e); return *this; }  
    constexpr reg32bit & operator ^= (Enum e) { raw ^= 1 << static_cast<size_t>(e); return *this; }

private:
    regrw raw;
};

