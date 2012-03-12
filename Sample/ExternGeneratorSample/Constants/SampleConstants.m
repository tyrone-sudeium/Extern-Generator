//
//  SampleConstants.m
//  ExternGeneratorSample
//
//  Created by Tyrone Trevorrow on 12/03/12.
//  Copyright (c) 2012 Sudeium. All rights reserved.
//

#import "SampleConstants.h"

// Here are the top level decls

// This one should be included
NSString * const kOutsideImplementationBlock = @"Outside Implementation Block";
// This one should not be
// TODO: Fix static
// static NSString * const kIsStatic = @"Static String";
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
    NSString * const kThisShouldntBeParsed = @"This shouldn't be parsed";
    NSLog(@"%@", kThisShouldntBeParsed);
    return self;
}

@end
