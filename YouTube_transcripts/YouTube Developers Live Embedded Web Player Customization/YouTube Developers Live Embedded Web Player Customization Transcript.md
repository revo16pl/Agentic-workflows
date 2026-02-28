# Transcript: YouTube Developers Live: Embedded Web Player Customization

**Video ID:** M7lc1UVf-VE
**URL:** https://www.youtube.com/watch?v=M7lc1UVf-VE

[00:10] JEFF POSNICK: Hey, everybody.

[00:11] Welcome to this week's show of
YouTube Developers Live.

[00:14] I'm Jeff Posnick coming to
you from New York City.

[00:16] I'm a member of the Developer
Relations team.

[00:19] And this week I'm really excited
to talk to you about

[00:21] different ways of customizing
the YouTube-embedded player.

[00:24] Before I get started though, I
want a couple of ground rules

[00:28] to just talk about what we're
going to be covering in

[00:31] today's show.

[00:32] There are a lot of different
embedded players, and there's

[00:34] lots of ways to customize
them.

[00:36] But for this particular show,
we're going to be focusing on

[00:39] customizing be iframe-embedded
player, which is our current

[00:45] recommended way of embedding
videos on web pages.

[00:48] And we're going to specifically
focus on the

[00:50] options that are most relevant
for desktop web browsers.

[00:54] A lot of these customization
options we'll talk about do

[00:58] have some effect with mobile
browser playback, but not all

[01:02] of them do.

[01:03] And we're going to just focus
today on how these options

[01:06] affect desktop playback.

[01:08] Another thing that we're not
going to be covering today is

[01:10] using the JavaScript API for
controlling playback.

[01:15] This is obviously a very
interesting topic and a very

[01:16] important topic, it's just a
little bit outside the scope

[01:18] of what we wanted
to talk about.

[01:20] So we're not going to be
covering any of the methods

[01:23] that you could use in JavaScript
to start playback

[01:25] or control playback, or receive
events when playback

[01:29] changes happen in the player.

[01:31] What we are going to be covering
is things that are

[01:33] covered in the documentation
on the specific page, so if

[01:38] you pull that up, we'll
share that with you.

[01:41] And as I'm going through this
demo, a lot of what I'm going

[01:44] to be covering refers to
specific web pages.

[01:47] When we go back and post this
video on YouTube, I'll have

[01:50] annotations linking to all the
web pages, so that you could

[01:52] go there and check them
out yourself.

[01:56] So this is our main jumping off
point for talking about

[02:00] the customization that
you could do to the

[02:03] YouTube-embedded
iframe player.

[02:06] And you could get here from
our main Developers.Googl

[02:09] e.com/YouTubedocumentation.

[02:13] And everything in this parameter
section in the docks

[02:17] is fair game for what we're
going to talk about now.

[02:20] One other thing before I
actually get into explaining

[02:24] these parameters is explain
the two different types of

[02:26] ways that you can load the
iframe-embedded player onto

[02:31] your web page.

[02:32] And we're kind of agnostic as
to the way in which you load

[02:35] it, these parameters are going
to behave the same way

[02:37] regardless.

[02:38] But I just wanted to point out
that there are two different

[02:40] ways of doing it.

[02:42] The first way is using the
iframes kind of like YouTube

[02:48] player, YT.

[02:49] Player constructor.

[02:50] And this is a more programmatic
way of loading

[02:53] the iframe player onto
your web page.

[02:54] So I have this jsFiddle right
here that demonstrates what

[02:58] that will look like.

[02:59] It basically involves loading
in this JavaScript API and

[03:03] calling the YT.

[03:05] Player constructor, and passing
in the ID of a div

[03:08] that's on your page.

[03:10] And you'll see here that there
is this playerVars section

[03:13] that you could pass
in to the YT.

[03:15] Player constructors.

[03:16] So this is where you get to
specify all the options that

[03:19] we're going to be covering today
if you're using the YT.

[03:21] PLayer constructor.

[03:23] And just quickly jumping over
here, this is where I stole

[03:27] that code from in our Getting
Started guide

[03:30] for the iframe API.

[03:32] We talk about how you could
actually get that code.

[03:36] So feel free to borrow it there
or from that jsFiddle.

[03:40] The second way that you load
the iframe player onto your

[03:41] page is just with a simple
iframe tag that you could add

[03:45] to any web page.

[03:47] And this has the same sort of
parameters that the YT.

[03:50] Player constructor is,
kind under the hood.

[03:52] They really end up creating
the same thing.

[03:54] Just that the YT.

[03:55] Player constructor is a
programmatic way of creating

[03:58] this tag using JavaScript.

[04:00] This is if you're just writing
out [? initiable ?]

[04:02] template, or even if you're not
a JavaScript programmer at

[04:06] all and just want to include
some HTML on your page, you

[04:09] could use this tag.

[04:12] And the same parameters we are
going to be talking about can

[04:15] go at the very end of the URL
that you use as a source of

[04:19] the iframe tag.

[04:20] So over here we have autoplay
equals 0 and

[04:23] controls equals 0.

[04:25] And that corresponds to what
we're seeing over here for the

[04:29] playerVars.

[04:30] And the actual documentation for
using that iframe tag is

[04:36] found over here.

[04:38] If you look in the docs over
here, we give some examples.

[04:44] So that's the ground rules for
how you actually will use

[04:47] these parameters that
we are going to be

[04:49] describing in your own code.

[04:52] So I just wanted to run through
pretty much from the

[04:54] top, all these parameters
here.

[04:56] We do have really nice
explanations what they mean in

[05:00] the documentation.

[05:01] So it's going to be a little bit
repetitive in some cases.

[05:05] But I did want to highlight some
specific ones that are

[05:08] the most useful.

[05:09] So autohide comes in
handy quite a bit.

[05:13] This is something that controls
the behavior of the

[05:17] controls, more or less, that
are on the bottom of the

[05:21] YouTube Player.

[05:22] It's not necessarily the initial
state of the controls,

[05:26] but it's more like what happens
the controls once

[05:28] playback starts.

[05:30] And I'm going to demonstrate
the ways of setting those

[05:33] different values by going to
this page over here, which is

[05:37] our YouTube player demo.

[05:39] So this is another really
great resource.

[05:42] And it's an alternative to
writing this code over here or

[05:47] writing this in jsFiddle.

[05:48] It's just a way to play around
with these parameters in a

[05:51] live setting.

[05:54] And we can think of it like our
API explorer, if you've

[05:57] ever used that for
our data APIs.

[06:00] This is the equivalent
for our player APIs.

[06:03] So what it lets you do is go
over here on the right and

[06:06] start choosing different values
for the parameters.

[06:09] And I'm not going to do this
for every single parameter

[06:11] that we didn't talk about, but
just to show you how you could

[06:15] experiment in real time
without having

[06:16] to write any code.

[06:18] Let me just try setting autohide
to 0 over here.

[06:21] I'm going to click
Update Player.

[06:24] And once I set it,
Begin Playback.

[06:28] This is a very old video.

[06:31] Actually, part of what I plan
on doing is replacing the

[06:34] default video that we use in
this demo with this video, so

[06:37] we'll have a very meta
experience, if you happen to

[06:39] be watching this while on the
demo page trying out these

[06:42] parameters.

[06:44] So the main thing to keep in
mind though is that the

[06:47] controls at the bottom
over here did not

[06:48] disappear during playback.

[06:51] And if I were to go over here
and change the autohide to 1,

[06:56] Update Player--

[06:57] it says, loading in the player
with the parameters--

[07:03] you'll see that when I mouse
over, the controls are there.

[07:05] When I move the mouse away,
the controls disappear.

[07:08] So for experiences where you
want maybe a more of lean-back

[07:13] type of situation, where people
aren't going to be

[07:15] interacting with the controls,
or you don't want the controls

[07:17] to overlay the video playback,
it's a very useful parameter.

[07:21] Autoplay is next on the
list alphabetically.

[07:25] Somewhat self-explanatory, if
you add in the autoplay

[07:27] parameter, then the video will
start playing back as soon as

[07:31] the iframe embed is loaded
on the page.

[07:34] I'll give a quick demo
of that over here.

[07:38] And this time, instead of using
the player demo page,

[07:43] I'm going to use that jsFiddle
that we have set up.

[07:46] And I'm going to just change
the autoplay value to 1.

[07:48] I'm going to click Run.

[07:50] And you could see,
here's the embed.

[07:52] It started playing as soon
as the page loads.

[07:55] So there are certain scenarios
where that's useful, certain

[07:57] scenarios where it's not.

[07:58] You have to use your judgment
as to whether autoplaying is

[08:02] the right thing to do.

[08:04] cc_load_policy is something that
controls whether closed

[08:09] captions or subtitles are
displayed by default.

[08:13] And the default behavior--
we don't set anything for

[08:17] cc_load_policy--

[08:18] is that the user's preferences
[? basic ?] on YouTube.

[08:21] There is a way of going in and
saying whether you want closed

[08:23] captions or you don't want
closed captions.

[08:26] That's normally what
takes effect.

[08:27] If you have a specific video and
you know that you always

[08:29] want the closed captions to
be shown, you could set

[08:31] cc_load_policy to 1.

[08:34] Color's a bit interesting.

[08:36] It's not something that I see
widely used and necessarily,

[08:41] but there are some cases where
you might want a little bit of

[08:44] flair, let's say,
in your player.

[08:45] And you don't want the
default behavior.

[08:48] So I'm going to go to the
player demo page really

[08:53] quickly and just show
you what it does.

[08:54] You could set color to white
instead of red, and you update

[09:02] the player.

[09:05] Controls should look slightly
different depending upon

[09:06] whether they're red or white.

[09:08] So it just basically changes the
branding a little bit on

[09:11] the player.

[09:13] Not necessarily the most useful
thing in the world, but

[09:15] it does give you a little
bit more control.

[09:18] Speaking of control, next item
alphabetically is controls.

[09:22] And this is actually
quite useful.

[09:24] There are cases where you can
actually see a lot of

[09:29] performance benefits by changing
this value from the

[09:33] defaults to a specific
option, which is 2.

[09:38] We have a note in the
documentation explaining more

[09:40] about what this does.

[09:42] And if you read the note, it
says that controls=2 can give

[09:45] you a performance improvement
over the default behavior.

[09:49] And the reason why that is is
controls=2 has a way of

[09:53] loading the iframe embedded
player that does not

[09:55] initialize the underlying
Flash player by default.

[10:00] It doesn't initialize it until
you actually click on the

[10:04] video thumbnail to start
the playback.

[10:07] This obviously only applies to
playbacks that do involve the

[10:12] Flash player.

[10:13] The iframe player might decide
that HTML5 video is going to

[10:16] be used instead, in which case
this isn't quite as important.

[10:19] But in situations where Flash
playback is being used, you

[10:21] could really see a significant
performance benefit from

[10:24] setting controls=2.

[10:26] And that might be the default
that we use at some point in

[10:29] the future, as mentioned here,
as soon as some UI issues are

[10:33] worked out.

[10:34] And I'm going to give you an
example of how you could see

[10:37] that performance benefit.

[10:39] It mainly comes across
when you have--

[10:41] let's say, I don't want to say
a specific number, but if you

[10:44] have multiple iframe embeds
on the same page.

[10:46] So this one over here has--

[10:48] I think there might be 50 from
the Google Developers channel.

[10:52] So the first thing that we're
going to look at is behavior

[10:56] pretty much by default, where
there's controls=1 or if you

[11:00] leave out controls.

[11:01] It's the default.

[11:02] And it can take some time for
these underlying Flash players

[11:08] to all initialize, and can add
some latency to the point

[11:12] where things look like
they're ready to be

[11:15] interacted with on the page.

[11:17] So not necessarily the
best user experience.

[11:20] If you take the same thing and
you change it to controls

[11:22] equals 2 explicitly, then you
should see a much better

[11:26] performance.

[11:27] It's quite remarkable,
actually.

[11:30] So what's going on?

[11:31] [? You can see ?] now again,
it's just loading in these

[11:33] thumbnails.

[11:34] It's not initializing the Flash
player for each video.

[11:38] And you could have--

[11:40] I don't want to say you should
put thousands of embeds on the

[11:42] same page-- but if you do happen
to have a large number

[11:45] of embeds on the page, you
will see a difference.

[11:49] So very important to
keep that in mind.

[11:50] A few other parameters
that are not

[11:53] necessarily as exciting.

[11:55] There's keyboard support for
the ActionScript player.

[12:00] I'm not really sure why you
would want to turn this off.

[12:03] I think it's actually kind of
nice to keep it on, but we do

[12:05] have the option of turning
it off if you want.

[12:09] This particular parameter
is quite important, the

[12:13] enablejsapi.

[12:14] And what it'll let you do is
ensure that you are able to

[12:18] talk to the iframe player
on the page using

[12:21] the JavaScript API.

[12:22] So as I mentioned, we're not
actually going to be covering

[12:25] anything about the JavaScript
API in this particular

[12:28] session, but plenty of
people have used it.

[12:31] And the one case where you
really need to be sure you're

[12:34] explicitly setting this is when
you're writing the iframe

[12:37] tag directly to the page.

[12:41] So kind of like this.

[12:45] Because when you're
using the YT.

[12:46] Player constructor, it pretty
much will be set automatically

[12:50] for you by default.

[12:52] Just because by virtue of the
fact that you're using

[12:54] JavaScript to initialize the
player, chances are you are

[12:57] going to want to talk to the
player with JavaScript.

[12:59] So it always gets set for you.

[13:00] But that's not the case if you
explicitly are writing an

[13:03] iframe tag to a page.

[13:04] So you really do need to make
sure there that you have

[13:06] enabled jsapi set to 1.

[13:10] And that's necessary in order to
talk to the iframe player.

[13:17] The end tag, and a little
bit further down

[13:20] the alphabet is start.

[13:22] So these are two corresponding
tags.

[13:24] This gives you a really easy way
of putting an embed on a

[13:27] page that has its custom end
time and a custom start time.

[13:31] So if you have a three-minute
video and you really want to

[13:35] embed 30 seconds in the middle
of the video, you could use

[13:37] those two tags to do it.

[13:38] As soon as playback reaches
the end tag, playback will

[13:43] effectively stop.

[13:44] So that could be useful.

[13:47] fs parameter--

[13:49] not super useful anymore.

[13:50] Basically, it lets you control
whether there is a full-screen

[13:54] button on the ActionScript
3.0 player.

[13:56] But I don't think it has an
effect on the HTML5 player.

[14:00] So not really sure why you would
want to change that.

[14:04] iv_load_policy is something that
controls whether, I guess

[14:07] interactive video
annotations--

[14:11] for lack of a better way of
describing it-- is shown on

[14:14] your video by default.

[14:16] So there's a couple of different
values over here.

[14:18] You use 1 or 3.

[14:20] Basically, setting at 1 will
make sure that those

[14:22] annotations are shown.

[14:23] Setting it to 3 will make
sure that they're

[14:24] not shown by default.

[14:26] But at any point, the user can
change the setting explicitly

[14:29] in the player, if they want to
show or hide the annotations.

[14:34] List is a really interesting
one.

[14:36] And there is quite a bit to
talk about with list.

[14:39] So I'm actually going to defer
at this point to a whole blog

[14:42] post that we put together to
talk about the different types

[14:46] of values that the list
parameter and the listType

[14:51] parameter, which is
an associated

[14:53] parameter, can take.

[14:54] I'll link to this blog post in
the video annotations, so you

[14:56] can read it in more detail.

[14:58] But the long and short of it is
that it's a really easy way

[15:01] to take a simple embedded player
on your page and use

[15:05] that to display a list of videos
without having to hard

[15:09] code the video IDs in advance.

[15:11] So you could have one specific
player on your page and say,

[15:14] play back the most recent videos
from a specific YouTube

[15:17] channel or specific playlist or
specific search term, even.

[15:23] So you could say, this is an
embedded player that will show

[15:26] the latest videos that
match the search

[15:29] from the YouTube API.

[15:30] Something along those lines.

[15:32] It's quite useful.

[15:33] I don't think as many people
know about it as they should.

[15:36] So hopefully people will watch
this and start using it a

[15:38] little bit more.

[15:40] listType goes hand in hand
with the list parameter.

[15:43] There is a loop parameter.

[15:45] And the loop parameter will--

[15:49] as explained in the
documentation--

[15:51] allow you to automatically
restart playback of a video

[15:55] when the playback has ended.

[15:57] You have to have a little bit of
a hack, if you're trying to

[16:00] do this for a single video,
where you create a playlist

[16:02] that has only one video
entry in it.

[16:04] So we have a little bit
more info there.

[16:06] modestbranding is something
that's covered in a different

[16:09] blog post, which we will also
link to from the annotation.

[16:12] And it talks about the option
down here at the bottom.

[16:17] It's not exactly a fully
logoless player.

[16:20] There still is a YouTube logo
involved that shows, I think,

[16:25] on the pause screen in the upper
right-hand corner, or in

[16:27] the queued screen.

[16:29] But it is one parameter that you
could set to tone down the

[16:33] YouTube branding
on the player.

[16:36] And that's something that you
might want to keep in mind if

[16:40] you have a scenario where you
want to embed, but don't want

[16:43] to make it fully YouTubed.

[16:47] The origin parameter is
something that can be used

[16:51] when you are using the iframe
embed tag, and you're going to

[16:55] be interacting with the iframe
embed using JavaScript.

[17:00] So as mentioned before, you
might want to explicitly put

[17:02] in enablejsapi.

[17:03] You also might want to
put in the origin

[17:06] parameter over here.

[17:08] And you set it equal to the full
URL for your web page.

[17:12] And this is a security mechanism
to make sure that

[17:17] only JavaScript that's run from
your host web page is

[17:20] able to talk to the player.

[17:23] And if you're using the YT.

[17:24] Player constructor, it gets
set automatically for you.

[17:27] So this is another instance
where you really only have to

[17:29] worry about this when you're
explicitly writing out an

[17:32] iframe tag.

[17:34] And sometimes people run into
issues where they explicitly

[17:38] were using the iframe tag, and
they're trying to talk to it

[17:41] using JavaScript, but their
code just isn't working.

[17:45] One thing to debug in that case
is check to see whether

[17:47] you are setting the
origin parameter.

[17:49] And if you are, make sure that
it's really set to the full

[17:53] URL of the host name
for your site.

[17:57] playerapiid--

[17:59] this isn't really relevant
anymore.

[18:01] It's more of a way of using the
older JavaScript API for

[18:04] identifying your player.

[18:06] There's a playlist parameter
which is easily confused with

[18:10] the list parameter.

[18:11] And it is something that
actually takes in a different

[18:13] set of values.

[18:14] The playlist parameter takes
in a list of video IDs.

[18:18] So this does not have to
be a real playlist, a

[18:20] [? list that ?] exists
on YouTube.

[18:21] It doesn't have to be anything
that uploads

[18:26] from a specific channel.

[18:27] It could just be a list of any
video IDs that you want.

[18:30] And it's a way of generating a
dynamic, on-the-fly playlist.

[18:35] So some use cases where
that might be useful.

[18:39] There's the rel parameter.

[18:41] And this controls whether or not
the end screen of a video

[18:45] will display related
videos or not.

[18:49] Most folks are familiar with the
fact that once you reach

[18:51] the end of a YouTube video,
you'll see some configuration

[18:55] of thumbnails with suggestions
for other videos to play.

[18:59] We do have the ability to turn
that off if you feel like you

[19:01] do not want that
on your embeds.

[19:06] showinfo is something that will
control what is displayed

[19:12] initially in the
queued states.

[19:15] There's ways of taking the
default behavior and kind of

[19:18] toning it down a bit, again,
where you don't see quite as

[19:20] much before the video starts.

[19:23] And you can set it to
show info equal

[19:25] 0, if you want that.

[19:27] showinfo's actually used
in another case.

[19:29] And that's when you're using
the list player.

[19:31] And explicitly setting showinfo
equal to 1 will make

[19:36] it so that there is a list of
queued videos in the playlist

[19:41] in your list player.

[19:42] So if we look over here,
this is a case where

[19:44] showinfo is set to 1.

[19:47] This is a playlist player that's
loading everything from

[19:49] Google Developers.

[19:50] And you'll see, before playback
has even started, you

[19:52] have this handy thumbnail for
all the videos that are queued

[19:56] up in the playlist for
the next videos.

[19:58] It will let you choose what
you want to start with.

[20:00] So it is actually quite useful
for scenarios where you're

[20:04] doing the list player.

[20:08] Start parameter we really
covered before, hand in hand

[20:12] with the end parameter.

[20:14] And the last one is the
theme parameter.

[20:17] This is something similar to
that earlier color parameter

[20:19] that just lets you change the
default way that the player

[20:23] looks and gives you some degree
of customization in

[20:26] that regard.

[20:29] There are now a couple of
deprecated parameters.

[20:32] I'm not going to cover those.

[20:33] They're deprecated
for a reason.

[20:34] We don't want folks using
them anymore.

[20:36] I wanted to point out that
there are occasionally--

[20:40] I don't want to say rumors--
but certain parameters out

[20:44] there that people pass around
and say, hey, you can use this

[20:46] player parameter to force HTML5
playback, or use this

[20:51] player parameter to force
playback in a certain quality

[20:53] level or something along
those lines.

[20:56] Those are undocumented
for a reason.

[20:58] We really do not want people to
use parameters that aren't

[21:01] explicitly mentioned in the
documentation, partly because

[21:04] we're not fully committed
to supporting them.

[21:06] They might sometimes work in
some cases, and they might

[21:10] stop working at any time
in the future.

[21:12] So we really don't want people
to build things that rely on

[21:15] those parameters.

[21:17] And there's also just cases
where we want control to be in

[21:22] the hands of the person who's
viewing the embed.

[21:25] So we want control over the
default playback to really lie

[21:30] in the person who's using the
web browser and might have

[21:33] Flash enabled.

[21:35] Or the default auto quality for
the quality level in many

[21:41] cases gives the best playback
experience.

[21:44] So if you don't see something
listed as a supported

[21:47] parameter, please
don't use it.

[21:49] And if you do happen to find
some parameters, please don't

[21:52] complain if they ever break at
some point in the future.

[21:55] I guess that's the
main takeaway.

[21:59] That covers the list of all
the supported parameters.

[22:01] We had a lot of different
web material here.

[22:04] And be sure to check out the
annotations on the video for

[22:06] links to everything that
we covered today.

[22:09] Thanks very much for watching.

[22:13] And we'll see everybody
next week.

[22:17] Cheers.

