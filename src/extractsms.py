import xml.etree.ElementTree as ET
from collections import namedtuple, Counter
from itertools import ifilter
from datetime import datetime 
import re

SMSMsg = namedtuple("SMSMsg", ['phone_number', 'type', 'message', 'date', 'timestamp', 'message_length', 'tokens'])
Metrics = namedtuple("Metrics", ['total_messages', 'average_length', 'longest', 'shortest', 'histogram', 'word_counts' ]) # vocabulary #normalized_vocab #avg_word_length #message_length_histogram

# message types
RECEIVED = 1
SENT = 2
UNKNOWN = 3

# Stop words to omit from word counts
STOP_WORDS = set(":p :) :( ;) as not the it in of so be it's am i'm an a and i is to too you my that".lower().split())


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

