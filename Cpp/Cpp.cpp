gcc -g3 -D_DEBUG -Wall -Wextra -pedantic-errors -Wfloat-equal -Wconversion -Wshadow -Weffc++ # -pg -fstack-protector

// Use ‘const’ as much as possible.
const int *p;           // pointer to const int
int * const p;          // const pointer to int
const int * const p;    // const pointer to const int
// Don’t use:
int const *p;

// GCC optimization
if(__builtin_expect(entity->extremely_unlikely_flag,0))
    // code that is rarely run

mmap // File in memomry mapping, to optimize paging operations


////////////
// C only
///////////
int main(void); // C standard to use void to indicate no parameters
// + program should end with a newline following C standard

// Interview test
int a=41; a++; printf("%d\n", a); // 42
int a=41; a++ & printf("%d\n", a); // undefined
int a=41; a++ && printf("%d\n", a); // 42
int a=41; if (a++ < 42) printf("%d\n", a); // 42
int a=41; a = a++; printf("%d\n", a); // undefined

/***********/
// C++ only
/**********/

// "Rule of three"
#define DISALLOW_COPY_AND_ASSIGN(TypeName) TypeName(const TypeName&); void operator=(const TypeName&)

// Basic exception
throw runtime_error("invalid type");
// Catching bad_alloc
try {
    obj = new Object;
} catch(std::bad_alloc &e) {
    std::cerr << "oom " << e.what() << std::endl;
    throw;
}

// Pitfalls
Derived d;
static_cast<Base>(d).foo() // the cast create a tmp obj, so foo() won't be called on d

// Parameter passing optimization: http://www.drdobbs.com/cpp/some-optimizations-are-more-important-th/240159684
string rev(string&& s) { reverse(s.begin(), s.end()); return s; }
// -> compiler will choose this one if the argument is an rvalue, which will reverse that rvalue in place
string rev(const string& s) { string t = s; reverse(t.begin(), t.end()); return t; }
// -> compiler will choose this one if the argument might be used again later, which will safely copy the string's characters

// POGO

// Windows code analysis
cl /analyze
