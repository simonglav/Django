class Solution:
    def maxNumberOfBalloons(self, text: str) -> int:
        counter = {x: 0 for x in 'balon'}
        for ch in text:
            if ch == 'b':
                counter['b'] += 1
            elif ch == 'a':
                counter['a'] += 1
            elif ch == 'l':
                counter['l'] += 0.5
            elif ch == 'o':
                counter['o'] += 0.5
            elif ch == 'n':
                counter['n'] += 1
        return int(min(counter.values()))


if __name__ == '__main__':
    sol = Solution()
    print(sol.maxNumberOfBalloons("nlaebolko"))
    print(sol.maxNumberOfBalloons("loonbalxballpoon"))
    print(sol.maxNumberOfBalloons("leetcode"))
