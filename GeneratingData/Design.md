# Double Dummy Solver

## Introduction

The scripts that are prefixed by DoubleDummy generate the hands and the number of tricks won using Double Dummy Analysis for each possible trump, assuming NORTH to be the dealer. For each (NS) hand we randomly distribute the remaining cards to (EW) 5 times to get 5 different games per (NS) hand. 

## Encoding

* holding: { {.(N)., .(E), .(S)., .(W).} (Spades), {...} (Hearts), {...} (Diamonds), {...} (Clubs) }
* trump: {0: Spades, 1: Hearts, 2: Diamonds, 3: Clubs, 4: NoTrump}
* suite: {0: Spades, 1: Hearts, 2: Diamonds, 3: Clubs}
* rank: {2^(Rank) where Rank(Ace)=14}

## Output Schema

The output schema for a given game is:

> (N) ....

> (S) ....

> (E) ....

> (W) ....

> (Spades, MaxTricks)

> (Hearts, MaxTricks)

> (Diamonds, MaxTricks)

> (Clubs, MaxTricks)

> (NoTrump, MaxTricks)


For each (NS) hand we randomly distribute the remaining cards to (EW) 5 times to get 5 different games per (NS) hand. Hence the overall structure of the document looks like:

> Game 1 (9 Lines)

> Game 2 (9 Lines)

> Game 3 (9 Lines)

> Game 4 (9 Lines)

> Game 5 (9 Lines)

> Empty Line

> Game 1 (9 Lines)

> Game 2 (9 Lines)

> Game 3 (9 Lines)

> Game 4 (9 Lines)

> Game 5 (9 Lines)

> Empty Line

## Clean Up

The output of the DoubleDummy.cpp is piped to DoubleDummyOutput which is then cleaned up CleanDoubleDummy.py which makes the output more pliable to scoring. The python script output to DoubleDummyCleaned.json whose schema is:

> { idx: 

> 	{

> 		"N":[ ..(North Hand).. ], 

> 		"S":[ ..(South Hand).. ], 

> 		"MaxTricks":

>			[

>				[ (Spades, MaxTricks), (Hearts, MaxTricks), (Diamonds, MaxTricks), (Clubs, MaxTricks), (NoTrump, MaxTricks) ],

>				..(5 Such Lists)..

>			]

>	}

>  (Several Such Indices Each Denoting a Unique North South Hand)

> }


# Bridge Scorer

## Introduction

The scoring is done using the description on Wikipedia (https://en.wikipedia.org/wiki/Bridge_scoring) and converted to IMP using the index given here (https://www.bridgehands.com/I/IMP.htm).

Since the score of the hands is to be estimated given only the final contract and not the course of bids (which can only be computed in runtime), we assume:

* No vulnerability
* No extra points for doubling or redoubling

Further, in order to distinguish between NS winning and losing, we misuse IMPs by awarding negative IMPs to contracts that cause NS to have a score smaller than EW. 

The ScoreDoubleDummy.py computes the 36 dimensional IMP vector and vectorises the North and South hands as well saving the output to DoubleDummyScore.json 
