import re


class RangeValueUtil:
    # get groups of value, -value, +value or +-value: example: 0.2+0.2-3.4 = 0.2, +0.2, -3.4
    REGEX_RANGE_PARTS = r'([+-]?([+-]{0,2}[0-9]+\.{0,1}[0-9]*)|\+|-)'  # get groups of value, -value, +value or +-value: example: 0.2+0.2-3.4 = 0.2, +0.2, -3.4

    """
    get a min and max value from a string that contains a range of values like 0.5+-0.1 or 0.5-0.1+
    String Format: [base_value][+-][range_value][+-][range_value]...
    Examples: 
        range from 0.5 to 0.6: 0.5+0.1
        range from 0.4 to 0.6: 0.5+-0.1 or 0.5-0.1+0.1
        range from 0.5 to infinity: 0.5+
    """

    @staticmethod
    def parse_range_values(value_range_string):
        range_findings = re.findall(RangeValueUtil.REGEX_RANGE_PARTS, value_range_string)
        if len(range_findings) == 0:
            print(f"No range findings found for {value_range_string}")
            return None, None

        # only take the first group of each finding
        range_findings = [fin[0] for fin in range_findings]

        value = float(range_findings[0])
        min_val = max_val = value
        for range_val in range_findings[1:]:
            if range_val.startswith("+-"):
                if len(range_val) == 2:
                    max_val = None
                    min_val = None
                else:
                    range_val = float(range_val[2:])
                    max_val += range_val
                    min_val -= range_val
            elif range_val.startswith("+"):
                if len(range_val) == 1:
                    max_val = None
                else:
                    max_val += float(range_val[1:])
            elif range_val.startswith("-"):
                if len(range_val) == 1:
                    min_val = None
                else:
                    min_val -= float(range_val[1:])
        return min_val, max_val
