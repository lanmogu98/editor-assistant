url: /Users/mogu/Library/CloudStorage/OneDrive-Personal/MY_PROJECT/editor_assistant/tests/A Mathematical Theory of Communication.pdf

title: A Mathematical Theory of Communication

authors: None

Reprinted with corrections from The Bell System Technical Journal,
Vol. 27, pp. 379–423, 623–656, July, October, 1948.

A Mathematical Theory of Communication

By C. E. SHANNON

INTRODUCTION

T

HE recent development of various methods of modulation such as PCM and PPM which exchange
bandwidth for signal-to-noise ratio has intensiﬁed the interest in a general theory of communication. A
basis for such a theory is contained in the important papers of Nyquist1 and Hartley2 on this subject. In the
present paper we will extend the theory to include a number of new factors, in particular the effect of noise
in the channel, and the savings possible due to the statistical structure of the original message and due to the
nature of the ﬁnal destination of the information.

The fundamental problem of communication is that of reproducing at one point either exactly or ap-
proximately a message selected at another point. Frequently the messages have meaning; that is they refer
to or are correlated according to some system with certain physical or conceptual entities. These semantic
aspects of communication are irrelevant to the engineering problem. The signiﬁcant aspect is that the actual
message is one selected from a set of possible messages. The system must be designed to operate for each
possible selection, not just the one which will actually be chosen since this is unknown at the time of design.
If the number of messages in the set is ﬁnite then this number or any monotonic function of this number
can be regarded as a measure of the information produced when one message is chosen from the set, all
choices being equally likely. As was pointed out by Hartley the most natural choice is the logarithmic
function. Although this deﬁnition must be generalized considerably when we consider the inﬂuence of the
statistics of the message and when we have a continuous range of messages, we will in all cases use an
essentially logarithmic measure.

The logarithmic measure is more convenient for various reasons:

1. It is practically more useful. Parameters of engineering importance such as time, bandwidth, number
of relays, etc., tend to vary linearly with the logarithm of the number of possibilities. For example,
adding one relay to a group doubles the number of possible states of the relays. It adds 1 to the base 2
logarithm of this number. Doubling the time roughly squares the number of possible messages, or
doubles the logarithm, etc.

2. It is nearer to our intuitive feeling as to the proper measure. This is closely related to (1) since we in-
tuitively measures entities by linear comparison with common standards. One feels, for example, that
two punched cards should have twice the capacity of one for information storage, and two identical
channels twice the capacity of one for transmitting information.

3. It is mathematically more suitable. Many of the limiting operations are simple in terms of the loga-

rithm but would require clumsy restatement in terms of the number of possibilities.

The choice of a logarithmic base corresponds to the choice of a unit for measuring information. If the
base 2 is used the resulting units may be called binary digits, or more brieﬂy bits, a word suggested by
J. W. Tukey. A device with two stable positions, such as a relay or a ﬂip-ﬂop circuit, can store one bit of
information. N such devices can store N bits, since the total number of possible states is 2N and log2 2N
N.
If the base 10 is used the units may be called decimal digits. Since

=

log2 M

=

log10 2

=

log10 M
3

32 log10 M

=

:

;

1Nyquist, H., “Certain Factors Affecting Telegraph Speed,” Bell System Technical Journal, April 1924, p. 324; “Certain Topics in

Telegraph Transmission Theory,” A.I.E.E. Trans., v. 47, April 1928, p. 617.

2Hartley, R. V. L., “Transmission of Information,” Bell System Technical Journal, July 1928, p. 535.

1

INFORMATION
SOURCE

TRANSMITTER

RECEIVER

DESTINATION

SIGNAL

RECEIVED
SIGNAL

MESSAGE

MESSAGE

NOISE
SOURCE

Fig. 1— Schematic diagram of a general communication system.

a decimal digit is about 3 1
3 bits. A digit wheel on a desk computing machine has ten stable positions and
therefore has a storage capacity of one decimal digit. In analytical work where integration and differentiation
are involved the base e is sometimes useful. The resulting units of information will be called natural units.
Change from the base a to base b merely requires multiplication by logb a.

By a communication system we will mean a system of the type indicated schematically in Fig. 1. It

consists of essentially ﬁve parts:

;

;

)

(

)

(

t

t

y

x

of two space coordinates and time, the light intensity at point

1. An information source which produces a message or sequence of messages to be communicated to the
receiving terminal. The message may be of various types: (a) A sequence of letters as in a telegraph
as in radio or telephony; (c) A function of
of teletype system; (b) A single function of time f
time and other variables as in black and white television — here the message may be thought of as a
function f
and time t on a
pickup tube plate; (d) Two or more functions of time, say f
— this is the case in “three-
dimensional” sound transmission or if the system is intended to service several individual channels in
multiplex; (e) Several functions of several variables — in color television the message consists of three
functions f
deﬁned in a three-dimensional continuum — we may also think
of these three functions as components of a vector ﬁeld deﬁned in the region — similarly, several
black and white television sources would produce “messages” consisting of a number of functions
of three variables; (f) Various combinations also occur, for example in television with an associated
audio channel.

, g

, h

, g

, h

x

y

x

y

y

x

y

x

t

t

t

t

t

t

(

(

)

)

(

)

)

(

)

)

(

(

(

)

;

;

;

;

;

;

;

2. A transmitter which operates on the message in some way to produce a signal suitable for trans-
mission over the channel. In telephony this operation consists merely of changing sound pressure
into a proportional electrical current. In telegraphy we have an encoding operation which produces
a sequence of dots, dashes and spaces on the channel corresponding to the message. In a multiplex
PCM system the different speech functions must be sampled, compressed, quantized and encoded,
and ﬁnally interleaved properly to construct the signal. Vocoder systems, television and frequency
modulation are other examples of complex operations applied to the message to obtain the signal.

3. The channel is merely the medium used to transmit the signal from transmitter to receiver. It may be

a pair of wires, a coaxial cable, a band of radio frequencies, a beam of light, etc.

4. The receiver ordinarily performs the inverse operation of that done by the transmitter, reconstructing

the message from the signal.

5. The destination is the person (or thing) for whom the message is intended.

We wish to consider certain general problems involving communication systems. To do this it is ﬁrst
necessary to represent the various elements involved as mathematical entities, suitably idealized from their

2

physical counterparts. We may roughly classify communication systems into three main categories: discrete,
continuous and mixed. By a discrete system we will mean one in which both the message and the signal
are a sequence of discrete symbols. A typical case is telegraphy where the message is a sequence of letters
and the signal a sequence of dots, dashes and spaces. A continuous system is one in which the message and
signal are both treated as continuous functions, e.g., radio or television. A mixed system is one in which
both discrete and continuous variables appear, e.g., PCM transmission of speech.

We ﬁrst consider the discrete case. This case has applications not only in communication theory, but
also in the theory of computing machines, the design of telephone exchanges and other ﬁelds. In addition
the discrete case forms a foundation for the continuous and mixed cases which will be treated in the second
half of the paper.

PART I: DISCRETE NOISELESS SYSTEMS

1. THE DISCRETE NOISELESS CHANNEL

Teletype and telegraphy are two simple examples of a discrete channel for transmitting information. Gen-
erally, a discrete channel will mean a system whereby a sequence of choices from a ﬁnite set of elementary
symbols S1 ; : : : ;
Sn can be transmitted from one point to another. Each of the symbols Si is assumed to have
a certain duration in time ti seconds (not necessarily the same for different Si, for example the dots and
dashes in telegraphy). It is not required that all possible sequences of the Si be capable of transmission on
the system; certain sequences only may be allowed. These will be possible signals for the channel. Thus
in telegraphy suppose the symbols are: (1) A dot, consisting of line closure for a unit of time and then line
open for a unit of time; (2) A dash, consisting of three time units of closure and one unit open; (3) A letter
space consisting of, say, three units of line open; (4) A word space of six units of line open. We might place
the restriction on allowable sequences that no spaces follow each other (for if two letter spaces are adjacent,
it is identical with a word space). The question we now consider is how one can measure the capacity of
such a channel to transmit information.

In the teletype case where all symbols are of the same duration, and any sequence of the 32 symbols
is allowed the answer is easy. Each symbol represents ﬁve bits of information. If the system transmits n
symbols per second it is natural to say that the channel has a capacity of 5n bits per second. This does not
mean that the teletype channel will always be transmitting information at this rate — this is the maximum
possible rate and whether or not the actual rate reaches this maximum depends on the source of information
which feeds the channel, as will appear later.

In the more general case with different lengths of symbols and constraints on the allowed sequences, we

make the following deﬁnition:
Deﬁnition: The capacity C of a discrete channel is given by

where N

T

(

)

is the number of allowed signals of duration T .

C

=

Lim
T !

T

(

)

logN
T

It is easily seen that in the teletype case this reduces to the previous result. It can be shown that the limit
in question will exist as a ﬁnite number in most cases of interest. Suppose all sequences of the symbols
S1 ; : : : ;
t
represents the number of sequences of duration t we have

Sn are allowed and these symbols have durations t1 ; : : : ;

tn. What is the channel capacity? If N

)

(

N

t

N

t

(

) =

(

t1) +

N

t

(

t2) +

N

t

+

(

tn):

(cid:0)

(cid:0)

(cid:1) (cid:1) (cid:1)

(cid:0)

The total number is equal to the sum of the numbers of sequences ending in S1 ;
N
is then asymptotic for large t to Xt

, respectively. According to a well-known result in ﬁnite differences, N
0 where X0 is the largest real solution of the characteristic equation:

Sn and these are
t

t2 ); : : : ;

S2 ; : : : ;

t1);

tn )

N

N

t

t

t

(

)

(cid:0)

(cid:0)

(cid:0)

(

(

(

X (cid:0)t1

X (cid:0)t2

X (cid:0)tn

1

+

+

+

=

(cid:1) (cid:1) (cid:1)

3

¥
and therefore

C

logX0 :

=

In case there are restrictions on allowed sequences we may still often obtain a difference equation of this

type and ﬁnd C from the characteristic equation. In the telegraphy case mentioned above

N

t

N

t

2

N

t

4

N

t

5

N

t

7

N

t

8

N

t

10

(

) =

(

) +

(

) +

(

) +

(

) +

(

) +

(

)

(cid:0)

(cid:0)

(cid:0)

(cid:0)

(cid:0)

(cid:0)

:

=

(cid:0)

+ (cid:22)

= (cid:22)

4

5

2

7

log

(cid:22)0 where

(cid:22)0 is the positive root of 1

as we see by counting sequences of symbols according to the last or next to the last symbol occurring.
10. Solving this we ﬁnd
Hence C is
0
539.
C
A very general type of restriction which may be placed on allowed sequences is the following: We
Sn
imagine a number of possible states a1 ;
can be transmitted (different subsets for the different states). When one of these has been transmitted the
state changes to a new state depending both on the old state and the particular symbol transmitted. The
telegraph case is a simple example of this. There are two states depending on whether or not a space was
the last symbol transmitted. If so, then only a dot or a dash can be sent next and the state always changes.
If not, any symbol can be transmitted and the state changes if a space is sent, otherwise it remains the same.
The conditions can be indicated in a linear graph as shown in Fig. 2. The junction points correspond to the

am. For each state only certain symbols from the set S1 ; : : : ;

a2 ; : : : ;

8

+ (cid:22)

+ (cid:22)

+ (cid:22)

+ (cid:22)

DASH

DOT

DOT

LETTER SPACE

DASH

WORD SPACE

Fig. 2— Graphical representation of the constraints on telegraph symbols.

states and the lines indicate the symbols possible in a state and the resulting state. In Appendix 1 it is shown
that if the conditions on allowed sequences can be described in this form C will exist and can be calculated
in accordance with the following result:

Theorem 1: Let b(

s
i j be the durationof the sth symbolwhich is allowable in state i and leads to state j.
ThenthechannelcapacityC isequalto logW whereW isthelargestrealrootofthedeterminantequation:

)

W (cid:0)b(

s
i j

)

(cid:14)i j

=

0

where

(cid:14)i j =

1 if i

=

j andiszerootherwise.

(cid:12)

(cid:12)

(cid:12)

(cid:12)

s

(cid:0)

(cid:12)

(cid:12)

For example, in the telegraph case (Fig. 2) the determinant is:

1
W (cid:0)6

W (cid:0)3

(cid:0)

W (cid:0)2

W (cid:0)4

(

+

)

W (cid:0)2

W (cid:0)4

1

0

=

:

(

+

)

(

+

)

(cid:12)

(cid:12)

(cid:0)

On expansion this leads to the equation given above for this case.

(cid:12)

(cid:12)

(cid:12)

(cid:12)

(cid:12)

(cid:12)

2. THE DISCRETE SOURCE OF INFORMATION

We have seen that under very general conditions the logarithm of the number of possible signals in a discrete
channel increases linearly with time. The capacity to transmit information can be speciﬁed by giving this
rate of increase, the number of bits per second required to specify the particular signal used.

We now consider the information source. How is an information source to be described mathematically,
and how much information in bits per second is produced in a given source? The main point at issue is the
effect of statistical knowledge about the source in reducing the required capacity of the channel, by the use

4

(cid:229)
of proper encoding of the information. In telegraphy, for example, the messages to be transmitted consist of
sequences of letters. These sequences, however, are not completely random. In general, they form sentences
and have the statistical structure of, say, English. The letter E occurs more frequently than Q, the sequence
TH more frequently than XP, etc. The existence of this structure allows one to make a saving in time (or
channel capacity) by properly encoding the message sequences into signal sequences. This is already done
to a limited extent in telegraphy by using the shortest channel symbol, a dot, for the most common English
letter E; while the infrequent letters, Q, X, Z are represented by longer sequences of dots and dashes. This
idea is carried still further in certain commercial codes where common words and phrases are represented
by four- or ﬁve-letter code groups with a considerable saving in average time. The standardized greeting
and anniversary telegrams now in use extend this to the point of encoding a sentence or two into a relatively
short sequence of numbers.

We can think of a discrete source as generating the message, symbol by symbol. It will choose succes-
sive symbols according to certain probabilities depending, in general, on preceding choices as well as the
particular symbols in question. A physical system, or a mathematical model of a system which produces
such a sequence of symbols governed by a set of probabilities, is known as a stochastic process.3 We may
consider a discrete source, therefore, to be represented by a stochastic process. Conversely, any stochastic
process which produces a discrete sequence of symbols chosen from a ﬁnite set may be considered a discrete
source. This will include such cases as:

1. Natural written languages such as English, German, Chinese.

2. Continuous information sources that have been rendered discrete by some quantizing process. For

example, the quantized speech from a PCM transmitter, or a quantized television signal.

3. Mathematical cases where we merely deﬁne abstractly a stochastic process which generates a se-

quence of symbols. The following are examples of this last type of source.

(A) Suppose we have ﬁve letters A, B, C, D, E which are chosen each with probability .2, successive
choices being independent. This would lead to a sequence of which the following is a typical
example.
B D C B C E C C C A D C B D D A A E C E E A
A B B D A E E C A C E E B A E E C B C E A D.
This was constructed with the use of a table of random numbers.4

(B) Using the same ﬁve letters let the probabilities be .4, .1, .2, .2, .1, respectively, with successive

choices independent. A typical message from this source is then:
A A A C D C B D C E A A D A D A C E D A
E A D C A B E D A D D C E C A A A A A D.

(C) A more complicated structure is obtained if successive symbols are not chosen independently
but their probabilities depend on preceding letters. In the simplest case of this type a choice
depends only on the preceding letter and not on ones before that. The statistical structure can
, the probability that letter i is followed
then be described by a set of transition probabilities pi (
by letter j. The indices i and j range over all the possible symbols. A second equivalent way of
specifying the structure is to give the “digram” probabilities p
, i.e., the relative frequency of
, (the probability of letter i), the transition probabilities
the digram i j. The letter frequencies p

j

i

j

i

(

)

)

;

3See, for example, S. Chandrasekhar, “Stochastic Problems in Physics and Astronomy,” Reviews of Modern Physics, v. 15, No. 1,

(

)

January 1943, p. 1.

4Kendall and Smith, Tables of Random Sampling Numbers, Cambridge, 1939.

5

pi (

j

and the digram probabilities p

i

j

are related by the following formulas:

)

(

;

)

p

i

p

i

j

p

j

i

p

j

(

) =

(

;

) =

(

;

) =

(

)

p j (

i

)

j

p

i

p

i

j

(

;

) =

(

)

pi (

j

)

j

j

pi (

j

j

p

i

p

i

j

1

) =

(

) =

(

;

) =

:

i

i

;

j

As a speciﬁc example suppose there are three letters A, B, C with the probability tables:

pi (

j

)

j
A B C
1
4
5
5
1
0
2
1
2
10
5

A 0
i B 1
2
C 1
2

i

p

i

p

i

j

(

)

(

;

)

A
B
C

9
27
16
27
2
27

A
A 0
i B 8
27
C 1
27

j
B
4
15
8
27
4
135

C
1
15
0
1
135

A typical message from this source is the following:
A B B A B A B A B A B A B A B B B A B B B B B A B A B A B A B A B B B A C A C A B
B A B B B B A B B A B A C B B B A B A.
The next increase in complexity would involve trigram frequencies but no more. The choice of
a letter would depend on the preceding two letters but not on the message before that point. A
would
set of trigram frequencies p
be required. Continuing in this way one obtains successively more complicated stochastic pro-
cesses. In the general n-gram case a set of n-gram probabilities p
or of transition
probabilities pi1 ;

or equivalently a set of transition probabilities pi j (

is required to specify the statistical structure.

i2 ; : : : ;

in(cid:0)1 (

i2 ;:::;

in )

in )

i1 ;

k

k

i

j

(

)

)

(

;

;

(D) Stochastic processes can also be deﬁned which produce a text consisting of a sequence of
“words.” Suppose there are ﬁve letters A, B, C, D, E and 16 “words” in the language with
associated probabilities:

.16 BEBE

.10 A
.04 ADEB .04 BED
.05 ADEE
.01 BADD .05 CA

.02 BEED .08 DAB
.04 DAD

.11 CABED .04 DEB
.05 CEED

.15 DEED
.01 EAB
.05 EE

Suppose successive “words” are chosen independently and are separated by a space. A typical
message might be:
DAB EE A BEBE DEED DEB ADEE ADEE EE DEB BEBE BEBE BEBE ADEE BED DEED
DEED CEED ADEE A DEED DEED BEBE CABED BEBE BED DAB DEED ADEB.
If all the words are of ﬁnite length this process is equivalent to one of the preceding type, but
the description may be simpler in terms of the word structure and probabilities. We may also
generalize here and introduce transition probabilities between words, etc.

These artiﬁcial languages are useful in constructing simple problems and examples to illustrate vari-
ous possibilities. We can also approximate to a natural language by means of a series of simple artiﬁcial
languages. The zero-order approximation is obtained by choosing all letters with the same probability and
independently. The ﬁrst-order approximation is obtained by choosing successive letters independently but
each letter having the same probability that it has in the natural language.5 Thus, in the ﬁrst-order ap-
proximation to English, E is chosen with probability .12 (its frequency in normal English) and W with
probability .02, but there is no inﬂuence between adjacent letters and no tendency to form the preferred

5Letter, digram and trigram frequencies are given in Secret and Urgent by Fletcher Pratt, Blue Ribbon Books, 1939. Word frequen-

cies are tabulated in Relative Frequency of English Speech Sounds, G. Dewey, Harvard University Press, 1923.

6

(cid:229)
(cid:229)
(cid:229)
(cid:229)
(cid:229)
(cid:229)
digrams such as TH, ED, etc. In the second-order approximation, digram structure is introduced. After a
letter is chosen, the next one is chosen in accordance with the frequencies with which the various letters
follow the ﬁrst one. This requires a table of digram frequencies pi(
. In the third-order approximation,
trigram structure is introduced. Each letter is chosen with probabilities which depend on the preceding two
letters.

j

)

3. THE SERIES OF APPROXIMATIONS TO ENGLISH

To give a visual idea of how this series of processes approaches a language, typical sequences in the approx-
imations to English have been constructed and are given below. In all cases we have assumed a 27-symbol
“alphabet,” the 26 letters and a space.

1. Zero-order approximation (symbols independent and equiprobable).

XFOML RXKHRJFFJUJ ZLPWCFWKCYJ FFJEYVKCQSGHYD QPAAMKBZAACIBZL-
HJQD.

2. First-order approximation (symbols independent but with frequencies of English text).

OCRO HLI RGWR NMIELWIS EU LL NBNESEBYA TH EEI ALHENHTTPA OOBTTVA
NAH BRL.

3. Second-order approximation (digram structure as in English).

ON IE ANTSOUTINYS ARE T INCTORE ST BE S DEAMY ACHIN D ILONASIVE TU-
COOWE AT TEASONARE FUSO TIZIN ANDY TOBE SEACE CTISBE.

4. Third-order approximation (trigram structure as in English).

IN NO IST LAT WHEY CRATICT FROURE BIRS GROCID PONDENOME OF DEMONS-
TURES OF THE REPTAGIN IS REGOACTIONA OF CRE.

5. First-order word approximation. Rather than continue with tetragram,

, n-gram structure it is easier
and better to jump at this point to word units. Here words are chosen independently but with their
appropriate frequencies.

: : :

REPRESENTING AND SPEEDILY IS AN GOOD APT OR COME CAN DIFFERENT NAT-
URAL HERE HE THE A IN CAME THE TO OF TO EXPERT GRAY COME TO FURNISHES
THE LINE MESSAGE HAD BE THESE.

6. Second-order word approximation. The word transition probabilities are correct but no further struc-

ture is included.

THE HEAD AND IN FRONTAL ATTACK ON AN ENGLISH WRITER THAT THE CHAR-
ACTER OF THIS POINT IS THEREFORE ANOTHER METHOD FOR THE LETTERS THAT
THE TIME OF WHO EVER TOLD THE PROBLEM FOR AN UNEXPECTED.

The resemblance to ordinary English text increases quite noticeably at each of the above steps. Note that
these samples have reasonably good structure out to about twice the range that is taken into account in their
construction. Thus in (3) the statistical process insures reasonable text for two-letter sequences, but four-
letter sequences from the sample can usually be ﬁtted into good sentences. In (6) sequences of four or more
words can easily be placed in sentences without unusual or strained constructions. The particular sequence
of ten words “attack on an English writer that the character of this” is not at all unreasonable. It appears then
that a sufﬁciently complex stochastic process will give a satisfactory representation of a discrete source.

The ﬁrst two samples were constructed by the use of a book of random numbers in conjunction with
(for example 2) a table of letter frequencies. This method might have been continued for (3), (4) and (5),
since digram, trigram and word frequency tables are available, but a simpler equivalent method was used.

7

To construct (3) for example, one opens a book at random and selects a letter at random on the page. This
letter is recorded. The book is then opened to another page and one reads until this letter is encountered.
The succeeding letter is then recorded. Turning to another page this second letter is searched for and the
succeeding letter recorded, etc. A similar process was used for (4), (5) and (6). It would be interesting if
further approximations could be constructed, but the labor involved becomes enormous at the next stage.

4. GRAPHICAL REPRESENTATION OF A MARKOFF PROCESS

Stochastic processes of the type described above are known mathematically as discrete Markoff processes
and have been extensively studied in the literature.6 The general case can be described as follows: There
exist a ﬁnite number of possible “states” of a system; S1 ;
Sn. In addition there is a set of transition
probabilities; pi (
the probability that if the system is in state Si it will next go to state S j. To make this
Markoff process into an information source we need only assume that a letter is produced for each transition
from one state to another. The states will correspond to the “residue of inﬂuence” from preceding letters.

S2 ; : : : ;

j

)

The situation can be represented graphically as shown in Figs. 3, 4 and 5. The “states” are the junction

A

.4

.1

B

E

.1

.2

C

D

.2

Fig. 3— A graph corresponding to the source in example B.

points in the graph and the probabilities and letters produced for a transition are given beside the correspond-
ing line. Figure 3 is for the example B in Section 2, while Fig. 4 corresponds to the example C. In Fig. 3

C

B

A

A

.8

.2

.5

B

C

.1

.5

.4

B

.5

Fig. 4— A graph corresponding to the source in example C.

there is only one state since successive letters are independent. In Fig. 4 there are as many states as letters.
If a trigram example were constructed there would be at most n2 states corresponding to the possible pairs
of letters preceding the one being chosen. Figure 5 is a graph for the case of word structure in example D.
Here S corresponds to the “space” symbol.

5. ERGODIC AND MIXED SOURCES

As we have indicated above a discrete source for our purposes can be considered to be represented by a
Markoff process. Among the possible discrete Markoff processes there is a group with special properties
of signiﬁcance in communication theory. This special class consists of the “ergodic” processes and we
shall call the corresponding sources ergodic sources. Although a rigorous deﬁnition of an ergodic process is
somewhat involved, the general idea is simple. In an ergodic process every sequence produced by the process

6For a detailed treatment see M. Fr´echet, M´ethode des fonctions arbitraires. Th´eorie des ´ev´enements en chaˆıne dans le cas d’un

nombre ﬁni d’´etats possibles. Paris, Gauthier-Villars, 1938.

8

is the same in statistical properties. Thus the letter frequencies, digram frequencies, etc., obtained from
particular sequences, will, as the lengths of the sequences increase, approach deﬁnite limits independent
of the particular sequence. Actually this is not true of every sequence but the set for which it is false has
probability zero. Roughly the ergodic property means statistical homogeneity.

All the examples of artiﬁcial languages given above are ergodic. This property is related to the structure
of the corresponding graph. If the graph has the following two properties7 the corresponding process will
be ergodic:

1. The graph does not consist of two isolated parts A and B such that it is impossible to go from junction
points in part A to junction points in part B along lines of the graph in the direction of arrows and also
impossible to go from junctions in part B to junctions in part A.

2. A closed series of lines in the graph with all arrows on the lines pointing in the same orientation will
be called a “circuit.” The “length” of a circuit is the number of lines in it. Thus in Fig. 5 series BEBES
is a circuit of length 5. The second property required is that the greatest common divisor of the lengths
of all circuits in the graph be one.

D

E

B

E

E

S

A

S

C

A

D

B

E

E

B

E

B

E

D

A

D

E

D

E

B

B

D

B

E

A

E

A

S

Fig. 5— A graph corresponding to the source in example D.

>

If the ﬁrst condition is satisﬁed but the second one violated by having the greatest common divisor equal
1, the sequences have a certain type of periodic structure. The various sequences fall into d different
to d
classes which are statistically the same apart from a shift of the origin (i.e., which letter in the sequence is
1 any sequence can be made statistically equivalent to any
called letter 1). By a shift of from 0 up to d
c. Letter a is
other. A simple example with d
followed with either b or c with probabilities 1
3 respectively. Either b or c is always followed by letter
a. Thus a typical sequence is

2 is the following: There are three possible letters a

3 and 2

b

(cid:0)

=

;

;

a b a c a c a c a b a c a b a b a c a c

:

This type of situation is not of much importance for our work.

If the ﬁrst condition is violated the graph may be separated into a set of subgraphs each of which satisﬁes
the ﬁrst condition. We will assume that the second condition is also satisﬁed for each subgraph. We have in
this case what may be called a “mixed” source made up of a number of pure components. The components
correspond to the various subgraphs. If L1, L2, L3 ; : : :

are the component sources we may write

7These are restatements in terms of the graph of conditions given in Fr´echet.

(cid:1) (cid:1) (cid:1)

L

=

p1L1 +

p2L2 +

p3L3 +

9

where pi is the probability of the component source Li.

Physically the situation represented is this: There are several different sources L1, L2, L3 ; : : :

which are
each of homogeneous statistical structure (i.e., they are ergodic). We do not know a priori which is to be
used, but once the sequence starts in a given pure component Li, it continues indeﬁnitely according to the
statistical structure of that component.

As an example one may take two of the processes deﬁned above and assume p1 = :

2 and p2 = :

8. A

sequence from the mixed source

2L1 + :
would be obtained by choosing ﬁrst L1 or L2 with probabilities .2 and .8 and after this choice generating a
sequence from whichever was chosen.

8L2

L

= :

Except when the contrary is stated we shall assume a source to be ergodic. This assumption enables one
to identify averages along a sequence with averages over the ensemble of possible sequences (the probability
of a discrepancy being zero). For example the relative frequency of the letter A in a particular inﬁnite
sequence will be, with probability one, equal to its relative frequency in the ensemble of sequences.

If Pi is the probability of state i and pi (

j

)

the transition probability to state j, then for the process to be

stationary it is clear that the Pi must satisfy equilibrium conditions:

Pj =

Pi pi (

j

):

i

In the ergodic case it can be shown that with any starting conditions the probabilities Pj (
j after N symbols, approach the equilibrium values as N

.

N

)

of being in state

6. CHOICE, UNCERTAINTY AND ENTROPY

!

We have represented a discrete information source as a Markoff process. Can we deﬁne a quantity which
will measure, in some sense, how much information is “produced” by such a process, or better, at what rate
information is produced?

Suppose we have a set of possible events whose probabilities of occurrence are p1 ;

pn. These
probabilities are known but that is all we know concerning which event will occur. Can we ﬁnd a measure
of how much “choice” is involved in the selection of the event or of how uncertain we are of the outcome?
, it is reasonable to require of it the following properties:

If there is such a measure, say H

p2 ; : : : ;

p2 ; : : : ;

pn )

p1 ;

(

1. H should be continuous in the pi.

2. If all the pi are equal, pi =

1
n , then H should be a monotonic increasing function of n. With equally

likely events there is more choice, or uncertainty, when there are more possible events.

3. If a choice be broken down into two successive choices, the original H should be the weighted sum
of the individual values of H. The meaning of this is illustrated in Fig. 6. At the left we have three

1/2

1/2

1/3

1/2

1/6

1/2

2/3

1/3

1/3

1/6

Fig. 6— Decomposition of a choice from three possibilities.

possibilities p1 =
probability 1
have the same probabilities as before. We require, in this special case, that

2 , and if the second occurs make another choice with probabilities 2

1
6 . On the right we ﬁrst choose between two possibilities each with
3 . The ﬁnal results

1
2 , p2 =

1
3 , p3 =

3 , 1

The coefﬁcient 1

2 is because this second choice only occurs half the time.

H

(

1
2 ;

1
3 ;

1
6 ) =

H

(

1
2 ;

1
2 ) +

1
2 H

(

2
3 ;

1
3 ):

10

(cid:229)
¥
In Appendix 2, the following result is established:

Theorem 2: Theonly H satisfyingthethreeaboveassumptionsisoftheform:

n

H

=

K

pi log pi

(cid:0)

i

1

=

where K isapositiveconstant.

This theorem, and the assumptions required for its proof, are in no way necessary for the present theory.
It is given chieﬂy to lend a certain plausibility to some of our later deﬁnitions. The real justiﬁcation of these
deﬁnitions, however, will reside in their implications.

=

(cid:0)

Quantities of the form H

(cid:229) pi log pi (the constant K merely amounts to a choice of a unit of measure)
play a central role in information theory as measures of information, choice and uncertainty. The form of H
will be recognized as that of entropy as deﬁned in certain formulations of statistical mechanics8 where pi is
the probability of a system being in cell i of its phase space. H is then, for example, the H in Boltzmann’s
famous H theorem. We shall call H
pn. If x is a
for its entropy; thus x is not an argument of a function but a label for a
x
chance variable we will write H
number, to differentiate it from H
say, the entropy of the chance variable y.
1

The entropy in the case of two possibilities with probabilities p and q

(cid:229) pi log pi the entropy of the set of probabilities p1 ; : : : ;

p, namely

y

=

(cid:0)

(

(

)

)

is plotted in Fig. 7 as a function of p.

H

p log p

q logq

=

(

+

)

(cid:0)

=

(cid:0)

H
BITS

1.0

.9

.8

.7

.6

.5

.4

.3

.2

.1

0

0

.1

.2

.3

.4

.5

.6

.7

.8

.9

1.0

p

Fig. 7— Entropy in the case of two possibilities with probabilities p and

1 (cid:0) p

.

(

)

The quantity H has a number of interesting properties which further substantiate it as a reasonable

measure of choice or information.

1. H

0 if and only if all the pi but one are zero, this one having the value unity. Thus only when we

=

are certain of the outcome does H vanish. Otherwise H is positive.

2. For a given n, H is a maximum and equal to logn when all the pi are equal (i.e., 1

n ). This is also

intuitively the most uncertain situation.

8See, for example, R. C. Tolman, Principles of Statistical Mechanics, Oxford, Clarendon, 1938.

11

(cid:229)
3. Suppose there are two events, x and y, in question with m possibilities for the ﬁrst and n for the second.
be the probability of the joint occurrence of i for the ﬁrst and j for the second. The entropy of the

j

Let p
i
joint event is

)

(

;

while

It is easily shown that

H

x

y

p

i

j

log p

i

j

(

;

) =

(

;

)

(

;

)

(cid:0)

i

;

j

H

x

p

i

j

log(cid:229)

p

i

j

(

) =

(

;

)

(

;

)

(cid:0)

i

;

j

j

p

i

j

log(cid:229)

p

i

j

H

y

(

) =

(

;

)

(

;

):

(cid:0)

i

;

j

i

H

x

y

H

x

H

y

(

;

)

(

) +

(

)

with equality only if the events are independent (i.e., p
j
less than or equal to the sum of the individual uncertainties.

i

(cid:20)

(

;

) =

p

i

p

j

). The uncertainty of a joint event is

(

)

(

)

4. Any change toward equalization of the probabilities p1 ;

p2 and
we increase p1, decreasing p2 an equal amount so that p1 and p2 are more nearly equal, then H increases.
More generally, if we perform any “averaging” operation on the pi of the form

pn increases H. Thus if p1 <

p2 ; : : : ;

p0

i =

ai j p j

j

where (cid:229)
mation amounts to no more than a permutation of the p j with H of course remaining the same).

0, then H increases (except in the special case where this transfor-

1, and all ai j

j ai j =

i ai j =

(cid:21)

5. Suppose there are two chance events x and y as in 3, not necessarily independent. For any particular

value i that x can assume there is a conditional probability pi (

j

)

that y has the value j. This is given by

pi (

j

) =

(

p
i
j p

;

(

j
i

)

j

;

)

:

We deﬁne the conditional entropy of y, Hx (
according to the probability of getting that particular x. That is

y

)

as the average of the entropy of y for each value of x, weighted

Hx (

y

) =

(

;

)

p

i

j

log pi (

j

) :

(cid:0)

i

;

j

This quantity measures how uncertain we are of y on the average when we know x. Substituting the value of
pi (

we obtain

j

)

Hx (

y

p

i

j

log p

i

j

p

i

j

log(cid:229)

p

i

j

) =

(

;

)

(

;

) +

(

;

)

(

;

)

(cid:0)

i

j

i

j

j

;

;

H

x

y

H

x

=

(

;

)

(

)

(cid:0)

H

x

y

H

x

(

;

) =

(

) +

Hx (

y

):

or

The uncertainty (or entropy) of the joint event x
known.

;

6. From 3 and 5 we have

y is the uncertainty of x plus the uncertainty of y when x is

Hence

H

x

H

y

H

x

y

H

x

(

) +

(

)

(

;

) =

(

) +

Hx(

y

):

(cid:21)

H

y

(

)

Hx (

y

):

The uncertainty of y is never increased by knowledge of x. It will be decreased unless x and y are independent
events, in which case it is not changed.

(cid:21)

12

(cid:229)
(cid:229)
(cid:229)
(cid:229)
(cid:229)
(cid:229)
(cid:229)
(cid:229)
(cid:229)
7. THE ENTROPY OF AN INFORMATION SOURCE

Consider a discrete source of the ﬁnite state type considered above. For each possible state i there will be a
of producing the various possible symbols j. Thus there is an entropy Hi for each
set of probabilities pi (
state. The entropy of the source will be deﬁned as the average of these Hi weighted in accordance with the
probability of occurrence of the states in question:

j

)

H

=

PiHi

i

Pi pi (

j

)

log pi(

j

) :

=

(cid:0)

i

;

j

This is the entropy of the source per symbol of text. If the Markoff process is proceeding at a deﬁnite time
rate there is also an entropy per second

where fi is the average frequency (occurrences per second) of state i. Clearly

H 0

mH

=

H 0

=

fiHi

i

where m is the average number of symbols produced per second. H or H 0 measures the amount of informa-
tion generated by the source per symbol or per second. If the logarithmic base is 2, they will represent bits
per symbol or per second.

If successive symbols are independent then H is simply

(cid:229) pi log pi where pi is the probability of sym-
bol i. Suppose in this case we consider a long message of N symbols. It will contain with high probability
about p1N occurrences of the ﬁrst symbol, p2N occurrences of the second, etc. Hence the probability of this
particular message will be roughly

(cid:0)

p

=

pp1N
1

pp2N
2

ppnN
n

or

(cid:1) (cid:1) (cid:1)

log p :

=

N (cid:229)

pi log pi

log p :

=

H :

=

i
NH

(cid:0)

log1

=

p
N :

H is thus approximately the logarithm of the reciprocal probability of a typical long sequence divided by the
number of symbols in the sequence. The same result holds for any source. Stated more precisely we have
(see Appendix 3):

Theorem 3: Givenany

0 and

(cid:15) >

(cid:14) >

0,wecanﬁndan N0 suchthatthesequencesofanylengthN

N0

fallintotwoclasses:

1. Asetwhosetotalprobabilityislessthan

.

(cid:15)

(cid:21)

2. Theremainder,allofwhosemembershaveprobabilitiessatisfyingtheinequality

log p(cid:0)1
N

H

(cid:0)

(cid:12)

(cid:12)

< (cid:14) :

In other words we are almost certain to have
A closely related result deals with the number of sequences of various probabilities. Consider again the
sequences of length N and let them be arranged in order of decreasing probability. We deﬁne n
to be
the number we must take from this set starting with the most probable one in order to accumulate a total
probability q for those taken.

very close to H when N is large.

q

(

)

(cid:12)

(cid:12)

(cid:12)

(cid:12)

(cid:12)

(cid:12)

log p(cid:0)1
N

13

(cid:229)
(cid:229)
(cid:229)
Theorem 4:

when q doesnotequal0 or 1.
q
We may interpret log n

(

)

Lim
N!

q

(

)

log n
N

H

=

log n
N

as the number of bits required to specify the sequence when we consider only
q

the most probable sequences with a total probability q. Then
is the number of bits per symbol for
the speciﬁcation. The theorem says that for large N this will be independent of q and equal to H. The rate
of growth of the logarithm of the number of reasonably probable sequences is given by H, regardless of our
interpretation of “reasonably probable.” Due to these results, which are proved in Appendix 3, it is possible
for most purposes to treat the long sequences as though there were just 2HN of them, each with a probability
2(cid:0)HN.

(

)

The next two theorems show that H and H 0 can be determined by limiting operations directly from
the statistics of the message sequences, without reference to the states and transition probabilities between
states.

Theorem 5: Let p

Bi )

betheprobabilityofasequenceBi ofsymbolsfromthesource. Let

(

GN =

1
N

(cid:0)

i

p

Bi )

log p

(

Bi )

(

wherethesumisoverallsequences Bi containingN symbols. ThenGN isamonotonicdecreasingfunction
of N and

Lim
N!

GN =

H

:

Theorem 6: Let p
Bi)
Bi ;

S j )=

p

(

p

(

betheconditionalprobabilityof S j after Bi. Let

Bi ;

S j )

(

be the probability of sequence Bi followed by symbol S j and pBi (

S j ) =

FN =

p

(

Bi ;

S j )

log pBi (

S j )

(cid:0)

i

;

j

where the sum is over all blocks Bi of N
decreasingfunctionof N,

(cid:0)

1 symbols and over all symbols S j. Then FN is a monotonic

FN =

GN =

FN

(cid:20)

and LimN!

¥ FN =

H.

NGN
N

1
N

=

n
GN ;

N

1

(

)

GN(cid:0)1 ;

(cid:0)

(cid:0)

Fn ;

1

These results are derived in Appendix 3. They show that a series of approximations to H can be obtained
N symbols. FN is the
by considering only the statistical structure of the sequences extending over 1
better approximation. In fact FN is the entropy of the Nth order approximation to the source of the type
discussed above. If there are no statistical inﬂuences extending over more than N symbols, that is if the
is not changed by a knowledge of
conditional probability of the next symbol knowing the preceding
any before that, then FN =
1
preceding ones are known, while GN is the entropy per symbol of blocks of N symbols.

H. FN of course is the conditional entropy of the next symbol when the

N

N

2

1

; : : : ;

(cid:0)

(cid:0)

)

(

)

(

;

The ratio of the entropy of a source to the maximum value it could have while still restricted to the same
symbols will be called its relative entropy. This is the maximum compression possible when we encode into
the same alphabet. One minus the relative entropy is the redundancy. The redundancy of ordinary English,
not considering statistical structure over greater distances than about eight letters, is roughly 50%. This
means that when we write English half of what we write is determined by the structure of the language and
half is chosen freely. The ﬁgure 50% was found by several independent methods which all gave results in

14

¥
(cid:229)
¥
(cid:229)
(cid:229)
this neighborhood. One is by calculation of the entropy of the approximations to English. A second method
is to delete a certain fraction of the letters from a sample of English text and then let someone attempt to
restore them. If they can be restored when 50% are deleted the redundancy must be greater than 50%. A
third method depends on certain known results in cryptography.

Two extremes of redundancy in English prose are represented by Basic English and by James Joyce’s
book “Finnegans Wake”. The Basic English vocabulary is limited to 850 words and the redundancy is very
high. This is reﬂected in the expansion that occurs when a passage is translated into Basic English. Joyce
on the other hand enlarges the vocabulary and is alleged to achieve a compression of semantic content.

The redundancy of a language is related to the existence of crossword puzzles. If the redundancy is
zero any sequence of letters is a reasonable text in the language and any two-dimensional array of letters
forms a crossword puzzle. If the redundancy is too high the language imposes too many constraints for large
crossword puzzles to be possible. A more detailed analysis shows that if we assume the constraints imposed
by the language are of a rather chaotic and random nature, large crossword puzzles are just possible when
the redundancy is 50%. If the redundancy is 33%, three-dimensional crossword puzzles should be possible,
etc.

8. REPRESENTATION OF THE ENCODING AND DECODING OPERATIONS

We have yet to represent mathematically the operations performed by the transmitter and receiver in en-
coding and decoding the information. Either of these will be called a discrete transducer. The input to the
transducer is a sequence of input symbols and its output a sequence of output symbols. The transducer may
have an internal memory so that its output depends not only on the present input symbol but also on the past
history. We assume that the internal memory is ﬁnite, i.e., there exist a ﬁnite number m of possible states of
the transducer and that its output is a function of the present state and the present input symbol. The next
state will be a second function of these two quantities. Thus a transducer can be described by two functions:

yn =

(cid:11)n

1 =

+

f
g

where

xn is the nth input symbol,

xn ; (cid:11)n )
xn ; (cid:11)n )

(

(

(cid:11)n is the state of the transducer when the nth input symbol is introduced,

yn is the output symbol (or sequence of output symbols) produced when xn is introduced if the state is

(cid:11)n.

If the output symbols of one transducer can be identiﬁed with the input symbols of a second, they can be
connected in tandem and the result is also a transducer. If there exists a second transducer which operates
on the output of the ﬁrst and recovers the original input, the ﬁrst transducer will be called non-singular and
the second will be called its inverse.

Theorem 7: The output of a ﬁnite state transducer driven by a ﬁnite state statistical source is a ﬁnite
state statistical source,with entropy(perunittime)less than orequalto that ofthe input. Ifthe transducer
isnon-singulartheyareequal.

(cid:11)

Let

(cid:11)1 can produce an x which changes

represent the state of the source, which produces a sequence of symbols xi; and let

be the state of
the transducer, which produces, in its output, blocks of symbols y j. The combined system can be represented
, are connected by
by the “product state space” of pairs
and
a line if
(cid:12)2, and this line is given the probability of that x in this
case. The line is labeled with the block of y j symbols produced by the transducer. The entropy of the output
can be calculated as the weighted sum over the states. If we sum ﬁrst on
each resulting term is less than or
, hence the entropy is not increased. If the transducer is non-singular
equal to the corresponding term for
3 are the output entropies of the source,
let its output be connected to the inverse transducer. If H 0
1, H 0
2 and H 0
1 and therefore H 0
H 0
H 0
H 0
the ﬁrst and second transducers respectively, then H 0
1 =
3 =
2
1

. Two points in the space

((cid:11)1 ; (cid:12)1 )

((cid:11)2 ; (cid:12)2 )

(cid:12)1 to

2.
H 0

((cid:11); (cid:12) )

(cid:11)

(cid:12)

(cid:12)

(cid:21)

(cid:21)

15

Suppose we have a system of constraints on possible sequences of the type which can be represented by
s
a linear graph as in Fig. 2. If probabilities p(
i j were assigned to the various lines connecting state i to state j
this would become a source. There is one particular assignment which maximizes the resulting entropy (see
Appendix 4).

)

Theorem 8: Let the system of constraints considered as a channel have a capacity C

logW. If we

=

assign

where

‘

(

s
i j isthedurationofthe sth symbolleadingfromstate i tostate j andthe Bi satisfy

)

p(

s
i j =

)

B j
Bi

W (cid:0)

‘

s
i j

(

)

Bi =

B jW (cid:0)

‘

s

;

j

s
i j

(

)

then H ismaximizedandequaltoC.

By proper assignment of the transition probabilities the entropy of symbols on a channel can be maxi-

mized at the channel capacity.

9. THE FUNDAMENTAL THEOREM FOR A NOISELESS CHANNEL

We will now justify our interpretation of H as the rate of generating information by proving that H deter-
mines the channel capacity required with most efﬁcient coding.
bits per symbol

bits per
. Then it is possible to encode the output of the sourcein such a way as to transmit at the average

Theorem 9: Let a source have entropy H

and a channel have a capacity C

)

(

(

symbolspersecondoverthechannelwhere

isarbitrarilysmall. Itisnotpossibletotransmitat

(cid:15)

(cid:15)

)

second
C
H

rate

(cid:0)

anaveragerategreaterthan

C
H

.

The converse part of the theorem, that

cannot be exceeded, may be proved by noting that the entropy
of the channel input per second is equal to that of the source, since the transmitter must be non-singular, and
C and the number of symbols per second
also this entropy cannot exceed the channel capacity. Hence H 0

C
H

H 0

H

C

H.

=

=

=

(cid:20)

(cid:20)

The ﬁrst part of the theorem will be proved in two different ways. The ﬁrst method is to consider the
set of all sequences of N symbols produced by the source. For N large we can divide these into two groups,
N members and the second containing less than 2RN members (where R is
one containing less than 2(
. As N increases
the logarithm of the number of different symbols) and having a total probability less than

H

+

(cid:17)

)

(cid:22)

and

approach zero. The number of signals of duration T in the channel is greater than 2(

C(cid:0)

T with

(cid:18)

)

(cid:17)

(cid:22)

(cid:18)

small when T is large. if we choose

T

=

H
C + (cid:21)

N

then there will be a sufﬁcient number of sequences of channel symbols for the high probability group when
) and also some additional ones. The high probability group
N and T are sufﬁciently large (however small
is coded in an arbitrary one-to-one way into this set. The remaining sequences are represented by larger
sequences, starting and ending with one of the sequences not used for the high probability group. This
special sequence acts as a start and stop signal for a different code. In between a sufﬁcient time is allowed
to give enough different sequences for all the low probability messages. This will require

(cid:18)

(cid:19)

(cid:21)

where

’

is small. The mean rate of transmission in message symbols per second will then be greater than

(cid:19)

(cid:18)

T1 =

R
C + ’

N

1

(

(cid:14))

T
N + (cid:14)

T1
N

(cid:0)1

1

=

(

(cid:14))

H
C + (cid:21)

+ (cid:14)

R
C + ’

(cid:0)1

:

(cid:0)

(cid:0)

#

(cid:20)

(cid:20)

(cid:21)

(cid:16)

(cid:17)

(cid:16)

(cid:17)

16

(cid:229)
As N increases

,

and

approach zero and the rate approaches

(cid:14)

(cid:21)

’

C
H

.

Another method of performing this coding and thereby proving the theorem can be described as follows:
Arrange the messages of length N in order of decreasing probability and suppose their probabilities are
p1
pi; that is Ps is the cumulative probability up to, but not including, ps.
We ﬁrst encode into a binary system. The binary code for message s is obtained by expanding Ps as a binary
number. The expansion is carried out to ms places, where ms is the integer satisfying:

pn. Let Ps =

s(cid:0)1
1

p2

p3

(cid:1) (cid:1) (cid:1) (cid:21)

(cid:21)

(cid:21)

log2

1
ps (cid:20)

ms <

1

+

log2

1
ps :

Thus the messages of high probability are represented by short codes and those of low probability by long
codes. From these inequalities we have

1
2ms

(cid:20)

ps <

1
2ms(cid:0)1 :

The code for Ps will differ from all succeeding ones in one or more of its ms places, since all the remaining
1
Pi are at least
2ms larger and their binary expansions therefore differ in the ﬁrst ms places. Consequently all
the codes are different and it is possible to recover the message from its code. If the channel sequences are
not already sequences of binary digits, they can be ascribed binary numbers in an arbitrary fashion and the
binary code thus translated into signals suitable for the channel.

The average number H 0 of binary digits used per symbol of original message is easily estimated. We

have

But,

and therefore,

H 0

=

(cid:229) ms ps :

1
N

1
N

log2

1
ps

1
N

ps

(cid:20)

(cid:229) ms ps <

1
N

1

+

log2

1
ps

ps

(cid:16)

(cid:17)

(cid:16)

(cid:17)

GN

H 0

GN +

<

(cid:20)

1
N

As N increases GN approaches H, the entropy of the source and H 0 approaches H.

We see from this that the inefﬁciency in coding, when only a ﬁnite delay of N symbols is used, need
N plus the difference between the true entropy H and the entropy GN calculated for

not be greater than 1
sequences of length N. The per cent excess time needed over the ideal is therefore less than

GN
H +

1
HN

1

:

(cid:0)

This method of encoding is substantially the same as one found independently by R. M. Fano.9 His
method is to arrange the messages of length N in order of decreasing probability. Divide this series into two
groups of as nearly equal probability as possible. If the message is in the ﬁrst group its ﬁrst binary digit
will be 0, otherwise 1. The groups are similarly divided into subsets of nearly equal probability and the
particular subset determines the second binary digit. This process is continued until each subset contains
only one message. It is easily seen that apart from minor differences (generally in the last digit) this amounts
to the same thing as the arithmetic process described above.

10. DISCUSSION AND EXAMPLES

In order to obtain the maximum power transfer from a generator to a load, a transformer must in general be
introduced so that the generator as seen from the load has the load resistance. The situation here is roughly
analogous. The transducer which does the encoding should match the source to the channel in a statistical
sense. The source as seen from the channel through the transducer should have the same statistical structure

9Technical Report No. 65, The Research Laboratory of Electronics, M.I.T., March 17, 1949.

17

(cid:229)
(cid:229)
(cid:229)
as the source which maximizes the entropy in the channel. The content of Theorem 9 is that, although an
exact match is not in general possible, we can approximate it as closely as desired. The ratio of the actual
rate of transmission to the capacity C may be called the efﬁciency of the coding system. This is of course
equal to the ratio of the actual entropy of the channel symbols to the maximum possible entropy.

In general, ideal or nearly ideal encoding requires a long delay in the transmitter and receiver. In the
noiseless case which we have been considering, the main function of this delay is to allow reasonably good
matching of probabilities to corresponding lengths of sequences. With a good code the logarithm of the
reciprocal probability of a long message must be proportional to the duration of the corresponding signal, in
fact

log p(cid:0)1
T

C

(cid:0)

must be small for all but a small fraction of the long messages.

(cid:12)

(cid:12)

(cid:12)

(cid:12)

(cid:12)

(cid:12)

(cid:25)

If a source can produce only one particular message its entropy is zero, and no channel is required. For
example, a computing machine set up to calculate the successive digits of
produces a deﬁnite sequence
with no chance element. No channel is required to “transmit” this to another point. One could construct a
second machine to compute the same sequence at the point. However, this may be impractical. In such a case
we can choose to ignore some or all of the statistical knowledge we have of the source. We might consider
the digits of
to be a random sequence in that we construct a system capable of sending any sequence of
digits. In a similar way we may choose to use some of our statistical knowledge of English in constructing
a code, but not all of it. In such a case we consider the source with the maximum entropy subject to the
statistical conditions we wish to retain. The entropy of this source determines the channel capacity which
is necessary and sufﬁcient. In the
example the only information retained is that all the digits are chosen
from the set 0
9. In the case of English one might wish to use the statistical saving possible due to
1
letter frequencies, but nothing else. The maximum entropy source is then the ﬁrst approximation to English
and its entropy determines the required channel capacity.

; : : : ;

(cid:25)

(cid:25)

;

As a simple example of some of these results consider a source which produces a sequence of letters
8 , 1
8 , successive symbols being chosen independently.

chosen from among A, B, C, D with probabilities 1
We have

2 , 1

4 , 1

H

=

=

1

1

2 log 1

4 log 1
2 +
7
4 bits per symbol

(cid:0)

:

(cid:0)

4 +

2

8 log 1

8

(cid:1)

Thus we can approximate a coding system to encode messages from this source into binary digits with an
average of 7
4 binary digit per symbol. In this case we can actually achieve the limiting value by the following
code (obtained by the method of the second proof of Theorem 9):

A
B
C
D

0
10
110
111

The average number of binary digits used in encoding a sequence of N symbols will be

N

1
2

1

+

1
4

2

+

2
8

3

=

7
4 N

:

(cid:2)

(cid:2)

(cid:2)

It is easily seen that the binary digits 0, 1 have probabilities 1
bit per symbol. Since, on the average, we have 7
basis are the same. The maximum possible entropy for the original set is log4
D have probabilities 1
the original set of symbols on a two-to-one basis by the following table:

2 so the H for the coded sequences is one
4 binary symbols per original letter, the entropies on a time
2, occurring when A, B, C,
8 . We can translate the binary sequences into

4 . Hence the relative entropy is 7

2 , 1

4 , 1

4 , 1

4 , 1

=

(cid:1)

(cid:0)

00
01
10
11

A0
B0
C0
D0

18

This double process then encodes the original message into the same symbols but with an average compres-
sion ratio 7
8 .

As a second example consider a source which produces a sequence of A’s and B’s with probability p for

A and q for B. If p

q we have

(cid:28)

H

log pp

1

1(cid:0)p

p

=

(

)

(cid:0)

1

p

(

)

1(cid:0)p

p

(

)=

(cid:0)

(cid:0)

(cid:0)

p log p
e
p :

p log

=

:

=

In such a case one can construct a fairly good coding of the message on a 0, 1 channel by sending a special
sequence, say 0000, for the infrequent symbol A and then a sequence indicating the number of B’s following
it. This could be indicated by the binary representation with all numbers containing the special sequence
deleted. All numbers up to 16 are represented as usual; 16 is represented by the next binary number after 16
10001, etc.
which does not contain four zeros, namely 17

=

It can be shown that as p

0 the coding approaches ideal provided the length of the special sequence is

properly adjusted.

!

PART II: THE DISCRETE CHANNEL WITH NOISE

11. REPRESENTATION OF A NOISY DISCRETE CHANNEL

We now consider the case where the signal is perturbed by noise during transmission or at one or the other
of the terminals. This means that the received signal is not necessarily the same as that sent out by the
transmitter. Two cases may be distinguished. If a particular transmitted signal always produces the same
received signal, i.e., the received signal is a deﬁnite function of the transmitted signal, then the effect may be
called distortion. If this function has an inverse — no two transmitted signals producing the same received
signal — distortion may be corrected, at least in principle, by merely performing the inverse functional
operation on the received signal.

The case of interest here is that in which the signal does not always undergo the same change in trans-
mission. In this case we may assume the received signal E to be a function of the transmitted signal S and a
second variable, the noise N.

E

f

S

N

=

(

;

)

The noise is considered to be a chance variable just as the message was above. In general it may be repre-
sented by a suitable stochastic process. The most general type of noisy discrete channel we shall consider
is a generalization of the ﬁnite state noise-free channel described previously. We assume a ﬁnite number of
states and a set of probabilities

p

i ((cid:12) ;

;

(cid:11)

j

):

)

(cid:12)

(cid:12)

(cid:11)

(cid:11)

and

. Thus

, the probability of transmitted symbol i being received as j.

and symbol i is transmitted, that symbol j will be received
This is the probability, if the channel is in state
and the channel left in state
range over the possible states, i over the possible transmitted
signals and j over the possible received signals. In the case where successive symbols are independently per-
turbed by the noise there is only one state, and the channel is described by the set of transition probabilities
pi (

j
If a noisy channel is fed by a source there are two statistical processes at work: the source and the noise.
Thus there are a number of entropies that can be calculated. First there is the entropy H
of the source
or of the input to the channel (these will be equal if the transmitter is non-singular). The entropy of the
x
output of the channel, i.e., the received signal, will be denoted by H
.
The joint entropy of input and output will be H
and
, the entropy of the output when the input is known and conversely. Among these quantities we have
Hy (
the relations

. Finally there are two conditional entropies Hx (

. In the noiseless case H

H
y

xy

x

y

y

x

) =

)

)

)

(

)

)

(

)

(

(

(

All of these entropies can be measured on a per-second or a per-symbol basis.

H

x

y

H

x

(

;

) =

(

) +

Hx(

y

H

y

) =

(

) +

Hy(

x

):

19

12. EQUIVOCATION AND CHANNEL CAPACITY

If the channel is noisy it is not in general possible to reconstruct the original message or the transmitted
signal with certainty by any operation on the received signal E. There are, however, ways of transmitting
the information which are optimal in combating noise. This is the problem which we now consider.

p1 =

Suppose there are two possible symbols 0 and 1, and we are transmitting at a rate of 1000 symbols per
1
second with probabilities p0 =
2 . Thus our source is producing information at the rate of 1000 bits
per second. During transmission the noise introduces errors so that, on the average, 1 in 100 is received
incorrectly (a 0 as 1, or 1 as 0). What is the rate of transmission of information? Certainly less than 1000
bits per second since about 1% of the received symbols are incorrect. Our ﬁrst impulse might be to say
the rate is 990 bits per second, merely subtracting the expected number of errors. This is not satisfactory
since it fails to take into account the recipient’s lack of knowledge of where the errors occur. We may carry
it to an extreme case and suppose the noise so great that the received symbols are entirely independent of
the transmitted symbols. The probability of receiving 1 is 1
2 whatever was transmitted and similarly for 0.
Then about half of the received symbols are correct due to chance alone, and we would be giving the system
credit for transmitting 500 bits per second while actually no information is being transmitted at all. Equally
“good” transmission would be obtained by dispensing with the channel entirely and ﬂipping a coin at the
receiving point.

Evidently the proper correction to apply to the amount of information transmitted is the amount of this
information which is missing in the received signal, or alternatively the uncertainty when we have received
a signal of what was actually sent. From our previous discussion of entropy as a measure of uncertainty it
seems reasonable to use the conditional entropy of the message, knowing the received signal, as a measure
of this missing information. This is indeed the proper deﬁnition, as we shall see later. Following this idea
the rate of actual transmission, R, would be obtained by subtracting from the rate of production (i.e., the
entropy of the source) the average rate of conditional entropy.

R

H

x

=

(

)

Hy(

x

)

(cid:0)

x
The conditional entropy Hy (
ambiguity of the received signal.

)

will, for convenience, be called the equivocation. It measures the average

In the example considered above, if a 0 is received the a posteriori probability that a 0 was transmitted

is .99, and that a 1 was transmitted is .01. These ﬁgures are reversed if a 1 is received. Hence

Hy (

x

) =

[:

99

99 log

0
081 bits/symbol

+

:

(cid:0)

01 log0

01

:

:

]

= :

or 81 bits per second. We may say that the system is transmitting at a rate 1000
919 bits per second.
In the extreme case where a 0 is equally likely to be received as a 0 or 1 and similarly for 1, the a posteriori
probabilities are 1

81

=

(cid:0)

2 , 1

2 and

Hy (

x

) =

1

1

2 log 1
1 bit per symbol

2 +

2 log 1

2

(cid:0)

=

(cid:2)

(cid:3)

or 1000 bits per second. The rate of transmission is then 0 as it should be.

The following theorem gives a direct intuitive interpretation of the equivocation and also serves to justify
it as the unique appropriate measure. We consider a communication system and an observer (or auxiliary
device) who can see both what is sent and what is recovered (with errors due to noise). This observer notes
the errors in the recovered message and transmits data to the receiving point over a “correction channel” to
enable the receiver to correct the errors. The situation is indicated schematically in Fig. 8.

Theorem 10: If the correction channel has a capacity equal to Hy (

x

)

correctiondataastosenditoverthischannelandcorrectallbutanarbitrarilysmallfraction
ThisisnotpossibleifthechannelcapacityislessthanHy (

x

.

)

it is possible to so encode the
oftheerrors.

(cid:15)

20

CORRECTION DATA

OBSERVER

M

SOURCE

TRANSMITTER

RECEIVER

M 0

M

CORRECTING
DEVICE

Fig. 8— Schematic diagram of a correction system.

Roughly then, Hy (

x
receiving point to correct the received message.

)

is the amount of additional information that must be supplied per second at the

To prove the ﬁrst part, consider long sequences of received message M 0 and corresponding original
of the M’s which could reasonably have produced each
frequency of errors

binary digits to send each T seconds. This can be done with

message M. There will be logarithmically T Hy (
M 0. Thus we have T Hy (
x
on a channel of capacity Hy (

x

x

.

(cid:15)

)

)

)

The second part can be proved by noting, ﬁrst, that for any discrete chance variables x, y, z

The left-hand side can be expanded to give

Hy (

x

z

;

)

Hy (

x

):

(cid:21)

Hy (
z
Hy (

x

)

Hyz(
x
Hy (

z

)

(cid:21)

Hy (
x
Hy (

x

) +

)

)

H

z

)

(

):

Hyz (

x

)

(cid:21)

(cid:0)

(cid:21)

(cid:0)

If we identify x as the output of the source, y as the received signal and z as the signal sent over the correction
channel, then the right-hand side is the equivocation less the rate of transmission over the correction channel.
If the capacity of this channel is less than the equivocation the right-hand side will be greater than zero and
Hyz (
0. But this is the uncertainty of what was sent, knowing both the received signal and the correction
x
signal. If this is greater than zero the frequency of errors cannot be arbitrarily small.

) >

Example:

=

1

Suppose the errors occur at random in a sequence of binary digits: probability p that a digit is wrong
and q
p that it is right. These errors can be corrected if their position is known. Thus the
correction channel need only send information as to these positions. This amounts to transmitting
from a source which produces binary digits with probability p for 1 (incorrect) and q for 0 (correct).
This requires a channel of capacity

(cid:0)

which is the equivocation of the original system.

(cid:0)

p log p

q logq

[

+

]

The rate of transmission R can be written in two other forms due to the identities noted above. We have

R

=

H
H

(

)

x
y

=

(

)

H

x

x
y

Hy(
Hx(
y
H

)

)

(cid:0)

(cid:0)

H

x

y

=

(

) +

(

)

(

;

):

(cid:0)

21

The ﬁrst deﬁning expression has already been interpreted as the amount of information sent less the uncer-
tainty of what was sent. The second measures the amount received less the part of this which is due to noise.
The third is the sum of the two amounts less the joint entropy and therefore in a sense is the number of bits
per second common to the two. Thus all three expressions have a certain intuitive signiﬁcance.

The capacity C of a noisy channel should be the maximum possible rate of transmission, i.e., the rate

when the source is properly matched to the channel. We therefore deﬁne the channel capacity by

C

Max

H

x

=

(

)

Hy(

x

)

(cid:0)

where the maximum is with respect to all possible information sources used as input to the channel. If the
channel is noiseless, Hy (
0. The deﬁnition is then equivalent to that already given for a noiseless channel
since the maximum entropy for the channel is its capacity.

x

) =

(cid:0)

(cid:1)

13. THE FUNDAMENTAL THEOREM FOR A DISCRETE CHANNEL WITH NOISE

It may seem surprising that we should deﬁne a deﬁnite capacity C for a noisy channel since we can never
send certain information in such a case. It is clear, however, that by sending the information in a redundant
form the probability of errors can be reduced. For example, by repeating the message many times and by a
statistical study of the different received versions of the message the probability of errors could be made very
small. One would expect, however, that to make this probability of errors approach zero, the redundancy
of the encoding must increase indeﬁnitely, and the rate of transmission therefore approach zero. This is by
no means true. If it were, there would not be a very well deﬁned capacity, but only a capacity for a given
frequency of errors, or a given equivocation; the capacity going down as the error requirements are made
more stringent. Actually the capacity C deﬁned above has a very deﬁnite signiﬁcance. It is possible to send
information at the rate C through the channel with as small a frequency of errors or equivocation as desired
by proper encoding. This statement is not true for any rate greater than C. If an attempt is made to transmit
at a higher rate than C, say C
R1, then there will necessarily be an equivocation equal to or greater than the
excess R1. Nature takes payment by requiring just that much uncertainty, so that we are not actually getting
any more than C through correctly.

+

The situation is indicated in Fig. 9. The rate of information into the channel is plotted horizontally and
the equivocation vertically. Any point above the heavy line in the shaded region can be attained and those
below cannot. The points on the line cannot in general be attained, but there will usually be two points on
the line that can.

These results are the main justiﬁcation for the deﬁnition of C and will now be proved.

Theorem 11: LetadiscretechannelhavethecapacityC andadiscretesourcetheentropypersecondH.
C thereexistsacodingsystemsuchthattheoutputofthesourcecanbetransmittedoverthechannel
C it is possible
isarbitrarilysmall. Thereisno

If H
with an arbitrarily small frequency of errors (or an arbitrarily small equivocation). If H
toencodethesourcesothattheequivocationislessthan H
methodofencodingwhichgivesanequivocationlessthanH

where

C.

C

+ (cid:15)

(cid:0)

>

(cid:20)

(cid:15)

The method of proving the ﬁrst part of this theorem is not by exhibiting a coding method having the
desired properties, but by showing that such a code must exist in a certain group of codes. In fact we will

(cid:0)

Hy (

x

)

ATTAINABLE
REGION

1.0

=

S L O P E

Fig. 9— The equivocation possible for a given input entropy to a channel.

C

H

x

(

)

22

average the frequency of errors over this group and show that this average can be made less than
average of a set of numbers is less than
there must exist at least one in the set which is less than
will establish the desired result.

(cid:15)

(cid:15)

. If the
. This

(cid:15)

The capacity C of a noisy channel has been deﬁned as

C

Max

H

x

=

(

)

Hy(

x

)

(cid:0)

where x is the input and y the output. The maximization is over all sources which might be used as input to
the channel.

(cid:0)

(cid:1)

Let S0 be a source which achieves the maximum capacity C. If this maximum is not actually achieved
by any source let S0 be a source which approximates to giving the maximum rate. Suppose S0 is used as
input to the channel. We consider the possible transmitted and received sequences of a long duration T . The
following will be true:

1. The transmitted sequences fall into two classes, a high probability group with about 2T H

x
) members

(

and the remaining sequences of small total probability.

2. Similarly the received sequences have a high probability set of about 2T H

y
) members and a low

(

probability set of remaining sequences.

3. Each high probability output could be produced by about 2T Hy (

x
) inputs. The probability of all other

cases has a small total probability.

All the

’s and

’s implied by the words “small” and “about” in these statements approach zero as we

(cid:15)

(cid:14)

allow T to increase and S0 to approach the maximizing source.

The situation is summarized in Fig. 10 where the input sequences are points on the left and output
sequences points on the right. The fan of cross lines represents the range of possible causes for a typical
output.

E

M

2H

x

T

(

)

HIGH PROBABILITY
MESSAGES

2H

y

T

(

)

HIGH PROBABILITY
RECEIVED SIGNALS

2Hy (

x

T

)

REASONABLE CAUSES
FOR EACH E

2Hx (

y

T

)

REASONABLE EFFECTS
FOR EACH M

Fig. 10— Schematic representation of the relations between inputs and outputs in a channel.

Now suppose we have another source producing information at rate R with R

C. In the period T this
source will have 2T R high probability messages. We wish to associate these with a selection of the possible
channel inputs in such a way as to get a small frequency of errors. We will set up this association in all

<

23

possible ways (using, however, only the high probability group of inputs as determined by the source S0)
and average the frequency of errors for this large class of possible coding systems. This is the same as
calculating the frequency of errors for a random association of the messages and channel inputs of duration
T . Suppose a particular output y1 is observed. What is the probability of more than one message in the set
of possible causes of y1? There are 2T R messages distributed at random in 2T H
x
) points. The probability of
a particular point being a message is thus

(

2T

R(cid:0)H

x

(

(

))

:

The probability that none of the points in the fan is a message (apart from the actual originating message) is

P

1

2T

R(cid:0)H

x

(

(

))

2T Hy (

x

)

=

:

Now R

H

x

<

(

)

Hy(

x

so R

H

x

)

(

) =

Hy (

x

(cid:2)

(cid:0)

with

positive. Consequently

(cid:3)

)

(cid:17)

(cid:17)

(cid:0)

(cid:0)

(cid:0)

(cid:0)

approaches (as T

)

!

P

=

1

2(cid:0)THy (

x

(cid:0)T (cid:17)

)

2T Hy (

x

)

(cid:0)

(cid:2)

(cid:3)

1

2(cid:0)T (cid:17)

:

Hence the probability of an error approaches zero and the ﬁrst part of the theorem is proved.

(cid:0)

The second part of the theorem is easily shown by noting that we could merely send C bits per second
from the source, completely neglecting the remainder of the information generated. At the receiver the
neglected part gives an equivocation H
. This limit can also
be attained in many other ways, as will be shown when we consider the continuous case.

C and the part transmitted need only add

x

(cid:0)

(cid:15)

(

)

The last statement of the theorem is a simple consequence of our deﬁnition of C. Suppose we can encode
positive. Then

a in such a way as to obtain an equivocation Hy (

with

C

a

x

+

(

) =

(cid:15)

(cid:15)

(cid:0)

a source with H
x
R

H

C

x
a and

) =

=

(

) =

+

H

x

(

)

Hy(

x

C

) =

+ (cid:15)

with

positive. This contradicts the deﬁnition of C as the maximum of H

x

(cid:0)

(cid:15)

(

)

Hy(

x

.

)

Actually more has been proved than was stated in the theorem. If the average of a set of numbers is
is

within
arbitrarily small we can say that almost all the systems are arbitrarily close to the ideal.

of of their maximum, a fraction of at most

below the maximum. Since

can be more than

p(cid:15)

p(cid:15)

(cid:0)

(cid:15)

(cid:15)

14. DISCUSSION

The demonstration of Theorem 11, while not a pure existence proof, has some of the deﬁciencies of such
proofs. An attempt to obtain a good approximation to ideal coding by following the method of the proof is
generally impractical. In fact, apart from some rather trivial cases and certain limiting situations, no explicit
description of a series of approximation to the ideal has been found. Probably this is no accident but is
related to the difﬁculty of giving an explicit construction for a good approximation to a random sequence.

An approximation to the ideal would have the property that if the signal is altered in a reasonable way
by the noise, the original can still be recovered. In other words the alteration will not in general bring it
closer to another reasonable signal than the original. This is accomplished at the cost of a certain amount of
redundancy in the coding. The redundancy must be introduced in the proper way to combat the particular
noise structure involved. However, any redundancy in the source will usually help if it is utilized at the
receiving point. In particular, if the source already has a certain redundancy and no attempt is made to
eliminate it in matching to the channel, this redundancy will help combat noise. For example, in a noiseless
telegraph channel one could save about 50% in time by proper encoding of the messages. This is not done
and most of the redundancy of English remains in the channel symbols. This has the advantage, however,
of allowing considerable noise in the channel. A sizable fraction of the letters can be received incorrectly
and still reconstructed by the context. In fact this is probably not a bad approximation to the ideal in many
cases, since the statistical structure of English is rather involved and the reasonable English sequences are
not too far (in the sense required for the theorem) from a random selection.

24

¥
As in the noiseless case a delay is generally required to approach the ideal encoding. It now has the
additional function of allowing a large sample of noise to affect the signal before any judgment is made
at the receiving point as to the original message. Increasing the sample size always sharpens the possible
statistical assertions.

The content of Theorem 11 and its proof can be formulated in a somewhat different way which exhibits
the connection with the noiseless case more clearly. Consider the possible signals of duration T and suppose
a subset of them is selected to be used. Let those in the subset all be used with equal probability, and suppose
the receiver is constructed to select, as the original signal, the most probable cause from the subset, when a
perturbed signal is received. We deﬁne N
to be the maximum number of signals we can choose for the
T
subset such that the probability of an incorrect interpretation is less than or equal to q.

q

)

(

;

Theorem 12: Lim
T !

T

q

;

)

logN
T

(

1.

C,whereC isthechannelcapacity,providedthat q doesnotequal0or

=

In other words, no matter how we set out limits of reliability, we can distinguish reliably in time T
enough messages to correspond to about CT bits, when T is sufﬁciently large. Theorem 12 can be compared
with the deﬁnition of the capacity of a noiseless channel given in Section 1.

15. EXAMPLE OF A DISCRETE CHANNEL AND ITS CAPACITY

A simple example of a discrete channel is indicated in Fig. 11. There are three possible symbols. The ﬁrst is
never affected by noise. The second and third each have probability p of coming through undisturbed, and
and P and Q be the
q of being changed into the other of the pair. We have (letting

p log p

q logq

(cid:11) =

[

+

]

(cid:0)

TRANSMITTED
SYMBOLS

q

q

p

p

RECEIVED
SYMBOLS

Fig. 11— Example of a discrete channel.

probabilities of using the ﬁrst and second symbols)

Plog P

2Q logQ

(

H
Hy (

x
x

) =

(cid:0)

2Q

) =

(cid:11):

(cid:0)

We wish to choose P and Q in such a way as to maximize H
Hence we consider

x

(

)

Hy (

x

, subject to the constraint P

2Q

1.

)

+

=

(cid:0)

Eliminating

(cid:21)

U

Plog P

2Q logQ

2Q

P

2Q

=

(cid:11) + (cid:21)(

+

)

(cid:0)

(cid:0)

(cid:0)

¶ U
¶ P =
¶ U
¶ Q =

1

logP

0

+ (cid:21) =

(cid:0)

(cid:0)

2

2 logQ

2

2

0

(cid:11) +

(cid:21) =

:

(cid:0)

(cid:0)

(cid:0)

logP
P

=

log Q
Qe(cid:11)

+ (cid:11)

Q

=

=

(cid:12)

25

¥
The channel capacity is then

P

=

(cid:12)

2

Q

=

1

2 :

(cid:12) +

(cid:12) +

C

log (cid:12) +

2

=

:

(cid:12)

=

1 and p

Note how this checks the obvious values in the cases p

log3,
2 and
log2. Here the second and third symbols cannot be distinguished at all and act together like one
1
2 and the second and third together with probability

which is correct since the channel is then noiseless with three possible symbols.
C
symbol. The ﬁrst symbol is used with probability P
1
2 . This may be distributed between them in any desired way and still achieve the maximum capacity.

1 and C
1
2 ,

For intermediate values of p the channel capacity will lie between log2 and log3. The distinction
between the second and third symbols conveys some information but not as much as in the noiseless case.
The ﬁrst symbol is used somewhat more frequently than the other two because of its freedom from noise.

If p

1
2 . In the ﬁrst,

(cid:12) =

(cid:12) =

=

=

=

=

=

16. THE CHANNEL CAPACITY IN CERTAIN SPECIAL CASES

If the noise affects successive channel symbols independently it can be described by a set of transition
probabilities pi j. This is the probability, if symbol i is sent, that j will be received. The maximum channel
rate is then given by the maximum of

Pi pi j log(cid:229)

Pi pi j +

Pi pi j log pi j

(cid:0)

i

j

i

i

j

;

;

where we vary the Pi subject to (cid:229) Pi =

1. This leads by the method of Lagrange to the equations,

ps j log

j

ps j
i Pi pi j = (cid:22)

s

1

2

=

;

; : : : :

Multiplying by Ps and summing on s shows that

C. Let the inverse of ps j (if it exists) be hst so that

(cid:22) =

s hst ps j = (cid:14)t j. Then:

Hence:

or,

hst ps j log ps j

log(cid:229)

Pi pit =

C(cid:229)

s

;

j

(cid:0)

i

hst :

s

Pi pit =

exp

i

C(cid:229)

(cid:0)

s

hst +

hst ps j log ps j

s

;

j

h

i

Pi =

hit exp

t

C(cid:229)

(cid:0)

s

hst +

hst ps j log ps j

:

s

;

j

h

i

This is the system of equations for determining the maximizing values of Pi, with C to be determined so
1. When this is done C will be the channel capacity, and the Pi the proper probabilities for the

that (cid:229) Pi =
channel symbols to achieve this capacity.

If each input symbol has the same set of probabilities on the lines emerging from it, and the same is true
of each output symbol, the capacity can be easily calculated. Examples are shown in Fig. 12. In such a case
(cid:229) pi log pi
Hx (
where the pi are the values of the transition probabilities from any input symbol. The channel capacity is

is independent of the distribution of probabilities on the input symbols, and is given by

y

(cid:0)

)

Max

H

y

(

)

Hx(

y

Max H

y

)

=

(

) +

pi log pi :

(cid:0)

The maximum of H
is clearly log m where m is the number of output symbols, since it is possible to make
them all equally probable by making the input symbols equally probable. The channel capacity is therefore

y

(cid:2)

(cid:3)

)

(

C

logm

=

+

pi log pi :

26

(cid:229)
(cid:229)
(cid:229)
(cid:229)
(cid:229)
(cid:229)
(cid:229)
(cid:229)
(cid:229)
(cid:229)
(cid:229)
(cid:229)
1/2

1/2

1/2

1/3

1/3

1/6

1/2

1/3

1/6

1/6

1/6

1/2

1/2

1/2

1/6

1/6

1/3

1/3

1/2

1/6

1/2

1/3

1/2

a

1/3

b

1/2

c

Fig. 12— Examples of discrete channels with the same transition probabilities for each input and for each output.

In Fig. 12a it would be

This could be achieved by using only the 1st and 3d symbols. In Fig. 12b

(cid:0)

C

log4

log2

log2

=

=

:

C

=

log 4

(cid:0)

log 4

=

2
3 log3
log3

1
3 log6

(cid:0)

1
3 log2

In Fig. 12c we have

=

(cid:0)

log 1
3 2

5
3

(cid:0)

:

C

=

log 3

(cid:0)

log

=

2

1
2 3

1
2 log2
3
1
3 6

1
6

:

1
3 log3

1
6 log6

(cid:0)

(cid:0)

Suppose the symbols fall into several groups such that the noise never causes a symbol in one group to
be mistaken for a symbol in another group. Let the capacity for the nth group be Cn (in bits per second)
when we use only the symbols in this group. Then it is easily shown that, for best use of the entire set, the
total probability Pn of all symbols in the nth group should be

Pn =

2Cn
(cid:229) 2Cn :

Within a group the probability is distributed just as it would be if these were the only symbols being used.
The channel capacity is

C

log(cid:229)

2Cn

=

:

17. AN EXAMPLE OF EFFICIENT CODING

The following example, although somewhat unrealistic, is a case in which exact matching to a noisy channel
is possible. There are two channel symbols, 0 and 1, and the noise affects them in blocks of seven symbols.
A block of seven is either transmitted without error, or exactly one symbol of the seven is incorrect. These
eight possibilities are equally likely. We have

C

=

=

=

Hx (

)

(

Max
H
y
1
8 log 1
8
7
8
4
7 bits/symbol

7

(cid:0)

+

(cid:2)

(cid:2)

:

(cid:3)

y

)

(cid:3)

An efﬁcient code, allowing complete correction of errors and transmitting at the rate C, is the following
(found by a method due to R. Hamming):

27

Let a block of seven symbols be X1 ;

X2 ; : : : ;
chosen arbitrarily by the source. The other three are redundant and calculated as follows:

X7. Of these X3, X5, X6 and X7 are message symbols and

X4
X2
X1

is chosen to make
“
“

“
“

“
“

“
“

X4 +
X2 +
X1 +

X5 +
X3 +
X3 +

X6 +
X6 +
X5 +

X7
X7
X7

(cid:11) =

(cid:12) =

(cid:13) =

even
“
“

When a block of seven is received
binary number

(cid:11) (cid:12) (cid:13)

and

are calculated and if even called zero, if odd called one. The

(cid:11); (cid:12)

(cid:13)

then gives the subscript of the Xi that is incorrect (if 0 there was no error).

THE GROWTH OF THE NUMBER OF BLOCKS OF SYMBOLS WITH A FINITE STATE CONDITION

Let Ni (

L

)

be the number of blocks of symbols of length L ending in state i. Then we have

APPENDIX 1

N j (

L

) =

Ni

L

i

s

;

(cid:0)

s
b(
i j

)

where b1
i j ;
are linear difference equations and the behavior as L

b2
i j ; : : : ;

bm
i j are the length of the symbols which may be chosen in state i and lead to state j. These

(cid:1)

(cid:0)

¥ must be of the type

Substituting in the difference equation

N j =

!

A jW L

:

or

A jW L

=

i

s

;

AiW L(cid:0)b(

s
i j

)

A j =

i

s

;

W (cid:0)b(

s
i j

)

AiW (cid:0)b(

s
i j

)

(cid:14)i j

Ai =

0

:

For this to be possible the determinant

i

s

(cid:0)

(cid:16)

(cid:17)

D

W

(

) =

ai j

=

j

j

s

W (cid:0)b(

s
i j

)

(cid:14)i j

(cid:0)

must vanish and this determines W , which is, of course, the largest real root of D

(cid:12)

(cid:12)

0.

(cid:12)

(cid:12)

The quantity C is then given by

(cid:12)

(cid:12)

=

C

=

Lim
L!

log (cid:229) A jW L
L

logW

=

and we also note that the same growth properties result if we require that all blocks start in the same (arbi-
trarily chosen) state.

APPENDIX 2

DERIVATION OF H

(cid:229) pi log pi

=

(cid:0)

1
n ;

1
n ; : : : ;

1
n

Let H
bilities into a series of m choices from s equally likely possibilities and obtain

A

. From condition (3) we can decompose a choice from sm equally likely possi-

n

=

)

(

(cid:16)

(cid:17)

A

sm

mA

s

(

) =

(

):

28

(cid:229)
(cid:229)
(cid:229)
(cid:229)
(cid:229)
(cid:229)
¥
Similarly

A

tn

nA

t

(

) =

(

):

We can choose n arbitrarily large and ﬁnd an m to satisfy

Thus, taking logarithms and dividing by n logs,

sm

tn

m

1

+

)

s(

<

:

(cid:20)

m
n

log t
log s

m
n +

1
n

or

m
n

log t
log s

(cid:20)

(cid:20)

(cid:0)

< (cid:15)

where

is arbitrarily small. Now from the monotonic property of A

(cid:12)

n

,

(cid:12)

(cid:15)

(

)

(cid:12)

(cid:12)

(cid:12)

(cid:12)

A

mA

(

sm
s

A

tn

A

)

(

)

(

(cid:20)

nA

t

(cid:20)

m

sm
1

1

+

)

A

s

(

)

(

)

(

+

)

(

):

(cid:20)

(cid:20)

Hence, dividing by nA

s

,

(

)

m
n

A
A

(

)

t
s

m
n +

1
n

or

m
n

A
A

(

)

t
s

< (cid:15)

(cid:20)

(cid:20)

(

)

(cid:0)

(

)

where K must be positive to satisfy (2).

(cid:12)

(cid:12)

(

)

(cid:0)

A
A

(

)

t
s

2

(cid:12)

(cid:12)

(cid:12)

A

(cid:12)

t

(cid:12)

K logt

(cid:12)

<

(cid:15)

(

) =

logt
logs

(cid:12)

(cid:12)

(cid:12)

Now suppose we have a choice from n possibilities with commeasurable probabilities pi =

where
the ni are integers. We can break down a choice from (cid:229) ni possibilities into a choice from n possibilities
with probabilities p1 ; : : : ;
pn and then, if the ith was chosen, a choice from ni with equal probabilities. Using
condition (3) again, we equate the total choice from (cid:229) ni as computed by two methods

(cid:12)

ni
(cid:229) ni

K log(cid:229)

ni =

H

(

p1 ; : : : ;

pn ) +

K (cid:229)

pi logni :

Hence

H

K

=

K (cid:229)

h

=

(cid:0)

pi log(cid:229)

pi log

ni
ni
(cid:229) ni =

(cid:0)

pi logni
K (cid:229)

pi log pi :

i

(cid:0)

If the pi are incommeasurable, they may be approximated by rationals and the same expression must hold
by our continuity assumption. Thus the expression holds in general. The choice of coefﬁcient K is a matter
of convenience and amounts to the choice of a unit of measure.

APPENDIX 3

THEOREMS ON ERGODIC SOURCES

If it is possible to go from any state with P
0, the system is
ergodic and the strong law of large numbers can be applied. Thus the number of times a given path pi j in
the network is traversed in a long sequence of length N is about proportional to the probability of being at
in
i, say Pi, and then choosing this path, Pi pi jN. If N is large enough the probability of percentage error
so that for all but a set of small probability the actual numbers lie within the limits
this is less than

0 to any other along a path of probability p

(cid:6)

>

>

(cid:14)

(cid:15)

Pi pi j

(

N

(cid:14))

:

(cid:6)

Hence nearly all sequences have a probability p given by

p

=

Pi pi j (cid:6)
p(
i j

(cid:14)

N

)

29

(cid:229)
(cid:229)
(cid:213)
and

log p
N

is limited by

or

This proves Theorem 3.

log p

N =

log p
N

(cid:0)

Pi pi j

(

log pi j

(cid:14))

(cid:6)

(cid:229) Pi pi j log pi j

< (cid:17) :

(cid:12)

(cid:12)

(cid:12)

(cid:12)

Theorem 4 follows immediately from this on calculating upper and lower bounds for n

(cid:12)

(cid:12)

q

based on the

(

)

possible range of values of p in Theorem 3.

In the mixed (not ergodic) case if

and the entropies of the components are H1
logn

q

Theorem: Lim
N!

(

q
N = ’(

)

)

isadecreasingstepfunction,

(cid:21) (cid:1) (cid:1) (cid:1) (cid:21)

(cid:21)

L

=

piLi

H2

Hn we have the

q

’(

) =

Hs

intheinterval

s(cid:0)1

1

(cid:11)i <

q

<

s

1

(cid:11)i :

To prove Theorems 5 and 6 ﬁrst note that FN is monotonic decreasing because increasing N adds a

subscript to a conditional entropy. A simple substitution for pBi (

S j )

in the deﬁnition of FN shows that

FN =

NGN

N

1

(

)

GN(cid:0)1

(cid:0)

(cid:0)

and summing this for all N gives GN =
must approach the same limit. By using Theorem 3 we see that Lim
N!

(cid:21)

(cid:229) Fn. Hence GN

1
N

GN =

H.

FN and GN monotonic decreasing. Also they

APPENDIX 4

MAXIMIZING THE RATE FOR A SYSTEM OF CONSTRAINTS

(

)

Suppose we have a set of constraints on sequences of symbols that is of the ﬁnite state type and can be
s
i j be the lengths of the various symbols that can occur in
represented therefore by a linear graph. Let
s
passing from state i to state j. What distribution of probabilities Pi for the different states and p(
for
i j
choosing symbol s in state i and going to state j maximizes the rate of generating information under these
constraints? The constraints deﬁne a discrete channel and the maximum rate must be less than or equal to
the capacity C of this channel, since if all blocks of large length were equally likely, this rate would result,
and if possible this would be best. We will show that this rate can be achieved by proper choice of the Pi and
s
i j .
p(

‘

)

)

The rate in question is

)

(cid:229) Pi p(
(cid:229) Pi p(

s
s
i j log p(
i j
s
i j

s
i j ‘

)

)

(

(cid:0)

)

=

N
M :

‘i j =

Let
j pi j =

s ‘
1, (cid:229) Pi (

(

)

s
i j . Evidently for a maximum p(

s
i j =
0. Hence we maximize

)

pi j

1, (cid:229)

k exp

(

s
i j . The constraints on maximization are (cid:229) Pi =

)

‘

(cid:14)i j ) =

(cid:0)

U

=

(cid:0)

¶ U
¶ pi j =

(cid:0)

(cid:229) Pi pi j log pi j
(cid:229) Pi pi j ‘i j
1
MPi (

+

log pi j ) +
M2

Pi +

(cid:22)i pi j +

(cid:17) jPi (

pi j

(cid:14)i j )

+ (cid:21)

i
NPi‘i j

(cid:0)

+ (cid:21) + (cid:22)i + (cid:17)iPi =

0

:

30

(cid:229)
(cid:229)
¥
(cid:229)
(cid:229)
¥
(cid:229)
(cid:229)
(cid:229)
(cid:229)
Solving for pi j

Since

pi j =

AiB jD(cid:0)

‘i j

:

pi j =

1

;

A(cid:0)1

i =

j

B jD(cid:0)

‘i j

j

pi j =

‘i j

B jD(cid:0)
s BsD(cid:0)

‘is :

The correct value of D is the capacity C and the B j are solutions of

for then

or

So that if

(cid:21)i satisfy

Bi =

(cid:229) B jC(cid:0)

‘i j

B j
Bi

C(cid:0)

‘i j

C(cid:0)

‘i j

Pj

=

pi j =

(cid:229) Pi

B j
Bi

Pi
Bi

C(cid:0)

‘i j

=

Pj
B j :

(cid:13)iC(cid:0)
Pi =

‘i j

= (cid:13) j

Bi(cid:13)i :

Both the sets of equations for Bi and

(cid:13)i can be satisﬁed since C is such that

C(cid:0)

‘i j

(cid:14)i j

0

=

:

j

(cid:0)

j

In this case the rate is

but

(cid:229) Pi pi j log B j
Bi
(cid:229) Pi pi j ‘i j

C(cid:0)

‘i j

(cid:229) Pi pi j log B j
Bi
(cid:229) Pi pi j ‘i j

C

=

(cid:0)

(cid:0)

(cid:229) Pi pi j (

log B j

logBi) =

Pj logB j

(cid:0)

j

(cid:0)

(cid:229) Pi logBi =

0

Hence the rate is C and as this could never be exceeded this is the maximum, justifying the assumed solution.

31

(cid:229)
(cid:229)
(cid:229)
(cid:229)
(cid:229)
(cid:229)
PART III: MATHEMATICAL PRELIMINARIES

In this ﬁnal installment of the paper we consider the case where the signals or the messages or both are
continuously variable, in contrast with the discrete nature assumed heretofore. To a considerable extent the
continuous case can be obtained through a limiting process from the discrete case by dividing the continuum
of messages and signals into a large but ﬁnite number of small regions and calculating the various parameters
involved on a discrete basis. As the size of the regions is decreased these parameters in general approach as
limits the proper values for the continuous case. There are, however, a few new effects that appear and also
a general change of emphasis in the direction of specialization of the general results to particular cases.

We will not attempt, in the continuous case, to obtain our results with the greatest generality, or with
the extreme rigor of pure mathematics, since this would involve a great deal of abstract measure theory
and would obscure the main thread of the analysis. A preliminary study, however, indicates that the theory
can be formulated in a completely axiomatic and rigorous manner which includes both the continuous and
discrete cases and many others. The occasional liberties taken with limiting processes in the present analysis
can be justiﬁed in all cases of practical interest.

18. SETS AND ENSEMBLES OF FUNCTIONS

We shall have to deal in the continuous case with sets of functions and ensembles of functions. A set of
functions, as the name implies, is merely a class or collection of functions, generally of one variable, time.
It can be speciﬁed by giving an explicit representation of the various functions in the set, or implicitly by
giving a property which functions in the set possess and others do not. Some examples are:

1. The set of functions:

Each particular value of

determines a particular function in the set.

(cid:18)

f

t

sin

t

(cid:18)

(

) =

(

+ (cid:18)):

2. The set of all functions of time containing no frequencies over W cycles per second.

3. The set of all functions limited in band to W and in amplitude to A.

4. The set of all English speech signals as functions of time.

An ensemble of functions is a set of functions together with a probability measure whereby we may

determine the probability of a function in the set having certain properties.1 For example with the set,

f

t

sin

t

(cid:18)

(

) =

(

+ (cid:18));

we may give a probability distribution for

, P

. The set then becomes an ensemble.

(cid:18)

((cid:18))

Some further examples of ensembles of functions are:

t
1. A ﬁnite set of functions fk (

(k

1

2

)

=

;

; : : : ;

n) with the probability of fk being pk.

2. A ﬁnite dimensional family of functions

f

((cid:11)1 ; (cid:11)2 ; : : : ; (cid:11)n;t

)

with a probability distribution on the parameters

(cid:11)i:

For example we could consider the ensemble deﬁned by

p

((cid:11)1 ; : : : ; (cid:11)n ):

f

a1 ; : : : ;

(

an ; (cid:18)1 ; : : : ; (cid:18)n;t

) =

ai sin i

(!

t

+ (cid:18)i)

n

i

1

=

with the amplitudes ai distributed normally and independently, and the phases
(from 0 to 2

) and independently.

(cid:25)

(cid:18)i distributed uniformly

1In mathematical terminology the functions belong to a measure space whose total measure is unity.

32

(cid:229)
3. The ensemble

f

ai ;

t

(

) =

+

an

n

(cid:0)

=

sin

2W t

n

(cid:25)(

)

2W t

(cid:0)

n

(cid:25)(

)

(cid:0)

with the ai normal and independent all with the same standard deviation pN. This is a representation
of “white” noise, band limited to the band from 0 to W cycles per second and with average power N.2

4. Let points be distributed on the t axis according to a Poisson distribution. At each selected point the

function f

t

(

)

is placed and the different functions added, giving the ensemble

f

t

(

+

tk )

k

(cid:0)

=

where the tk are the points of the Poisson distribution. This ensemble can be considered as a type of
impulse or shot noise where all the impulses are identical.

5. The set of English speech functions with the probability measure given by the frequency of occurrence

in ordinary use.

An ensemble of functions f

t

is stationary if the same ensemble results when all functions are shifted

any ﬁxed amount in time. The ensemble

(cid:11)

(

)

is stationary if

is distributed uniformly from 0 to 2

(cid:18)

(cid:25)

. If we shift each function by t1 we obtain

f

t

sin

t

(cid:18)

(

) =

(

+ (cid:18))

f

t

(cid:18)

(

+

t1) =

t1 + (cid:18))

+

sin
sin

(

t
t

=

(

+ ’)

distributed uniformly from 0 to 2

with
invariant under the translation. The other examples given above are also stationary.

. Each function has changed but the ensemble as a whole is

’

(cid:25)

An ensemble is ergodic if it is stationary, and there is no subset of the functions in the set with a

probability different from 0 and 1 which is stationary. The ensemble

sin

t

(

+ (cid:18))

is ergodic. No subset of these functions of probability
lations. On the other hand the ensemble

0

1 is transformed into itself under all time trans-

=

;

a sin

t

(

+ (cid:18))

with a distributed normally and
a between 0 and 1 for example is stationary.

(cid:18)

uniform is stationary but not ergodic. The subset of these functions with

Of the examples given, 3 and 4 are ergodic, and 5 may perhaps be considered so. If an ensemble is
ergodic we may say roughly that each function in the set is typical of the ensemble. More precisely it is
known that with an ergodic ensemble an average of any statistic over the ensemble is equal (with probability
1) to an average over the time translations of a particular function of the set.3 Roughly speaking, each
function can be expected, as time progresses, to go through, with the proper frequency, all the convolutions
of any of the functions in the set.

2This representation can be used as a deﬁnition of band limited white noise. It has certain advantages in that it involves fewer
limiting operations than do deﬁnitions that have been used in the past. The name “white noise,” already ﬁrmly entrenched in the
literature, is perhaps somewhat unfortunate. In optics white light means either any continuous spectrum as contrasted with a point
spectrum, or a spectrum which is ﬂat with wavelength (which is not the same as a spectrum ﬂat with frequency).

3This is the famous ergodic theorem or rather one aspect of this theorem which was proved in somewhat different formulations
by Birkoff, von Neumann, and Koopman, and subsequently generalized by Wiener, Hopf, Hurewicz and others. The literature on
ergodic theory is quite extensive and the reader is referred to the papers of these writers for precise and general formulations; e.g.,
E. Hopf, “Ergodentheorie,” Ergebnisse der Mathematik und ihrer Grenzgebiete, v. 5; “On Causality Statistics and Probability,” Journal
of Mathematics and Physics, v. XIII, No. 1, 1934; N. Wiener, “The Ergodic Theorem,” Duke Mathematical Journal, v. 5, 1939.

33

¥
(cid:229)
¥
¥
(cid:229)
¥
6
Just as we may perform various operations on numbers or functions to obtain new numbers or functions,
we can perform operations on ensembles to obtain new ensembles. Suppose, for example, we have an
ensemble of functions f
a resulting function
g

and an operator T which gives for each function f

t

:

t

t

(cid:11)

(cid:11)

)

(

)

(

(cid:11)

(

)

g

t

T f

t

(cid:11)

(cid:11)

(

) =

(

):

t

. The probability of a certain
Probability measure is deﬁned for the set g
subset of the g
functions which produce members of
the given subset of g functions under the operation T . Physically this corresponds to passing the ensemble
through some device, for example, a ﬁlter, a rectiﬁer or a modulator. The output functions of the device
form the ensemble g

functions is equal to that of the subset of the f

by means of that for the set f

t

t

t

t

.

(cid:11)

(cid:11)

(cid:11)

(cid:11)

)

(

)

)

(

(

)

(

A device or operator T will be called invariant if shifting the input merely shifts the output, i.e., if

(cid:11)

(

)

implies

g

t

T f

t

(cid:11)

(cid:11)

(

) =

(

)

g

t

(cid:11)

(

+

t1) =

T f

t

(cid:11)

(

+

t1)

(

(cid:11)

t

for all f
and all t1. It is easily shown (see Appendix 5 that if T is invariant and the input ensemble is
stationary then the output ensemble is stationary. Likewise if the input is ergodic the output will also be
ergodic.

)

A ﬁlter or a rectiﬁer is invariant under all time translations. The operation of modulation is not since the
carrier phase gives a certain time structure. However, modulation is invariant under all translations which
are multiples of the period of the carrier.

Wiener has pointed out the intimate relation between the invariance of physical devices under time
translations and Fourier theory.4 He has shown, in fact, that if a device is linear as well as invariant Fourier
analysis is then the appropriate mathematical tool for dealing with the problem.

An ensemble of functions is the appropriate mathematical representation of the messages produced by
a continuous source (for example, speech), of the signals produced by a transmitter, and of the perturbing
noise. Communication theory is properly concerned, as has been emphasized by Wiener, not with operations
on particular functions, but with operations on ensembles of functions. A communication system is designed
not for a particular speech function and still less for a sine wave, but for the ensemble of speech functions.

19. BAND LIMITED ENSEMBLES OF FUNCTIONS

If a function of time f
by giving its ordinates at a series of discrete points spaced 1
following result.5

is limited to the band from 0 to W cycles per second it is completely determined
2W seconds apart in the manner indicated by the

t

)

(

Theorem 13: Let f

t

containnofrequenciesoverW. Then

(

)

where

f

t

(

) =

Xn

sin

2Wt

n

(cid:25)(

)

2W t

(cid:0)

n

(cid:0)

(cid:25)(

)

(cid:0)

Xn =

f

n
2W

:

4Communication theory is heavily indebted to Wiener for much of its basic philosophy and theory. His classic NDRC report,
The Interpolation, Extrapolation and Smoothing of Stationary Time Series (Wiley, 1949), contains the ﬁrst clear-cut formulation of
communication theory as a statistical problem, the study of operations on time series. This work, although chieﬂy concerned with the
linear prediction and ﬁltering problem, is an important collateral reference in connection with the present paper. We may also refer
here to Wiener’s Cybernetics (Wiley, 1948), dealing with the general problems of communication and control.

(cid:16)

(cid:17)

5For a proof of this theorem and further discussion see the author’s paper “Communication in the Presence of Noise” published in

the Proceedings of the Institute of Radio Engineers, v. 37, No. 1, Jan., 1949, pp. 10–21.

34

¥
(cid:229)
¥
In this expansion f

is represented as a sum of orthogonal functions. The coefﬁcients Xn of the various
terms can be considered as coordinates in an inﬁnite dimensional “function space.” In this space each
function corresponds to precisely one point and each point to one function.

t

)

(

A function can be considered to be substantially limited to a time T if all the ordinates Xn outside this
interval of time are zero. In this case all but 2TW of the coordinates will be zero. Thus functions limited to
a band W and duration T correspond to points in a space of 2TW dimensions.

A subset of the functions of band W and duration T corresponds to a region in this space. For example,
the functions whose total energy is less than or equal to E correspond to points in a 2TW dimensional sphere
with radius r

p2W E.

=

(

xn )

An ensemble of functions of limited duration and band will be represented by a probability distribution
p
in the corresponding n dimensional space. If the ensemble is not limited in time we can consider
x1 ; : : : ;
the 2TW coordinates in a given interval T to represent substantially the part of the function in the interval T
and the probability distribution p
to give the statistical structure of the ensemble for intervals of
that duration.

x1 ; : : : ;

xn )

(

20. ENTROPY OF A CONTINUOUS DISTRIBUTION

The entropy of a discrete set of probabilities p1 ; : : : ;

pn has been deﬁned as:

H

=

pi log pi :

(cid:0)

In an analogous manner we deﬁne the entropy of a continuous distribution with the density distribution
function p

by:

x

(

)

H

p

x

log p

x

dx

=

(

)

(

)

:

Z

(cid:0)

(cid:0)

With an n dimensional distribution p

x1 ; : : : ;

xn )

(

we have

H

p

=

(

Z

Z

x1 ; : : : ;

xn )

log p

x1 ; : : : ;

xn )

dx1

(

dxn :

(cid:0)

(cid:1) (cid:1) (cid:1)

(cid:1) (cid:1) (cid:1)

If we have two arguments x and y (which may themselves be multidimensional) the joint and conditional
entropies of p

are given by

x

y

(

;

)

H

x

y

p

x

y

log p

x

y

dx dy

(

;

) =

(

;

)

(

;

)

ZZ

(cid:0)

and

where

y
Hx (

x
Hy (

p

x

y

log

) =

(

;

)

ZZ

(cid:0)

p

x

y

log

) =

(

;

)

ZZ

;

(

y
x
p
x
p
x
p
y
y
p

)

(

(

;

)

dx dy

)

dx dy

(cid:0)

(

)

p

x

p

x

y

dy

(

) =

(

;

)

Z

p

y

p

x

y

dx

(

) =

(

;

)

:

Z

The entropies of continuous distributions have most (but not all) of the properties of the discrete case.

In particular we have the following:

1. If x is limited to a certain volume v in its space, then H

x

is a maximum and equal to logv when p

x

(

)

(

)

is constant (1

v) in the volume.

=

35

(cid:229)
¥
¥
2. With any two variables x, y we have

H

x

y

H

x

H

y

(

;

)

(

) +

(

)

(cid:20)

with equality if (and only if) x and y are independent, i.e., p
set of points of probability zero).

x

y

p

x

p

y

(apart possibly from a

(

;

) =

(

)

(

)

3. Consider a generalized averaging operation of the following type:

p0

y

a

x

y

p

x

dx

(

) =

(

;

)

(

)

Z

with

a

x

y

dx

a

x

y

dy

1

a

x

y

0

(

;

)

=

(

;

)

=

;

(

;

)

:

Z

Z

(cid:21)

Then the entropy of the averaged distribution p0
distribution p

x

.

y

is equal to or greater than that of the original

(

)

(

)

4. We have

and

H

x

y

H

x

(

;

) =

(

) +

Hx (

y

H

y

) =

(

) +

Hy(

x

)

Hx (

y

H

y

)

(

):

(cid:20)

5. Let p

x

be a one-dimensional distribution. The form of p

x

giving a maximum entropy subject to the

(

)

(

)

condition that the standard deviation of x be ﬁxed at

is Gaussian. To show this we must maximize

(cid:27)

H

x

p

x

log p

x

dx

(

) =

(

)

(

)

Z

(cid:0)

with

as constraints. This requires, by the calculus of variations, maximizing

2

p

x

x2 dx

and 1

p

x

dx

(cid:27)

=

(

)

=

(

)

Z

Z

The condition for this is

p

x

log p

x

p

x

x2

p

x

dx

(

)

(

) + (cid:21)

(

)

+ (cid:22)

(

)

:

Z

(cid:0)

(cid:2)

(cid:3)

1

log p

x

x2

0

(

) + (cid:21)

+ (cid:22) =

and consequently (adjusting the constants to satisfy the constraints)

(cid:0)

(cid:0)

p

x

(

) =

1
p2

(cid:25)(cid:27)

x2

2

2(cid:27)

=

)

e(cid:0)

(

:

Similarly in n dimensions, suppose the second order moments of p

x1 ; : : : ;

xn )

are ﬁxed at Ai j:

(

Ai j =

xix j p

x1 ; : : : ;

xn )

dx1

(

dxn :

Z

Z

(cid:1) (cid:1) (cid:1)

(cid:1) (cid:1) (cid:1)

Then the maximum entropy occurs (by a similar calculation) when p
Gaussian distribution with the second order moments Ai j.

x1 ; : : : ;

xn )

(

is the n dimensional

36

6. The entropy of a one-dimensional Gaussian distribution whose standard deviation is

is given by

(cid:27)

This is calculated as follows:

H

x

log p2

e

(

) =

(cid:25)

(cid:27) :

p

x

(

) =

1
p2

(cid:25)(cid:27)

x2

2

2(cid:27)

(

=

)

e(cid:0)

log p

x

log p2

(

) =

(cid:25)(cid:27) +

(cid:0)

x2
2
2

(cid:27)

H

x

p

x

log p

x

dx

(

) =

(

)

(

)

Z

(cid:0)

p

x

log p2

dx

p

x

=

(

)

(cid:25)(cid:27)

+

(

)

Z

Z

x2
2

2 dx

(cid:27)

2

(cid:27)

2

2
log pe

(cid:27)

log p2

=

(cid:25)(cid:27) +

log p2

=

(cid:25)(cid:27) +

log p2

e

=

(cid:25)

(cid:27) :

Similarly the n dimensional Gaussian distribution with associated quadratic form ai j is given by

p

x1 ; : : : ;

xn ) =

(

1
2

n

j

2

=

ai j
2

j

exp

(

(cid:25))

(cid:0)

1

2 (cid:229)

ai jxix j

(cid:16)

(cid:17)

and the entropy can be calculated as

H

log

2

e

=

(

(cid:25)

)

n

2

=

ai j

1
2

(cid:0)

j

j

where

ai j

is the determinant whose elements are ai j.

j

j

7. If x is limited to a half line (p

x

0 for x

0) and the ﬁrst moment of x is ﬁxed at a:

(

) =

then the maximum entropy occurs when

and is equal to log ea.

(cid:20)

a

=

0

Z

p

x

x dx

(

)

;

p

x

(

) =

x

a

(

=

)

e(cid:0)

1
a

8. There is one important difference between the continuous and discrete entropies. In the discrete case
the entropy measures in an absolute way the randomness of the chance variable. In the continuous
case the measurement is relative to the coordinate system. If we change coordinates the entropy will
in general change. In fact if we change to coordinates y1

yn the new entropy is given by

H

y

p

(

) =

(

Z

Z

x1 ; : : : ;

xn )

J

x
y

(cid:1) (cid:1) (cid:1)

log p

x1 ; : : : ;

xn )

J

(

x
y

dy1

dyn

(cid:1) (cid:1) (cid:1)

(cid:1) (cid:1) (cid:1)

(cid:16)

(cid:17)

(cid:16)

(cid:17)

x
where J
y
ing the variables to x1

xn, we obtain:

is the Jacobian of the coordinate transformation. On expanding the logarithm and chang-

(cid:0)

(cid:1)

(cid:1) (cid:1) (cid:1)

H

y

H

x

p

(

) =

(

)

(

x1 ; : : : ;

xn )

logJ

Z

Z

(cid:0)

(cid:1) (cid:1) (cid:1)

dx1 : : :

dxn :

x
y

(cid:16)

(cid:17)

37

¥
Thus the new entropy is the old entropy less the expected logarithm of the Jacobian. In the continuous
case the entropy can be considered a measure of randomness relative to an assumed standard, namely
the coordinate system chosen with each small volume element dx1
dxn given equal weight. When
we change the coordinate system the entropy in the new system measures the randomness when equal
volume elements dy1
In spite of this dependence on the coordinate system the entropy concept is as important in the con-
tinuous case as the discrete case. This is due to the fact that the derived concepts of information rate
and channel capacity depend on the difference of two entropies and this difference does not depend
on the coordinate frame, each of the two terms being changed by the same amount.

dyn in the new system are given equal weight.

(cid:1) (cid:1) (cid:1)

(cid:1) (cid:1) (cid:1)

The entropy of a continuous distribution can be negative. The scale of measurements sets an arbitrary
zero corresponding to a uniform distribution over a unit volume. A distribution which is more conﬁned
than this has less entropy and will be negative. The rates and capacities will, however, always be non-
negative.

9. A particular case of changing coordinates is the linear transformation

y j =

ai jxi :

i

In this case the Jacobian is simply the determinant

ai j

(cid:0)1 and

j

j

H

y

H

x

(

) =

(

) +

log

ai j

:

j

j

In the case of a rotation of coordinates (or any measure preserving transformation) J
H

x

.

1 and H

y

=

(

) =

(

)

21. ENTROPY OF AN ENSEMBLE OF FUNCTIONS

Consider an ergodic ensemble of functions limited to a certain band of width W cycles per second. Let

p

x1 ; : : : ;

xn )

(

be the density distribution function for amplitudes x1 ; : : : ;
entropy of the ensemble per degree of freedom by

xn at n successive sample points. We deﬁne the

H 0

=

Lim
n!

1
n Z

Z

(cid:0)

(cid:1) (cid:1) (cid:1)

p

x1 ; : : : ;

xn )

log p

(

x1 ; : : : ;

xn )

dx1 : : :

dxn :

(

We may also deﬁne an entropy H per second by dividing, not by n, but by the time T in seconds for n
samples. Since n

2TW , H

2W H 0.

With white thermal noise p is Gaussian and we have

=

=

H 0
H

=

log p2
W log2

(cid:25)

;

eN
eN

=

(cid:25)

:

For a given average power N, white noise has the maximum possible entropy. This follows from the

maximizing properties of the Gaussian distribution noted above.

The entropy for a continuous stochastic process has many properties analogous to that for discrete pro-
cesses. In the discrete case the entropy was related to the logarithm of the probability of long sequences,
and to the number of reasonably probable sequences of long length. In the continuous case it is related in
a similar fashion to the logarithm of the probability density for a long series of samples, and the volume of
reasonably high probability in the function space.

More precisely, if we assume p

x1 ; : : : ;

(

xn )

continuous in all the xi for all n, then for sufﬁciently large n

log p
n

(cid:0)

H 0

< (cid:15)

(cid:12)

(cid:12)

(cid:12)

(cid:12)

38

(cid:12)

(cid:12)

(cid:229)
¥
for all choices of
small. This follows form the ergodic property if we divide the space into a large number of small cells.

apart from a set whose total probability is less than

x1 ; : : : ;

, with

and

xn )

(cid:14)

(cid:14)

(cid:15)

(

arbitrarily

The relation of H to volume can be stated as follows: Under the same assumptions consider the n
be the smallest volume in this space which
. Let Vn (

xn )

q

)

dimensional space corresponding to p
includes in its interior a total probability q. Then

x1 ; : : : ;

(

Lim
n!

q

)

logVn(
n

H 0

=

provided q does not equal 0 or 1.

These results show that for large n there is a rather well-deﬁned volume (at least in the logarithmic sense)
of high probability, and that within this volume the probability density is relatively uniform (again in the
logarithmic sense).

In the white noise case the distribution function is given by

p

x1 ; : : : ;

xn ) =

(

1
N

2

exp

n

2

=

1
2N

(

(cid:25)

)

(cid:0)

x2
i :

Since this depends only on (cid:229) x2
bution has spherical symmetry. The region of high probability is a sphere of radius pnN. As n
probability of being outside a sphere of radius
n
eN.
volume of the sphere approaches log p2

i the surfaces of equal probability density are spheres and the entire distri-
the
n times the logarithm of the

approaches zero and 1

N

+ (cid:15))

!

(

(cid:25)

In the continuous case it is convenient to work not with the entropy H of an ensemble but with a derived
quantity which we will call the entropy power. This is deﬁned as the power in a white noise limited to the
same band as the original ensemble and having the same entropy. In other words if H 0 is the entropy of an
ensemble its entropy power is

p

e
In the geometrical picture this amounts to measuring the high probability volume by the squared radius of a
sphere having the same volume. Since white noise has the maximum entropy for a given power, the entropy
power of any noise is less than or equal to its actual power.

2

(cid:25)

:

1

N1 =

exp2H 0

22. ENTROPY LOSS IN LINEAR FILTERS

Theorem 14: IfanensemblehavinganentropyH1 perdegreeoffreedominbandW ispassedthrougha

ﬁlterwithcharacteristicY

f

theoutputensemblehasanentropy

(

)

H2 =

H1 +

1
W ZW

log

Y

f

2 d f

(

)

:

j

j

The operation of the ﬁlter is essentially a linear transformation of coordinates. If we think of the different
frequency components as the original coordinate system, the new frequency components are merely the old
ones multiplied by factors. The coordinate transformation matrix is thus essentially diagonalized in terms
of these coordinates. The Jacobian of the transformation is (for n sine and n cosine components)

n

Y

J

=

(

i

1 j

=

2

fi )

j

where the fi are equally spaced through the band W . This becomes in the limit

exp

1
W ZW

log

Y

f

2 d f

(

)

:

j

j

Since J is constant its average value is the same quantity and applying the theorem on the change of entropy
with a change of coordinates, the result follows. We may also phrase it in terms of the entropy power. Thus
if the entropy power of the ﬁrst ensemble is N1 that of the second is

N1 exp

1
W ZW

log

Y

f

2 d f

(

)

:

j

j

39

¥
(cid:229)
¥
(cid:213)
TABLE I

GAIN

ENTROPY

ENTROPY

POWER POWER GAIN
FACTOR IN DECIBELS

IMPULSE RESPONSE

1

!

(cid:0)

1

2

!

(cid:0)

1

3

!

(cid:0)

p1

2

!

(cid:0)

1

1

1

1

1

1
e2

8

69

:

2

)

sin2
t2

t
2

(

=

(cid:0)

=

0

1

!

4

2
e

(cid:16)

(cid:17)

5

33

:

2

sint
t3

cost
t2

(cid:0)

(cid:0)

(cid:20)

(cid:21)

0

411

3

87

6

:

:

1

cost
t4

(cid:0)

cost
2t2 +

sint
t3

(cid:0)

(cid:0)

(cid:20)

(cid:21)

2

2
e

2

67

:

(cid:16)

(cid:17)

(cid:0)

J1 (
t
t

)

(cid:25)

2

1
e2(cid:11)

8

69

(cid:11)

:

1
t2

(cid:11)

cos

1

t

(cid:11)

(

)

cost

(cid:0)

(cid:0)

(cid:0)

(cid:2)

(cid:3)

0

1

!

0

1

!

0

1

!

(cid:11)

0

1

!

The ﬁnal entropy power is the initial entropy power multiplied by the geometric mean gain of the ﬁlter. If
the gain is measured in db, then the output entropy power will be increased by the arithmetic mean db gain
over W .

In Table I the entropy power loss has been calculated (and also expressed in db) for a number of ideal
, with phase assumed

gain characteristics. The impulsive responses of these ﬁlters are also given for W
to be 0.

2

=

(cid:25)

e2 for the ﬁrst case also applies to any gain characteristic obtain from 1

The entropy loss for many other cases can be obtained from these results. For example the entropy
by a measure
power factor 1
, or a “saw tooth”
preserving transformation of the
characteristic between 0 and 1 have the same entropy loss. The reciprocal gain has the reciprocal factor.
Thus 1

has the factor e2. Raising the gain to any power raises the factor to this power.

axis. In particular a linearly increasing gain G

(!) = !

(cid:0)

!

!

=

=!

23. ENTROPY OF A SUM OF TWO ENSEMBLES

If we have two ensembles of functions f
the ﬁrst ensemble has the probability density function p

and g

we can form a new ensemble by “addition.” Suppose
. Then the

and the second q

t

t

(cid:11)

(cid:12)

)

(

)

(

x1 ; : : : ;

xn )

x1 ; : : : ;

xn )

(

(

40

density function for the sum is given by the convolution:

r

x1 ; : : : ;

xn) =

(

p

y1 ; : : : ;

yn )

q

(

x1

(

y1 ; : : : ;

xn

yn)

dy1

dyn :

Z

Z

(cid:1) (cid:1) (cid:1)

(cid:0)

(cid:0)

(cid:1) (cid:1) (cid:1)

Physically this corresponds to adding the noises or signals represented by the original ensembles of func-
tions.

The following result is derived in Appendix 6.
Theorem 15: Lettheaveragepoweroftwo ensemblesbe N1 and N2 andlettheirentropypowersbeN1

and N2. Thentheentropypowerofthesum, N3,isboundedby

N1 +

N2

N3

N1 +

N2 :

(cid:20)

(cid:20)

White Gaussian noise has the peculiar property that it can absorb any other noise or signal ensemble
which may be added to it with a resultant entropy power approximately equal to the sum of the white noise
power and the signal power (measured from the average signal value, which is normally zero), provided the
signal power is small, in a certain sense, compared to noise.

Consider the function space associated with these ensembles having n dimensions. The white noise
corresponds to the spherical Gaussian distribution in this space. The signal ensemble corresponds to another
probability distribution, not necessarily Gaussian or spherical. Let the second moments of this distribution
xn )
about its center of gravity be ai j. That is, if p

is the density distribution function

x1 ; : : : ;

(

ai j =

p

xi

(

(cid:11)i)(

x j

(cid:11) j )

dx1

dxn

Z

Z

(cid:1) (cid:1) (cid:1)

(cid:0)

(cid:0)

(cid:1) (cid:1) (cid:1)

where the
(cid:11)i are the coordinates of the center of gravity. Now ai j is a positive deﬁnite quadratic form, and
we can rotate our coordinate system to align it with the principal directions of this form. ai j is then reduced
to diagonal form bii. We require that each bii be small compared to N, the squared radius of the spherical
distribution.

In this case the convolution of the noise and signal produce approximately a Gaussian distribution whose

corresponding quadratic form is

The entropy power of this distribution is

or approximately

N

bii :

+

1

n

=

N

(

+

bii)

h

i

n

N

=

(

)

+

bii (

N

)

n(cid:0)1

1

n

=

h

:

N

=

+

1
n

bii :

i

The last term is the signal power, while the ﬁrst is the noise power.

PART IV: THE CONTINUOUS CHANNEL

24. THE CAPACITY OF A CONTINUOUS CHANNEL

In a continuous channel the input or transmitted signals will be continuous functions of time f
belonging
to a certain set, and the output or received signals will be perturbed versions of these. We will consider
only the case where both transmitted and received signals are limited to a certain band W . They can then
be speciﬁed, for a time T , by 2TW numbers, and their statistical structure by ﬁnite dimensional distribution
functions. Thus the statistics of the transmitted signal will be determined by

t

(

)

P

x1 ; : : : ;

xn ) =

P

(

x

(

)

41

(cid:213)
(cid:229)
(cid:229)
and those of the noise by the conditional probability distribution

Px1 ;:::;

xn (

y1 ; : : : ;

yn) =

Px (

y

):

The rate of transmission of information for a continuous channel is deﬁned in a way analogous to that

for a discrete channel, namely

R

H

x

=

(

)

Hy(

x

)

(

x

is the entropy of the input and Hy (

the equivocation. The channel capacity C is deﬁned as the
where H
maximum of R when we vary the input over all possible ensembles. This means that in a ﬁnite dimensional
approximation we must vary P

and maximize

P

x

x

(cid:0)

)

)

x1 ; : : : ;

xn )

(

) =

(

P

x

log P

x

dx

P

x

y

log

(

)

(

)

+

(

;

)

Z

ZZ

(

x
P
y
y
P

;

)

dx dy

:

This can be written

(cid:0)

(

)

P

x

y

(

;

)

log

ZZ

P
x
P

(

;

x
y
P

)

y

(

)

(

)

dx dy

using the fact that

P

x

y

log P

x

dx dy

P

x

log P

x

dx. The channel capacity is thus expressed as

(

;

)

(

)

=

(

)

(

)

follows:

ZZ

Z

C

=

Lim
T !

Max
x
P

(

)

1
T ZZ

P

x

y

(

;

)

log

P
x
P

(

;

x
y
P

)

y

(

)

(

)

dx dy

:

It is obvious in this form that R and C are independent of the coordinate system since the numerator

and denominator in log

P
x
P

(

;

x
y
P

)

y

(

)

(

)

will be multiplied by the same factors when x and y are transformed in

. Properly interpreted
any one-to-one way. This integral expression for C is more general than H
(see Appendix 7) it will always exist while H
in some
Hy (
cases. This occurs, for example, if x is limited to a surface of fewer dimensions than n in its n dimensional
approximation.

x
may assume an indeterminate form ¥

Hy(

x

x

x

(cid:0)

(cid:0)

(cid:0)

(

)

)

(

)

)

)

)

(

x

x

and Hy (

If the logarithmic base used in computing H

is two then C is the maximum number of
binary digits that can be sent per second over the channel with arbitrarily small equivocation, just as in
the discrete case. This can be seen physically by dividing the space of signals into a large number of
small cells, sufﬁciently small so that the probability density Px (
of signal x being perturbed to point y is
substantially constant over a cell (either of x or y). If the cells are considered as distinct points the situation is
essentially the same as a discrete channel and the proofs used there will apply. But it is clear physically that
this quantizing of the volume into individual points cannot in any practical situation alter the ﬁnal answer
signiﬁcantly, provided the regions are sufﬁciently small. Thus the capacity will be the limit of the capacities
for the discrete subdivisions and this is just the continuous capacity deﬁned above.

y

)

On the mathematical side it can be shown ﬁrst (see Appendix 7) that if u is the message, x is the signal,

y is the received signal (perturbed by noise) and v is the recovered message then

H

x

(

)

Hy(

x

H

u

)

(

)

Hv(

u

)

(cid:0)

(cid:21)

(cid:0)

regardless of what operations are performed on u to obtain x or on y to obtain v. Thus no matter how we
encode the binary digits to obtain the signal, or how we decode the received signal to recover the message,
the discrete rate for the binary digits does not exceed the channel capacity we have deﬁned. On the other
hand, it is possible under very general conditions to ﬁnd a coding system for transmitting binary digits at the
rate C with as small an equivocation or frequency of errors as desired. This is true, for example, if, when we
take a ﬁnite dimensional approximating space for the signal functions, P
is continuous in both x and y
except at a set of points of probability zero.

x

y

(

)

;

An important special case occurs when the noise is added to the signal and is independent of it (in the

probability sense). Then Px (

y

is a function only of the difference n

y

x

,

)

= (

)

Px (

y

Q

y

x

) =

(

)

(cid:0)

(cid:0)

42

¥
¥
and we can assign a deﬁnite entropy to the noise (independent of the statistics of the signal), namely the
entropy of the distribution Q

. This entropy will be denoted by H

n

n

.

Theorem 16: Ifthesignalandnoiseareindependentandthereceivedsignalisthesumofthetransmitted

(

)

(

)

signalandthenoisethentherateoftransmissionis

i.e.,theentropyofthereceivedsignallesstheentropyofthenoise. Thechannelcapacityis

R

H

y

H

n

=

(

)

(

);

(cid:0)

We have, since y

x

n:

=

+

C

=

Max
x
P

(

)

H

y

H

n

(

)

(

):

(cid:0)

H

x

y

H

x

n

(

;

) =

(

;

):

Expanding the left side and using the fact that x and n are independent

Hence

H

y

(

) +

Hy(

x

H

x

H

n

) =

(

) +

(

):

R

H

x

=

(

)

Hy(

x

H

y

H

n

) =

(

)

(

):

n

Since H

is independent of P

, the entropy of the received
signal. If there are certain constraints on the ensemble of transmitted signals, the entropy of the received
signal must be maximized subject to these constraints.

, maximizing R requires maximizing H

y

x

(cid:0)

(cid:0)

)

)

(

(

(

)

25. CHANNEL CAPACITY WITH AN AVERAGE POWER LIMITATION

A simple application of Theorem 16 is the case when the noise is a white thermal noise and the transmitted
signals are limited to a certain average power P. Then the received signals have an average power P
N
where N is the average noise power. The maximum entropy for the received signals occurs when they also
form a white noise ensemble since this is the greatest possible entropy for a power P
N and can be obtained
by a suitable choice of transmitted signals, namely if they form a white noise ensemble of power P. The
entropy (per second) of the received ensemble is then

+

+

and the noise entropy is

The channel capacity is

H

y

W log 2

e

P

N

(

) =

(cid:25)

(

+

);

H

n

W log2

eN

(

) =

(cid:25)

:

C

H

y

H

n

W log

=

(

)

(

) =

(cid:0)

P

+

N
N :

Summarizing we have the following:
Theorem 17: ThecapacityofachannelofbandW perturbedbywhitethermalnoisepowerN whenthe

averagetransmitterpowerislimitedto P isgivenby

C

=

W log

P

+

N
N :

This means that by sufﬁciently involved encoding systems we can transmit binary digits at the rate

P

N

+

W log2
higher rate by any encoding system without a deﬁnite positive frequency of errors.

bits per second, with arbitrarily small frequency of errors. It is not possible to transmit at a

N

To approximate this limiting rate of transmission the transmitted signals must approximate, in statistical
properties, a white noise.6 A system which approaches the ideal rate may be described as follows: Let

6This and other properties of the white noise case are discussed from the geometrical point of view in “Communication in the

Presence of Noise,” loc. cit.

43

=

(cid:0)

2s samples of white noise be constructed each of duration T . These are assigned binary numbers from
M
0 to M
1. At the transmitter the message sequences are broken up into groups of s and for each group
the corresponding noise sample is transmitted as the signal. At the receiver the M samples are known and
the actual received signal (perturbed by noise) is compared with each of them. The sample which has the
least R.M.S. discrepancy from the received signal is chosen as the transmitted signal and the corresponding
binary number reconstructed. This process amounts to choosing the most probable (a posteriori) signal.
The number M of noise samples used will depend on the tolerable frequency
of errors, but for almost all
selections of samples we have

(cid:15)

Lim
!0

(cid:15)

Lim
T !

T

)

logM
T

((cid:15);

W log

=

P

+

N
N ;

is chosen, we can, by taking T sufﬁciently large, transmit as near as we wish

(cid:15)

so that no matter how small

to TW log

binary digits in the time T .

P

N

+

N

P

N

Formulas similar to C

for the white noise case have been developed independently
by several other writers, although with somewhat different interpretations. We may mention the work of
N. Wiener,7 W. G. Tuller,8 and H. Sullivan in this connection.

W log

N

=

+

In the case of an arbitrary perturbing noise (not necessarily white thermal noise) it does not appear that
the maximizing problem involved in determining the channel capacity C can be solved explicitly. However,
upper and lower bounds can be set for C in terms of the average noise power N the noise entropy power N1.
These bounds are sufﬁciently close together in most practical cases to furnish a satisfactory solution to the
problem.

Theorem 18: The capacity of a channel of band W perturbed by an arbitrary noise is bounded by the

inequalities

where

W log

P

+

N1
N1 (cid:20)

C

W log

(cid:20)

P

N

+

N1

P

averagetransmitterpower

=

=

N
N1 =

averagenoisepower
entropypowerofthenoise.

Here again the average power of the perturbed signals will be P

N. The maximum entropy for this
power would occur if the received signal were white noise and would be W log 2
. It may not
be possible to achieve this; i.e., there may not be any ensemble of transmitted signals which, added to the
.
perturbing noise, produce a white thermal noise at the receiver, but at least this sets an upper bound to H
We have, therefore

N

P

e

y

+

+

(cid:25)

(

)

)

(

C

Max H

y

H

n

=

(

)

(

)

W log 2

e

(cid:0)

P

N

W log 2

(cid:25)

(

+

)

(cid:25)

eN1 :

(cid:20)

(cid:0)

This is the upper limit given in the theorem. The lower limit can be obtained by considering the rate if we
make the transmitted signal a white noise, of power P. In this case the entropy power of the received signal
N1 since we have shown in in a previous
must be at least as great as that of a white noise of power P
theorem that the entropy power of the sum of two ensembles is greater than or equal to the sum of the
individual entropy powers. Hence

+

Max H

y

W log2

e

P

(

)

(cid:25)

(

+

N1)

7Cybernetics, loc. cit.
8“Theoretical Limitations on the Rate of Transmission of Information,” Proceedings of the Institute of Radio Engineers, v. 37,

(cid:21)

No. 5, May, 1949, pp. 468–78.

44

¥
and

C

(cid:21)

=

N1)

W log2

eN1

(cid:25)

(cid:0)

W log2
P

W log

(cid:25)

(

+

e

P
N1

+

N1

:

As P increases, the upper and lower bounds approach each other, so we have as an asymptotic rate

W log

P

N

+

N1

:

If the noise is itself white, N

N1 and the result reduces to the formula proved previously:

=

C

W log

1

=

+

P
N

:

If the noise is Gaussian but with a spectrum which is not necessarily ﬂat, N1 is the geometric mean of

(cid:16)

(cid:17)

the noise power over the various frequencies in the band W . Thus

N1 =

exp

1
W ZW

log N

f

d f

(

)

where N

f

(

)

is the noise power at frequency f .

Theorem 19: IfwesetthecapacityforagiventransmitterpowerP equalto

C

=

W log

P

+

N
N1

(cid:17)

(cid:0)

then

(cid:17)

ismonotonicdecreasingas P increasesandapproaches0asalimit.

Suppose that for a given power P1 the channel capacity is

W log

P1 +

N
N1

(cid:17)1

(cid:0)

:

This means that the best signal distribution, say p
received distribution r
adding a white noise of power

whose entropy power is

y

)

(

(

(

x
P1 +

)

, when added to the noise distribution q

x

(

)

N

(cid:17)1)

. Let us increase the power to P1 + (cid:1)

, gives a
P by

P to the signal. The entropy of the received signal is now at least

(cid:0)

(cid:1)

H

y

W log2

e

(

) =

(cid:25)

(

P1 +

N

(cid:17)1 + (cid:1)

P

)

(cid:0)

by application of the theorem on the minimum entropy power of a sum. Hence, since we can attain the
must be monotonic
H indicated, the entropy of the maximizing distribution must be at least as great and
decreasing. To show that
consider a signal which is white noise with a large P. Whatever
the perturbing noise, the received signal will be approximately a white noise, if P is sufﬁciently large, in the
N.
sense of having an entropy power approaching P

0 as P

!

!

(cid:17)

(cid:17)

26. THE CHANNEL CAPACITY WITH A PEAK POWER LIMITATION

+

In some applications the transmitter is limited not by the average power output but by the peak instantaneous
power. The problem of calculating the channel capacity is then that of maximizing (by variation of the
ensemble of transmitted symbols)

H

y

H

n

(

)

(

)

subject to the constraint that all the functions f
in the ensemble be less than or equal to pS, say, for all
t. A constraint of this type does not work out as well mathematically as the average power limitation. The

t

(cid:0)

)

(

S
N

, an “asymptotic” upper bound (valid

most we have obtained for this case is a lower bound valid for all

for large

S
N

) and an asymptotic value of C for

S
N

small.

45

¥
Theorem 20: The channel capacity C for a band W perturbed by white thermal noise of power N is

boundedby

C

W log

2
e3

S
N ;

(cid:21)

(cid:25)

where S isthepeakallowedtransmitterpower. Forsufﬁcientlylarge

S
N

C

W log

(cid:20)

N

2
(cid:25)e S
N

+

1

(

+ (cid:15))

where

(cid:15)

isarbitrarilysmall. As

S
N

!

0 (andprovidedthebandW startsat 0)

C

W log

1

+

S
N

!

.

(cid:18)

(cid:19)

We wish to maximize the entropy of the received signal. If

we maximize the entropy of the transmitted ensemble.

1

:

S
N

is large this will occur very nearly when

The asymptotic upper bound is obtained by relaxing the conditions on the ensemble. Let us suppose that
the power is limited to S not at every instant of time, but only at the sample points. The maximum entropy of
the transmitted ensemble under these weakened conditions is certainly greater than or equal to that under the
original conditions. This altered problem can be solved easily. The maximum entropy occurs if the different
samples are independent and have a distribution function which is constant from
pS. The entropy
can be calculated as

pS to

+

(cid:0)

The received signal will then have an entropy less than

W log4S

:

W log

4S

2

eN

1

(

+

(cid:25)

)(

+ (cid:15))

with
W log 2

(cid:15)

0 as
eN:

!

S
N

!

and the channel capacity is obtained by subtracting the entropy of the white noise,

(cid:25)

W log

4S

2

eN

1

W log

2

eN

W log

(

+

(cid:25)

)(

+ (cid:15))

(

(cid:25)

) =

N

2
(cid:25)e S
N

+

1

(

+ (cid:15)):

This is the desired upper bound to the channel capacity.

(cid:0)

To obtain a lower bound consider the same ensemble of functions. Let these functions be passed through
an ideal ﬁlter with a triangular transfer characteristic. The gain is to be unity at frequency 0 and decline
linearly down to gain 0 at frequency W . We ﬁrst show that the output functions of the ﬁlter have a peak

W t

sin 2
2

(cid:25)

(cid:25)

Wt

going into

power limitation S at all times (not just the sample points). First we note that a pulse
the ﬁlter produces

1
2

sin2

W t
2

(cid:25)

W t

((cid:25)

)

in the output. This function is never negative. The input function (in the general case) can be thought of as
the sum of a series of shifted functions

Wt

a

sin 2
2

(cid:25)

Wt

where a, the amplitude of the sample, is not greater than pS. Hence the output is the sum of shifted functions
of the non-negative form above with the same coefﬁcients. These functions being non-negative, the greatest
positive value for any t is obtained when all the coefﬁcients a have their maximum positive values, i.e., pS.
In this case the input function was a constant of amplitude pS and since the ﬁlter has unit gain for D.C., the
output is the same. Hence the output ensemble has a peak power S.

(cid:25)

46

¥
The entropy of the output ensemble can be calculated from that of the input ensemble by using the
theorem dealing with such a situation. The output entropy is equal to the input entropy plus the geometrical
mean gain of the ﬁlter:

Hence the output entropy is

0

Z

W

logG2 d f

=

0

Z

W

log

W

f

2

(cid:0)

W

d f

2W

=

:

(cid:0)

and the channel capacity is greater than

(cid:16)

(cid:17)

W log4S

2W

W log

=

(cid:0)

4S
e2

W log

2
e3

S
N :

(cid:25)

We now wish to show that, for small

capacity is approximately

S
N

(peak signal power over average white noise power), the channel

C

W log

1

=

+

S
N

:

(cid:18)

(cid:19)

1 as

S
N

!

0. Since the average signal power P is less than or equal

More precisely C

W log

1

+

(cid:18)

S
N

to the peak S, it follows that for all

.

!

(cid:19)

S
N

C

W log

1

+

P
N

W log

1

+

S
N

:

(cid:20)

(cid:20)

(cid:18)

(cid:19)

(cid:18)

(cid:19)

Therefore, if we can ﬁnd an ensemble of functions such that they correspond to a rate nearly W log

1

S
N

+

and are limited to band W and peak S the result will be proved. Consider the ensemble of functions of the
following type. A series of t samples have the same value, either
pS, then the next t samples have
the same value, etc. The value for a series is chosen at random, probability 1
pS. If
this ensemble be passed through a ﬁlter with triangular gain characteristic (unit gain at D.C.), the output is
peak limited to
S. Furthermore the average power is nearly S and can be made to approach this by taking t
sufﬁciently large. The entropy of the sum of this and the thermal noise can be found by applying the theorem
on the sum of a noise and a small signal. This theorem will apply if

pS and 1

2 for

2 for

pS or

(cid:0)

+

(cid:0)

(cid:6)

+

(cid:19)

(cid:18)

pt

S
N

is sufﬁciently small. This can be ensured by taking
will be S
to

small enough (after t is chosen). The entropy power
N to as close an approximation as desired, and hence the rate of transmission as near as we wish

+

S
N

W log

S

N

+

N

:

PART V: THE RATE FOR A CONTINUOUS SOURCE

(cid:18)

(cid:19)

27. FIDELITY EVALUATION FUNCTIONS

In the case of a discrete source of information we were able to determine a deﬁnite rate of generating
information, namely the entropy of the underlying stochastic process. With a continuous source the situation
is considerably more involved. In the ﬁrst place a continuously variable quantity can assume an inﬁnite
number of values and requires, therefore, an inﬁnite number of binary digits for exact speciﬁcation. This
means that to transmit the output of a continuous source with exact recovery at the receiving point requires,

47

in general, a channel of inﬁnite capacity (in bits per second). Since, ordinarily, channels have a certain
amount of noise, and therefore a ﬁnite capacity, exact transmission is impossible.

This, however, evades the real issue. Practically, we are not interested in exact transmission when we
have a continuous source, but only in transmission to within a certain tolerance. The question is, can we
assign a deﬁnite rate to a continuous source when we require only a certain ﬁdelity of recovery, measured in
a suitable way. Of course, as the ﬁdelity requirements are increased the rate will increase. It will be shown
that we can, in very general cases, deﬁne such a rate, having the property that it is possible, by properly
encoding the information, to transmit it over a channel whose capacity is equal to the rate in question, and
satisfy the ﬁdelity requirements. A channel of smaller capacity is insufﬁcient.

)

y

It is ﬁrst necessary to give a general mathematical formulation of the idea of ﬁdelity of transmission.
Consider the set of messages of a long duration, say T seconds. The source is described by giving the
. A given
probability density, in the associated space, that the source will select the message in question P
communication system is described (from the external point of view) by giving the conditional probability
that if message x is produced by the source the recovered message at the receiving point will be y. The
Px (
system as a whole (including source and transmission system) is described by the probability function P
y
of having message x and ﬁnal output y. If this function is known, the complete characteristics of the system
from the point of view of ﬁdelity are known. Any evaluation of ﬁdelity must correspond mathematically
to an operation applied to P
. This operation must at least have the properties of a simple ordering of
systems; i.e., it must be possible to say of two systems represented by P1(
that, according to
our ﬁdelity criterion, either (1) the ﬁrst has higher ﬁdelity, (2) the second has higher ﬁdelity, or (3) they have
equal ﬁdelity. This means that a criterion of ﬁdelity can be represented by a numerically valued function:

and P2(

x

x

x

x

y

x

y

y

)

)

(

)

(

(

)

)

;

;

;

;

whose argument ranges over possible probability functions P

x

y

.

(cid:0)

(cid:1)

(

;

)

We will now show that under very general and reasonable assumptions the function v

v

P

x

y

(

;

)

written in a seemingly much more specialized form, namely as an average of a function
of possible values of x and y:

v

P

x

y

P

x

y

x

y

dx dy

(

;

)

=

(

;

)(cid:26)(

;

)

:

ZZ

P
y

(

x

x

;

can be
y
over the set

)

(cid:26)(

;

)

(cid:0)

(cid:1)

(cid:1)

(cid:0)

To obtain this we need only assume (1) that the source and system are ergodic so that a very long sample
will be, with probability nearly 1, typical of the ensemble, and (2) that the evaluation is “reasonable” in the
sense that it is possible, by observing a typical input and output x1 and y1, to form a tentative evaluation
on the basis of these samples; and if these samples are increased in duration the tentative evaluation will,
. Let the tentative
with probability 1, approach the exact evaluation based on a full knowledge of P
evaluation be
which
y
x
x
are in the high probability region corresponding to the system:

) a constant for almost all

. Then the function

approaches (as T

y

y

x

y

x

!

(cid:26)(

(cid:26)(

)

)

(

)

(

)

;

;

;

;

and we may also write

since

This establishes the desired result.

x

y

v

P

x

y

(cid:26)(

;

)

(

;

)

!

x

y

P

x

y

x

y

dx dy

(cid:26)(

;

)

(

;

)(cid:26)(

;

)

(cid:0)

(cid:1)

ZZ

!

P

x

y

dx dy

1

(

;

)

=

:

ZZ

;

)

(cid:26)(

y

x

The function

has the general nature of a “distance” between x and y.9 It measures how undesirable
it is (according to our ﬁdelity criterion) to receive y when x is transmitted. The general result given above
can be restated as follows: Any reasonable evaluation can be represented as an average of a distance function
over the set of messages and recovered messages x and y weighted according to the probability P
of
getting the pair in question, provided the duration T of the messages be taken sufﬁciently large.

x

y

(

)

;

The following are simple examples of evaluation functions:

9It is not a “metric” in the strict sense, however, since in general it does not satisfy either

x

y

(cid:26)

y

x

or

(cid:26)

x

y

(cid:26)

y

z

(cid:26)

x

z

.

(cid:26)

(

;

) =

(

;

)

(

;

) +

(

;

)

(

;

)

(cid:21)

48

¥
1. R.M.S. criterion.

v

x

t

y

t

2

=

(

)

(

)

:

is (apart from a constant
In this very commonly used measure of ﬁdelity the distance function
factor) the square of the ordinary Euclidean distance between the points x and y in the associated
function space.

x

y

(cid:26)(

(cid:0)

(cid:1)

(cid:0)

)

;

x

y

(cid:26)(

;

) =

1
T Z
0

T

x

t

y

t

2 dt

(

)

(

)

:

(cid:0)

2. Frequency weighted R.M.S. criterion. More generally one can apply different weights to the different
frequency components before using an R.M.S. measure of ﬁdelity. This is equivalent to passing the
difference x
through a shaping ﬁlter and then determining the average power in the output.
Thus let

y

t

t

(cid:0)

(cid:3)

(cid:2)

(

)

)

(

and

then

3. Absolute error criterion.

e

t

x

t

y

t

(

) =

(

)

(

)

(cid:0)

f

t

e

k

t

d

(

) =

((cid:28) )

(

(cid:28) )

(cid:28)

Z

(cid:0)

(cid:0)

x

y

(cid:26)(

;

) =

T

1
T Z
0

f

t

2 dt

(

)

:

x

y

(cid:26)(

;

) =

T

1
T Z
0

x

t

y

t

dt

(

)

(

)

:

(cid:0)

(cid:12)

4. The structure of the ear and brain determine implicitly an evaluation, or rather a number of evaluations,
appropriate in the case of speech or music transmission. There is, for example, an “intelligibility”
is equal to the relative frequency of incorrectly interpreted words when
criterion in which
message x
in these
cases it could, in principle, be determined by sufﬁcient experimentation. Some of its properties follow
from well-known experimental results in hearing, e.g., the ear is relatively insensitive to phase and the
sensitivity to amplitude and frequency is roughly logarithmic.

. Although we cannot give an explicit representation of

x
is received as y

y

x

y

t

t

(cid:26)(

(cid:26)(

(

)

(

)

)

)

(cid:12)

(cid:12)

(cid:12)

;

;

5. The discrete case can be considered as a specialization in which we have tacitly assumed an evaluation
is then deﬁned as the number of symbols in the
x
based on the frequency of errors. The function
sequence y differing from the corresponding symbols in x divided by the total number of symbols in
x.

y

(cid:26)(

)

;

28. THE RATE FOR A SOURCE RELATIVE TO A FIDELITY EVALUATION

We are now in a position to deﬁne a rate of generating information for a continuous source. We are given
P
which will be assumed
continuous in both x and y. With a particular system P

for the source and an evaluation v determined by a distance function

the quality is measured by

x

y

x

x

y

(cid:26)(

(

)

)

;

(

;

)

v

x

y

P

x

y

dx dy

=

(cid:26)(

;

)

(

;

)

:

ZZ

Furthermore the rate of ﬂow of binary digits corresponding to P

x

y

is

(

;

)

R

P

x

y

log

=

(

;

)

ZZ

P
x
P

(

;

y
x
P

)

y

(

)

(

)

dx dy

:

We deﬁne the rate R1 of generating information for a given quality v1 of reproduction to be the minimum of
R when we keep v ﬁxed at v1 and vary Px (

. That is:

y

)

(

P
x

P

;

x
y
P

)

y

dx dy

(

)

(

)

R1 =

Min
y
Px (

)

ZZ

P

x

y

(

;

)

log

49

¥
¥
subject to the constraint:

v1 =

P

x

y

x

y

dx dy

(

;

)(cid:26)(

;

)

:

ZZ

This means that we consider, in effect, all the communication systems that might be used and that
transmit with the required ﬁdelity. The rate of transmission in bits per second is calculated for each one
and we choose that having the least rate. This latter rate is the rate we assign the source for the ﬁdelity in
question.

The justiﬁcation of this deﬁnition lies in the following result:
Theorem 21: IfasourcehasarateR1 foravaluation v1 itispossibletoencodetheoutputofthesource
C. Thisis not

andtransmititoverachannelofcapacityC withﬁdelityasnear v1 asdesiredprovided R1
possibleif R1 >

C.

(cid:20)

The last statement in the theorem follows immediately from the deﬁnition of R1 and previous results. If
it were not true we could transmit more than C bits per second over a channel of capacity C. The ﬁrst part
of the theorem is proved by a method analogous to that used for Theorem 11. We may, in the ﬁrst place,
divide the
space into a large number of small cells and represent the situation as a discrete case. This
will not change the evaluation function by more than an arbitrarily small amount (when the cells are very
is the particular system which
y
x
small) because of the continuity assumed for
minimizes the rate and gives R1. We choose from the high probability y’s a set at random containing

. Suppose that P1(

y

x

x

y

(cid:26)(

(

)

)

)

;

;

;

R1+

T

)

(cid:15)

2(

(cid:15)

!

!

0 as T

members where
. With large T each chosen point will be connected by a high probability
line (as in Fig. 10) to a set of x’s. A calculation similar to that used in proving Theorem 11 shows that with
large T almost all x’s are covered by the fans from the chosen y points for almost all choices of the y’s. The
communication system to be used operates as follows: The selected points are assigned binary numbers.
When a message x is originated it will (with probability approaching 1 as T
) lie within at least one
of the fans. The corresponding binary number is transmitted (or one of them chosen arbitrarily if there are
several) over the channel by suitable coding means to give a small probability of error. Since R1
C this is
possible. At the receiving point the corresponding y is reconstructed and used as the recovered message.

!

(cid:20)

The evaluation v0

1 for this system can be made arbitrarily close to v1 by taking T sufﬁciently large.
the evaluation
t

and recovered message y

t

(

)

(

)

This is due to the fact that for each long sample of message x
approaches v1 (with probability 1).

It is interesting to note that, in this system, the noise in the recovered message is actually produced by a
kind of general quantizing at the transmitter and not produced by the noise in the channel. It is more or less
analogous to the quantizing noise in PCM.

The deﬁnition of the rate is similar in many respects to the deﬁnition of channel capacity. In the former

29. THE CALCULATION OF RATES

R

=

Min
y
Px (

)

ZZ

P

x

y

(

;

)

log

P
x
P

(

;

x
y
P

)

y

(

)

(

)

dx dy

with P

x

(

)

and v1 =

P

x

y

x

y

dx dy ﬁxed. In the latter

(

;

)(cid:26)(

;

)

ZZ

C

=

Max
x
P

(

)

ZZ

P

x

y

(

;

)

log

P
x
P

(

;

x
y
P

)

y

(

)

(

)

dx dy

with Px (
y
P
K

)

ﬁxed and possibly one or more other constraints (e.g., an average power limitation) of the form
y
x

dx dy.

x

y

=

(

;

)(cid:21)(

;

)

A partial solution of the general maximizing problem for determining the rate of a source can be given.

RR

Using Lagrange’s method we consider

P

x

y

(

;

)

log

ZZ

(

P
x

P

;

x
y
P

)

y

P

x

y

x

y

x

P

x

y

dx dy

+ (cid:22)

(

;

)(cid:26)(

;

) + (cid:23) (

)

(

;

)

:

(cid:20)

(cid:21)

(

)

(

)

50

¥
¥
The variational equation (when we take the ﬁrst variation on P

x

y

) leads to

(

;

)

Py (

x

B

x

e(cid:0)

x

y

(cid:21)(cid:26)

(

;

)

) =

(

)

where

is determined to give the required ﬁdelity and B

x

is chosen to satisfy

(cid:21)

(

)

B

x

e(cid:0)

x

(cid:21)(cid:26)

(

;

y
) dx

1

(

)

=

:

Z

This shows that, with best encoding, the conditional probability of a certain cause for various received

y, Py (

x

will decline exponentially with the distance function

x

y

between the x and y in question.

)

(cid:26)(

;

)

In the special case where the distance function

x

y

depends only on the (vector) difference between x

(cid:26)(

;

)

and y,

we have

Hence B

x

is constant, say

, and

(

)

(cid:11)

x

y

x

y

(cid:26)(

;

) = (cid:26)(

)

(cid:0)

B

x

e(cid:0)

(cid:21)(cid:26)

(

x(cid:0)y

) dx

1

(

)

=

:

Z

Py (

x

x(cid:0)y

(cid:21)(cid:26)

(

)

e(cid:0)

) = (cid:11)

:

Unfortunately these formal solutions are difﬁcult to evaluate in particular cases and seem to be of little value.
In fact, the actual calculation of rates has been carried out in only a few very simple cases.

If the distance function

y
is white noise, the rate can be determined. In that case we have

x

(cid:26)(

)

;

is the mean square discrepancy between x and y and the message ensemble

R

Min

H

x

=

(

)

Hy(

x

H

x

)

=

(

)

MaxHy (

x

)

(cid:0)

(cid:0)

with N
W1 is the bandwidth of the message ensemble. Therefore

2. But the Max Hy (

occurs when y

x

x

y

= (

(cid:0)

(cid:0)

(cid:2)

(cid:3)

)

)

x is a white noise, and is equal to W1 log2

eN where

(cid:25)

eQ

W1 log 2

(cid:25)

eN

(cid:0)

R

=

=

(cid:25)

W1 log2
Q
N

W1 log

where Q is the average message power. This proves the following:

Theorem 22: Theratefor a whitenoise sourceof power Q and bandW1 relativeto an R.M.S. measure

ofﬁdelityis

R

W1 log

=

Q
N

where N istheallowedmeansquareerrorbetweenoriginalandrecoveredmessages.

More generally with any message source we can obtain inequalities bounding the rate relative to a mean

square error criterion.

Theorem 23: TherateforanysourceofbandW1 isboundedby

where Q istheaveragepowerofthesource,Q1 itsentropypowerandN theallowedmeansquareerror.

W1 log

Q1
N

R

W1 log

(cid:20)

(cid:20)

Q
N

The lower bound follows from the fact that the Max Hy (

N occurs in the white
noise case. The upper bound results if we place points (used in the proof of Theorem 21) not in the best way
but at random in a sphere of radius

for a given

N.

Q

x

y

x

(cid:0)

=

)

)

(

p

2

(cid:0)

51

ACKNOWLEDGMENTS

The writer is indebted to his colleagues at the Laboratories, particularly to Dr. H. W. Bode, Dr. J. R. Pierce,
Dr. B. McMillan, and Dr. B. M. Oliver for many helpful suggestions and criticisms during the course of this
work. Credit should also be given to Professor N. Wiener, whose elegant solution of the problems of ﬁltering
and prediction of stationary ensembles has considerably inﬂuenced the writer’s thinking in this ﬁeld.

APPENDIX 5

Let S1 be any measurable subset of the g ensemble, and S2 the subset of the f ensemble which gives S1
under the operation T . Then

Let H (cid:21) be the operator which shifts all functions in a set by the time

. Then

(cid:21)

S1 =

T S2 :

since T is invariant and therefore commutes with H (cid:21). Hence if m

S

is the probability measure of the set S

[

]

H (cid:21)S1 =

H (cid:21)T S2 =

T H (cid:21)S2

m

[

H (cid:21)S1 ] =

m

[

m

=

[

T H (cid:21)S2 ] =
m
S1 ]
S2 ] =

m

[

[

H (cid:21)S2 ]

where the second equality is by deﬁnition of measure in the g space, the third since the f ensemble is
stationary, and the last by deﬁnition of g measure again.

To prove that the ergodic property is preserved under invariant operations, let S1 be a subset of the g
ensemble which is invariant under H (cid:21), and let S2 be the set of all functions f which transform into S1. Then

so that H (cid:21)S2 is included in S2 for all

. Now, since

(cid:21)

H (cid:21)S1 =

H (cid:21)T S2 =

T H (cid:21)S2 =

S1

this implies

m

[

H (cid:21)S2 ] =

m

[

S1 ]

H (cid:21)S2 =

S2

for all

with m

(cid:21)

[

S2 ]

0

=

;

1. This contradiction shows that S1 does not exist.

APPENDIX 6

N1 +

N2, is due to the fact that the maximum possible entropy for a power N1 +

The upper bound, N3
occurs when we have a white noise of this power. In this case the entropy power is N1 +
To obtain the lower bound, suppose we have two distributions in n dimensions p

with
entropy powers N1 and N2. What form should p and q have to minimize the entropy power N3 of their
convolution r

N2.
xi )

and q

xi )

N2

(cid:20)

(

(

:
xi )

(

The entropy H3 of r is given by

r

xi ) =

(

p

yi )

q

(

xi

(

yi )

dyi :

Z

(cid:0)

H3 =

r

xi )

log r

(

xi )

dxi :

(

Z

(cid:0)

We wish to minimize this subject to the constraints

H1 =

p

xi )

log p

(

xi )

dxi

(

Z

(cid:0)

H2 =

q

xi )

log q

xi )

dxi :

(

(

Z

(cid:0)

52

6
We consider then

U

U

r

x

log r

x

p

x

log p

x

q

x

logq

x

dx

=

(

)

(

) + (cid:21)

(

)

(

) + (cid:22)

(

)

(

)

Z

(cid:0)

(cid:2)

1

logr

x

r

x

1

log p

x

p

x

(cid:3)

1

logq

x

q

x

dx

(cid:14)

=

[

+

(

)](cid:14)

(

) + (cid:21)[

+

(

)](cid:14)

(

) + (cid:22)[

+

(

)](cid:14)

(

)

:

Z

(cid:0)

If p

x

(

)

is varied at a particular argument xi =

(cid:2)

si, the variation in r

x

is

(

)

(cid:3)

r

x

q

(cid:14)

(

) =

(

xi

si )

(cid:0)

and

and similarly when q is varied. Hence the conditions for a minimum are

U

q

(cid:14)

=

(

xi

si )

logr

xi )

dxi

(

log p

(cid:21)

(

si ) =

0

Z

(cid:0)

(cid:0)

(cid:0)

q

xi

(

si )

logr

xi )

dxi =

(

log p

(cid:21)

(

si )

Z

Z

(cid:0)

(cid:0)

p

xi

(

si )

logr

xi )

dxi =

(

logq

(cid:22)

(

si ):

(cid:0)

(cid:0)

If we multiply the ﬁrst by p

si )

(

and the second by q

si )

and integrate with respect to si we obtain

(

H3 =
H3 =

H1
H2

(cid:21)

(cid:0)

(cid:22)

or solving for

and

and replacing in the equations

(cid:21)

(cid:22)

(cid:0)

H1

q

xi

(

si)

log r

xi )

dxi =

(

H3 log p

si )

(

Z

(cid:0)

(cid:0)

H2

p

xi

(

si)

log r

xi )

dxi =

(

H3 logq

si ):

(

Z

(cid:0)

(cid:0)

Now suppose p

xi )

and q

xi )

(

(

are normal

p

xi ) =

(

Ai j
2

j

n

2

=

j

n

2

=

exp

1

2 (cid:229) Ai jxix j

q

xi ) =

(

(

(cid:25))

(cid:0)

Bi j
2

j

n

2

=

j

n

2

=

(

(cid:25))

exp

(cid:0)

1

2 (cid:229) Bi jxix j :

Then r

xi )

(

will also be normal with quadratic form Ci j. If the inverses of these forms are ai j, bi j, ci j then

ci j =

ai j +

bi j :

We wish to show that these functions satisfy the minimizing conditions if and only if ai j =
give the minimum H3 under the constraints. First we have

Kbi j and thus

logr

xi ) =

(

log

n
2
n
2

1
2

Ci j

log

(cid:25)

1
2

j

j (cid:0)

Ci j

1

2 (cid:229) Ci jxix j
2 (cid:229) Ci jsis j

1

1

2 (cid:229) Ci jbi j :

q

xi

(

si )

logr

xi )

(

Z

dxi =

(cid:0)

j

j (cid:0)

(cid:0)

(cid:25)

This should equal

which requires Ai j =

H1
H3

H3
H1

n
2

(cid:20)

log

1
2

Ai j

(cid:25)

j

j (cid:0)

1

2 (cid:229) Ai jsis j

Ci j. In this case Ai j =

Bi j and both equations reduce to identities.

(cid:21)

H1
H2

53

APPENDIX 7

The following will indicate a more general and more rigorous approach to the central deﬁnitions of commu-
. The variables
nication theory. Consider a probability measure space whose elements are ordered pairs
x, y are to be identiﬁed as the possible transmitted and received signals of some long duration T . Let us call
the set of all points whose x belongs to a subset S1 of x points the strip over S1, and similarly the set whose
y belong to S2 the strip over S2. We divide x and y into a collection of non-overlapping measurable subsets
Xi and Yi approximate to the rate of transmission R by

y

x

)

(

;

where

P

(

Xi )
Yi )
Yi )

(

P
Xi ;

P

(

R1 =

1
T

i

P

Xi ;

Yi )

log

(

(

P
Yi )
Xi ;
Yi )
P
Xi )

(

(

P

is the probability measure of the strip over Xi
is the probability measure of the strip over Yi
is the probability measure of the intersection of the strips

:

A further subdivision can never decrease R1. For let X1 be divided into X1 =

X 0

1 +

1 and let
X 00

(

(

P
P

(

Y1 ) =
X 0

1 ) =

P

(

X 00

1 ) =

a
b

c

P

P

(

(

P
X1 ) =
X 0
Y1 ) =
1 ;
X 00
Y1 ) =
1 ;
e

+

:

c

+

b
d

e

P

X1 ;

Y1 ) =

(

d

Then in the sum we have replaced (for the X1, Y1 intersection)

d

e

log

(

+

)

+

d
b

e
c

a

(

+

)

by d log

d
ab +

e log

e
ac :

It is easily shown that with the limitation we have on b, c, d, e,

d

e

+

d
b

+

e
c

ddee
bdce

+

(cid:20)

(cid:20)

(cid:21)

and consequently the sum is increased. Thus the various possible subdivisions form a directed set, with
R monotonic increasing with reﬁnement of the subdivision. We may deﬁne R unambiguously as the least
upper bound for R1 and write it

R

=

1
T ZZ

P

x

y

(

;

)

log

P
x
P

(

;

x
y
P

)

y

(

)

(

)

dx dy

:

This integral, understood in the above sense, includes both the continuous and discrete cases and of course
many others which cannot be represented in either form. It is trivial in this formulation that if x and u are
in one-to-one correspondence, the rate from u to y is equal to that from x to y. If v is any function of y (not
necessarily with an inverse) then the rate from x to y is greater than or equal to that from x to v since, in
the calculation of the approximations, the subdivisions of y are essentially a ﬁner subdivision of those for
v. More generally if y and v are related not functionally but statistically, i.e., we have a probability measure
space
. This means that any operation applied to the received signal, even though
it involves statistical elements, does not increase R.

, then R

R

v

v

y

x

x

y

(cid:20)

)

(

)

)

(

(

;

;

;

Another notion which should be deﬁned precisely in an abstract formulation of the theory is that of
“dimension rate,” that is the average number of dimensions required per second to specify a member of
an ensemble. In the band limited case 2W numbers per second are sufﬁcient. A general deﬁnition can be
be a metric measuring
framed as follows. Let f

be an ensemble of functions and let

t

t

f

t

f

(cid:26)T [

(cid:11)

(cid:12)

(

);

(

)]

(cid:11)

(

)

54

(cid:229)
)

(cid:11)

((cid:15); (cid:14) ;

T

the “distance” from f
N
apart from a set of measure
the space to within
by the triple limit

(cid:15)

(cid:12)

to f

over the time T (for example the R.M.S. discrepancy over this interval.) Let
be the least number of elements f which can be chosen such that all elements of the ensemble
of at least one of those chosen. Thus we are covering
for the ensemble

apart from a set of small measure

. We deﬁne the dimension rate

are within the distance

(cid:14)

(cid:15)

(cid:14)

(cid:21)

(cid:21) =

Lim
!0

(cid:14)

Lim
!0

(cid:15)

Lim
T !

logN

T

((cid:15); (cid:14) ;

)

T log

(cid:15)

:

This is a generalization of the measure type deﬁnitions of dimension in topology, and agrees with the intu-
itive dimension rate for simple ensembles where the desired result is obvious.

55

¥
