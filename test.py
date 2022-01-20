class Solution:
    def longestPalindrome(self, s: str) -> str:
        longest = ""
        core_start = 0
        while core_start in range(len(s)):
            # identifying the "core"
            core_end = core_start 
            while core_end < len(s) - 1:
                if s[core_end + 1] == s[core_end]:
                    core_end += 1
                else: 
                    break
            # expanding the palindrome left and right
            expand = 0
            while (core_start - expand) > 0 and (core_end + expand) < len(s) - 1: 
                if s[core_start - expand - 1] == s[core_end + expand + 1]:
                    expand += 1
                else:
                    break
            # comparing to the longest found so far
            if (core_end + expand + 1) - (core_start - expand) > len(longest): 
                longest = s[(core_start - expand):(core_end + expand + 1)]
            # skip through the rest of the "core"
            core_start = core_end + 1
        return longest

sol = Solution()
print(sol.longestPalindrome("ddffe"))
pass