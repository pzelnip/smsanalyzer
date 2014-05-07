smsanalyzer
===========

Some playing around analyzing SMS messages

I recently discovered Android Super Backup (https://play.google.com/store/apps/details?id=com.idea.backup.smscontacts)
which (among other things) allows you to export SMS messages to an XML file.

This was cool, but I wanted to just have the text of the messages.

So I wrote a Python script to extract the messages.

Then the amateur data scientist in me started wondering about what kinds of things I could discover by analyzing
the messages.

So I modified the script to do things like spit out some basic metrics (what's the average message length, etc).

And from there I started adding more and more.

At this point, this is now a place to play with doing some data analytics and maybe play with a few new libraries.

In the repo is also a html file which shows histograms of messages from all SMS's between myself and a friend using
the popular D3.js library (http://d3js.org/)
