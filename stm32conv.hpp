#include <cstdint>
#include <cstddef>

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
    volatile uint32_t raw;
};
