import xml.etree.ElementTree as ET
from collections import namedtuple, Counter
from itertools import ifilter
from datetime import datetime 
import re


# detect number of distinct conversations by comparing timestamps between
# messsages.  If the difference is greater than say 15 minutes, consider it
# a new conversation.

# punchcard for time of messages ala Githubs commit punchcard graph


SMSMsg = namedtuple("SMSMsg", ['phone_number', 'type', 'message', 'date', 'timestamp', 'message_length', 'tokens'])
Metrics = namedtuple("Metrics", ['total_messages', 'average_length', 'longest', 'shortest', 'histogram', 'word_counts' ]) # vocabulary #normalized_vocab #avg_word_length #message_length_histogram

# message types
RECEIVED = 1
SENT = 2
UNKNOWN = 3

# Stop words to omit from word counts, mostly taken from:
# http://www.ranks.nl/stopwords
STOP_WORDS = set(""":p :) :( ;) 
i a a's    able    about    above    according
accordingly    across    actually    after    afterwards
again    against    ain't    all    allow
allows    almost    alone    along    already
also    although    always    am    among
amongst    an    and    another    any
anybody    anyhow    anyone    anything    anyway
anyways    anywhere    apart    appear    appreciate
appropriate    are    aren't    around    as
aside    ask    asking    associated    at
available    away    awfully    be    became
because    become    becomes    becoming    been
before    beforehand    behind    being    believe
below    beside    besides    best    better
between    beyond    both    brief    but
by    c'mon    c's    came    can
can't    cannot    cant    cause    causes
certain    certainly    changes    clearly    co
com    come    comes    concerning    consequently
consider    considering    contain    containing    contains
corresponding    could    couldn't    course    currently
definitely    described    despite    did    didn't
different    do    does    doesn't    doing
don't    done    down    downwards    during
each    edu    eg    eight    either
else    elsewhere    enough    entirely    especially
et    etc    even    ever    every
everybody    everyone    everything    everywhere    ex
exactly    example    except    far    few
fifth    first    five    followed    following
follows    for    former    formerly    forth
four    from    further    furthermore    get
gets    getting    given    gives    go
goes    going    gone    got    gotten
greetings    had    hadn't    happens    hardly
has    hasn't    have    haven't    having
he    he's    hello    help    hence
her    here    here's    hereafter    hereby
herein    hereupon    hers    herself    hi
him    himself    his    hither    hopefully
how    howbeit    however    i'd    i'll
i'm    i've    ie    if    ignored
immediate    in    inasmuch    inc    indeed
indicate    indicated    indicates    inner    insofar
instead    into    inward    is    isn't
it    it'd    it'll    it's    its
itself    just    keep    keeps    kept
know    known    knows    last    lately
later    latter    latterly    least    less
lest    let    let's    like    liked
likely    little    look    looking    looks
ltd    mainly    many    may    maybe
me    mean    meanwhile    merely    might
more    moreover    most    mostly    much
must    my    myself    name    namely
nd    near    nearly    necessary    need
needs    neither    never    nevertheless    new
next    nine    no    nobody    non
none    noone    nor    normally    not
nothing    novel    now    nowhere    obviously
of    off    often    oh    ok
okay    old    on    once    one
ones    only    onto    or    other
others    otherwise    ought    our    ours
ourselves    out    outside    over    overall
own    particular    particularly    per    perhaps
placed    please    plus    possible    presumably
probably    provides    que    quite    qv
rather    rd    re    really    reasonably
regarding    regardless    regards    relatively    respectively
right    said    same    saw    say
saying    says    second    secondly    see
seeing    seem    seemed    seeming    seems
seen    self    selves    sensible    sent
serious    seriously    seven    several    shall
she    should    shouldn't    since    six
so    some    somebody    somehow    someone
something    sometime    sometimes    somewhat    somewhere
soon    sorry    specified    specify    specifying
still    sub    such    sup    sure
t's    take    taken    tell    tends
th    than    thank    thanks    thanx
that    that's    thats    the    their
theirs    them    themselves    then    thence
there    there's    thereafter    thereby    therefore
therein    theres    thereupon    these    they
they'd    they'll    they're    they've    think
third    this    thorough    thoroughly    those
though    three    through    throughout    thru
thus    to    together    too    took
toward    towards    tried    tries    truly
try    trying    twice    two    un
under    unfortunately    unless    unlikely    until
unto    up    upon    us    use
used    useful    uses    using    usually
value    various    very    via    viz
vs    want    wants    was    wasn't
way    we    we'd    we'll    we're
we've    welcome    well    went    were
weren't    what    what's    whatever    when
whence    whenever    where    where's    whereafter
whereas    whereby    wherein    whereupon    wherever
whether    which    while    whither    who
who's    whoever    whole    whom    whose
why    will    willing    wish    with
within    without    won't    wonder    would
wouldn't    yes    yet    you    you'd
you'll    you're    you've    your    yours
yourself    yourselves    zero
""".lower().split())


def tokenize(message):
    message = message.lower()
    # split on whitespace
    result = message.split()
    # remove stopwords
    result = filter(lambda x : x not in STOP_WORDS, result)
    # remove any word which does not contain at least a single letter
    result = filter(lambda x : re.search('[a-zA-Z]', x), result)
    
    return result

def build_tuples(root):
    msg_types = {"1" : RECEIVED,
                 "2" : SENT
                 }
    result = []
    for child in root:
        attrs = child.attrib
        result.append(SMSMsg(attrs['address'],
                             msg_types.get(attrs['type'], UNKNOWN),
                             attrs['body'],
                             attrs['time'],
                             datetime.fromtimestamp(int(attrs['date']) / 1000),
                             len(attrs['body']),
                             tokenize(attrs['body']))
                      )
    return result

                                           
def avg_collection(messages):
    longest = messages.next()
    shortest = longest
    
    total = len(longest.message)
    count = 1
    msg_lengths = [longest.message_length]
    vocab_counts = Counter()
    for msg in messages:
        total += msg.message_length
        count += 1
        if msg.message_length > longest.message_length:
            longest = msg
        if msg.message_length < shortest.message_length:
            shortest = msg
        
        msg_lengths.append(msg.message_length)
        vocab_counts.update(msg.tokens)    
            
    return Metrics(count, total * 1.0 / count, longest, shortest, Counter(msg_lengths), vocab_counts)


def pprint_metrics(metrics):
    return '''Total Messages: %s
Average Message Length (in number of characters): %s
Longest Message was %s characters: %s 
Shortest Message was %s characters: %s
Word Counts: %s
''' % (metrics.total_messages,
       metrics.average_length,
       metrics.longest.message_length, metrics.longest.message, 
       metrics.shortest.message_length, metrics.shortest.message,
       metrics.word_counts.most_common())


def histogram_d3_data(metrics, max_length=100):
    result = []
    total = 0
    for item in metrics.histogram.items():
        if item[0] <= max_length:
            total += item[1]
            for _ in range(item[1]):
                result.append(item[0])
    return result

def dump_histogram_data(all_metrics, sent_metrics, recv_metrics):
    print("----")
    print "All Messages Histogram data:"
    result = histogram_d3_data(all_metrics)
    print result
    print len(result)
    print("----")
    print "Adam Sent Messages Histogram data:"
    result = histogram_d3_data(sent_metrics)
    print result
    print len(result)
    print("----")
    print "Adam Received Messages Histogram data:"
    result = histogram_d3_data(recv_metrics)
    print result
    print len(result)

    
def main():
    fname = "sms.xml"
    tree = ET.parse(fname)
    root = tree.getroot()

    result = build_tuples(root)

    to_adam_text = ifilter(lambda x : x.type == RECEIVED, result)
    from_adam_text = ifilter(lambda x : x.type == SENT, result)

    recv_metrics = avg_collection(to_adam_text)
    sent_metrics = avg_collection(from_adam_text)
    all_metrics = avg_collection(iter(result))
    
    print("Adam's sent messages: %s" % pprint_metrics(sent_metrics))
    print("Adam's received messages: %s" % pprint_metrics(recv_metrics))
    print("All messages: %s" % pprint_metrics(all_metrics))
    
    dump_histogram_data(all_metrics, sent_metrics, recv_metrics)
    
if __name__ == "__main__":
    main()

