https://www.reddit.com/r/Python/comments/1aeik5l/use_python_to_calculate_number_of_upvotes_and/

Use Python to calculate number of upvotes and downvotes

Downvoting with no explaination really hurts, but does happen despite 
r/Python rule \#3 "Please don't downvote without commenting your reasoning for doing so".

After a bit of suffering of injustice one may inquire how many of the downvotes where there?
On some level at StackOverflow you see the stats on upvote and downvote to your question, but
reddit shows you just the net score provides the _upvote rate_. Albegraically, this is enough to
calculate the raw upvote and downvote numbers.

The formulas come from pen and paper by solution for this system of two equations:

```
upvotes - downvotes = net_score
upvote_rate = upvotes / (upvotes + downvotes )
```

The code:

```
def votes(upvote_rate: float, net_score: int)-> tuple[int, int]:
    downvotes = net_score * (1-upvote_rate) / (2 * upvote_rate - 1)
    upvotes = net_score + downvotes
    return round(upvotes), round(downvotes)

print(votes(.8, 3)) # (4, 1)
print(votes(.56, 5)) # (23, 18)
```

So, by knowing my upvote rate of 56% and net score of 5 
I now know there were 23 upvotes and 18 downvotes (sadly, with no comment).
