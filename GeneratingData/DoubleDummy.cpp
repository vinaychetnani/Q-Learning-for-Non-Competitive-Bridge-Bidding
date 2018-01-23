#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <algorithm>
#include "dll.h"

//Rank Values
#define R2	0x0004
#define R3	0x0008
#define R4	0x0010
#define R5	0x0020
#define R6	0x0040
#define R7	0x0080
#define R8	0x0100
#define R9	0x0200
#define RT	0x0400
#define RJ	0x0800
#define RQ	0x1000
#define RK	0x2000
#define RA	0x4000


//Deck Constants

#define cards_per_suite 13
#define suites 4

 
//Player Constants

#define cards_per_player 13
#define players 4


//Dealt at a Time

#define players_dealt 2
#define number_of_combinations 5

using namespace std;

struct card
{
	unsigned int value;
	unsigned int suite;
};

// Initialise and shuffle the deck.
void initialise_deck(card *deck, int seed)
{
	unsigned int R[cards_per_suite] = {R2, R3, R4, R5, R6, R7, R8, R9, RT, RJ, RQ, RK, RA};
	for(int i=0; i<suites; i++)
	{
		for(int j=0; j<cards_per_suite; j++)
		{
			deck[i*cards_per_suite + j].suite = i;
			deck[i*cards_per_suite + j].value = R[j];
		}
	}
	srand(seed+time(0));
	random_shuffle(&deck[0], &deck[cards_per_suite * suites]);
}

// Generate north and south hands.
void generate_ns(card ns[players_dealt][cards_per_player], card *deck)//North-South Hands
{
	for(int i=0; i<cards_per_player; i++)
	{
		for(int j=0; j<players_dealt; j++)
		{
			ns[j][i] = deck[i*players_dealt + j];
		}
	}
}

// Generate east and west hands.
void generate_ew(card ew[number_of_combinations][players_dealt][cards_per_player], card *deck, int seed)
{
	int offset = players_dealt * cards_per_player;
	for(int combination = 0; combination<number_of_combinations; combination++)
	{
		srand(time(0) + seed);
		random_shuffle(&deck[cards_per_suite * players_dealt], &deck[cards_per_suite * suites]);
		for(int i=0; i<cards_per_player; i++)
		{
			for(int j=0; j<players_dealt; j++)
			{
				ew[combination][j][i] = deck[i*players_dealt + j + offset];
			}
		}
	}
}

void initialise_holding(int holding[suites][players])
{
	for(int i=0; i<suites; i++)
		for(int j=0; j<players; j++)
			holding[i][j] = 0;
}

void parse_holding(int holding[suites][players], card ns[players_dealt][cards_per_player], card ew[players_dealt][cards_per_player])
{
	for(int i=0; i<players_dealt; i++)
	{
		for(int j=0; j<cards_per_player; j++)
		{
			card x = ns[i][j];
			holding[x.suite][2*i] = (holding[x.suite][2*i] | x.value);
		}
	}

	for(int i=0; i<players_dealt; i++)
	{
		for(int j=0; j<cards_per_player; j++)
		{
			card x = ew[i][j];
			holding[x.suite][2*i+1] = (holding[x.suite][2*i+1] | x.value);
		}
	}

}

void print_hand(card ns[players_dealt][cards_per_player], card ew[players_dealt][cards_per_player])
{
	for(int i=0; i<players_dealt; i++)
	{
		for(int j=0; j<cards_per_player; j++)
		{
			printf("%d %d\t", ns[i][j].suite, ns[i][j].value);
		}
		printf("\n");
	}

	for(int i=0; i<players_dealt; i++)
	{
		for(int j=0; j<cards_per_player; j++)
		{
			printf("%d %d\t", ew[i][j].suite, ew[i][j].value);
		}
		printf("\n");
	}
}

void solver(int holding[suites][players], int trump_suit)
{
	//Initialise the deal.
	deal dl;
	dl.first = 0; //North
	dl.trump = trump_suit;
	
	dl.currentTrickSuit[0] = 0;
	dl.currentTrickSuit[1] = 0;
	dl.currentTrickSuit[2] = 0;

	dl.currentTrickRank[0] = 0;
	dl.currentTrickRank[1] = 0;
	dl.currentTrickRank[2] = 0;

	for (int h = 0; h < DDS_HANDS; h++)
	{
		for (int s = 0; s < DDS_SUITS; s++)
		{
			dl.remainCards[h][s] = holding[s][h];
		}
	}

	futureTricks fut;
	int target = -1;
	int solutions = 1;
	int mode = 0;
	int threadIndex = 0;

	int res = SolveBoard(dl, target, solutions, mode, &fut, threadIndex);
	char line[80];

	if (res != RETURN_NO_FAULT)
	{
		ErrorMessage(res, line);
		printf("DDS error: %s\n", line);
	}


	int score = fut.score[0];
	printf("%d %d\n", dl.trump, score);
}

void compute_hand(int seed)
{
	SetMaxThreads(0);
	
	//Initialise the deck.
	card deck[cards_per_suite * suites];
	initialise_deck(deck, seed);

	//Deal the cards.
	card ns[players_dealt][cards_per_player];
	generate_ns(ns, deck);
	
	card ew[number_of_combinations][players_dealt][cards_per_player];
	generate_ew(ew, deck, seed);
	
	for(int combination = 0; combination<number_of_combinations; combination++)
	{
		int holding[suites][players];
		//Initialise the holding.
		initialise_holding(holding);

		//Parse cards into a holding.
		parse_holding(holding, ns, ew[combination]);

		//Print the hand.
		print_hand(ns, ew[combination]);

		//For all trump suits (S,H,D,C,NoTrump)
		for(int trump_suit=0; trump_suit<5; trump_suit++)
			solver(holding, trump_suit);
	}
}

int main(int argc, char **argv)
{
	int offset, count;
	sscanf(argv[1], "%d", &offset);
	sscanf(argv[2], "%d", &count);
	for(int i=offset; i<count+offset; i++)
	{
		compute_hand(i);
		printf("\n");
	}
	return 0;
}
