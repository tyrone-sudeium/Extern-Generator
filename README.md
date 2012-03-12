# Extern Generator for Objective-C
### The Theory
Given a .m file that is filled with top-level constant declarations, the compiler (or build tools) should be able to automatically derive the "externs" that go in the corresponding header file.

Right now, you pretty much have to type every const twice.

That's where this script comes in.

### How It Works
1. Using libclang, it will generate an Abstract Syntax Tree from your .m file
2. Then it will do a tree traversal to find all the top level variable declarations, finds the ones that are constants and extracts the declaration signature.
3. It will then attempt to open the header file corresponding to the .m file, finds a specific tag (#pragma GenerateHeaderExterns Begin) and inserts these declarations between the begin and end, except as extern.

### Example
Given an implementation file:
``` objective-c
// This one should be included
NSString * const kOutsideImplementationBlock = @"Outside Implementation Block";
// This one should not be
static NSString * const kIsStatic = @"Static String";
// This one should be included
NSInteger const kConstantInteger = 50;
// This one should not
NSInteger globalInteger = 0;

@implementation SampleConstants

// Technically these are top-level decls too
// This one should be included
NSString * const kInsideImplementationBlock = @"Inside Implementation Block";

- (id) init
{
    self = [super init];
    // This one should not be
    NSString * const kThisShouldntBeParsed = @"This shouldn't be parsed";
    NSLog(@"%@", kThisShouldntBeParsed);
    return self;
}

@end
```
And a header file:
``` objective-c
#import <Foundation/Foundation.h>

#pragma GenerateHeaderExterns Begin
#pragma GenerateHeaderExterns End

@interface SampleConstants : NSObject

@end
```
Generates in the header file:
``` objective-c
#import <Foundation/Foundation.h>

#pragma GenerateHeaderExterns Begin
extern NSString* const kOutsideImplementationBlock;
extern NSInteger const kConstantInteger;
extern NSString* const kInsideImplementationBlock;
#pragma GenerateHeaderExterns End

@interface SampleConstants : NSObject

@end
```
### TODOs
1. Fix static constants being picked up as externs.  I still have to work out how clang parses "static"-ness.
2. Fix the hardcoded -framework Foundation argument being passed to libclang.
3. Find a better way to determine where libclang.dylib is on the system.  Right now it will only work if Xcode.app is installed into /Applications.
4. Fix compatibility with standard C (fixing 2 will help).
5. Fix compatibility with C++.