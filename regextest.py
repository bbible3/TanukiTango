from namedetection import *

namer = TanukiNamer([], [])
print("Regex result:", namer.regex_test("（麻美(まみ)）",  TanukiNamer.RegexType.SUB_NAME))
