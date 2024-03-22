#! /usr/bin/env python3

# test tuple as dict key
thistuple = ("apple", "banana", "cherry", "apple", "cherry")

t = ("a", 1)
d = {}
d[t] = t

print(d)
