import re

fields = ('side', 'region', 'side', 'region', 'single')
pattern_digits = '{side}_{region}_{side}_{region}_{single}'
for each in list(set(fields)):
    regex_pattern = re.compile(each)
    indexes = [match.end() for match in regex_pattern.finditer(pattern_digits)]
    repetetions = len(indexes)
    if repetetions > 1:
        i = 0
        for match in sorted(indexes, reverse=True):
            pattern_digits = "{}{}{}".format(
                pattern_digits[:match],
                str(repetetions-i),
                pattern_digits[match:]
            )
            i += 1
print(pattern_digits)
