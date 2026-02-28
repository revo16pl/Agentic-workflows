# Transcript: Turn Claude Code into Your Own INCREDIBLE UI Designer (using Playwright MCP Subagents)

**Video ID:** xOO8Wt_i72s
**URL:** https://www.youtube.com/watch?v=xOO8Wt_i72s

[00:00] I keep tweeting about the workflow I'm

[00:02] about to show you, and every single time

[00:04] I do, the tweet goes viral. Why? Because

[00:07] it unlocks the missing 90% of Claude

[00:10] Code's incredible design capabilities.

[00:13] If you're using Claude Code, Cursor, or

[00:16] any other coding agent for front-end

[00:18] development, you need to hear this. If

[00:20] you're anything like I used to be, you

[00:22] prompt for a greatl looking modern

[00:24] design just to end up with the same

[00:26] generic shad CN purple UI that you see

[00:29] all over Twitter. Getting pixel perfect

[00:31] refinements feels impossible and like

[00:34] you're just going around in circles

[00:36] trying to convince the model to please

[00:37] just do what you asked it. I hate to

[00:39] break it to you, but those cookie cutter

[00:42] designs aren't the model's fault. It's

[00:44] the environment that you're placing

[00:46] those agents in. You're taking an

[00:48] incredible PhD level intelligence and

[00:51] you're forcing it to design with

[00:52] essentially blindfolds on the models.

[00:55] They can't see their own designs. They

[00:57] can only see the code that they're

[00:59] writing. Or in other words, they're only

[01:00] using the text side of their modality,

[01:02] not the vision side. What I'm about to

[01:04] show you is a massive unlock our team

[01:07] has found. It's a single tool that gives

[01:09] the AI eyes to see. the missing link in

[01:12] a workflow. All built around the

[01:14] Playright MCP, allowing these agents to

[01:17] control the browser, take screenshots,

[01:19] iteratively self-correct on their

[01:21] designs, and to do so much more. I'll

[01:23] take you through my exact workflows that

[01:25] will give you design superpowers,

[01:28] including the setup for sub

[01:30] agents/comands,

[01:31] the Playright MCP config details, and

[01:34] also how I've customized my claw.md

[01:37] file. In addition to some other hard one

[01:39] insights, I will also sneak in some of

[01:42] the most powerful mental models and

[01:45] tactics that we've discovered for

[01:47] getting the most out of cloud code along

[01:49] the way. Feel free to reference the

[01:51] descriptions timestamps to skip around

[01:53] to what's most relevant to you. By the

[01:55] way, I'm Patrick, the CTO and co-founder

[01:57] of an AI native startup who's been using

[02:00] Cloud Code heavily since it was first

[02:02] released back in February. This workflow

[02:05] is the single biggest front-end unlock

[02:07] that we found. We have the honor of

[02:09] working with the world's largest brands

[02:11] including Google, Coca-Cola, Disney,

[02:14] Nike, Microsoft, and others who expect

[02:17] worldclass designs. So, we're constantly

[02:19] looking for ways to get any edge that we

[02:22] can. And I hope you can benefit from

[02:23] these workflows, too. So, with that,

[02:25] let's dive in. Playright is a framework

[02:28] developed by Microsoft that is actually

[02:30] more for web testing and automation

[02:33] allowing you to navigate around the

[02:36] browser and take screenshots and do

[02:38] different endto-end tests. But what's

[02:40] really really powerful for our purposes

[02:42] is the MCP that they've released. So

[02:45] I'll go ahead and show you the Playright

[02:47] GitHub page. As you can see, we've got

[02:49] over almost 76,000 stars at the time of

[02:52] this recording. They highlight Chromium,

[02:54] WebKit, and Firefox as different

[02:56] browsers that you have access to. But if

[02:58] I navigate over to the

[03:00] Microsoftplayright-m

[03:02] repository, we've got a bunch of readme

[03:06] items, including quick start guide here

[03:09] for Cloud Code and other agents. As you

[03:11] can see, it is really easy to add

[03:14] Playright to Cloud Code, but I will

[03:15] revisit this in a second to give you a

[03:17] few more configuration details that you

[03:19] want to include. Now that you know a

[03:20] little bit more about playright, I want

[03:22] to introduce you to the key concept that

[03:24] I keep coming back to as I add new tools

[03:26] and in this case for a design workflow

[03:29] and that is this orchestration layer.

[03:31] See what we want to do is we want to put

[03:33] claw code in a framework to give it a

[03:36] foundation where it's able to have all

[03:38] the context it needs all the tools to go

[03:41] out and take actions or get additional

[03:43] context and then clear validation state

[03:46] examples of good and bad outcomes style

[03:48] guides or anything else that can give it

[03:50] a definitive example of what is needed

[03:53] in terms of output. So if you have the

[03:55] validation such as a UI mock or a style

[03:58] guide, you have the tools such as of

[03:59] course playright in this case and you

[04:01] have the context well-written prompts

[04:03] and documentation you will get so much

[04:05] more success out of claude code than it

[04:07] comes just out of the box. So in this

[04:09] case we are focusing mostly on the

[04:11] playright tool and also the validation

[04:14] step which is baked into some of my sub

[04:16] aent workflows. The second key insight

[04:18] that really brings the 10x and the 10x

[04:21] design flow is this idea of an iterative

[04:24] agentic loop. Imagine as we get more and

[04:27] more capable models, what we want to do

[04:29] is we want to give them access to more

[04:32] and more of our workflow so that they

[04:34] can not just run for five minutes, but

[04:36] they could run for half an hour or an

[04:38] hour or even longer than that. The huge

[04:41] unlocks that we get in productivity come

[04:43] from this iteration loop that allow

[04:45] these agents to not just run for longer

[04:47] as I mentioned but also to come to much

[04:50] better outputs. We need a fixed spec or

[04:54] validator in order to iterate against so

[04:58] that we can compare the output that cla

[05:00] code gets again and again until we get

[05:03] exactly the output that we're expecting.

[05:04] In this case, you can imagine claude

[05:06] code first looks at a spec. So, a style

[05:08] guide, a UI mock, whatever you're

[05:10] providing in the prompt and some of

[05:12] these other bits of context. And then

[05:14] you allow it to go ahead and tool check

[05:17] or look at the playwright screenshot in

[05:20] our case and compare that iteratively to

[05:23] what it's building and back to the spec.

[05:25] So, if it's able to go out, make some

[05:28] changes, take a screenshot, look at

[05:30] that, and then identify, oh shoot, this

[05:32] SVG is nowhere close to what the user

[05:35] asked me, and then go back again. That

[05:36] iterative loop is what really gets us to

[05:39] these full agentic workflows and saves

[05:41] us a ton of time because we can kick off

[05:44] a process, go work on something else and

[05:46] not have to babysit it and prompt five

[05:48] different times in order to get to the

[05:49] end result. You have that context built

[05:52] in. And the final big conceptual piece

[05:54] here is thinking about the training data

[05:56] that is under cloud code, specifically

[05:59] Opus 4.1 and Sonnet 4. What do they have

[06:02] in their neural nets or what circuits do

[06:05] they have in their minds when it comes

[06:07] to good design? If you think about it,

[06:09] this is just an estimation here, but the

[06:11] common crawl and text makes up the

[06:14] majority of the training data. So, this

[06:16] is books, just general stuff on the

[06:17] internet, but we also have code that

[06:19] these foundation labs are training more

[06:21] and more on. And then we have images and

[06:23] the multimodal models. Multimodal

[06:25] meaning, of course, you're bringing in

[06:27] all kinds of different modalities,

[06:28] including images and text in this case.

[06:30] The thing is though, when we're

[06:32] typically using cloud code, we're not

[06:34] tapping into the images side or the

[06:36] visual modality within cloud code.

[06:38] Indirectly, we get a little bit of that

[06:39] benefit, but we're really just looking

[06:41] at code best practices and other design

[06:44] principles, but we're not allowing the

[06:46] model to use its intellect when it comes

[06:48] to understanding and looking at visual

[06:51] design. So, we're missing out on all

[06:53] that intelligence in the model, all

[06:55] those neurons, if you will, or circuits

[06:58] that help the model parse visual bits.

[07:01] And that's where being able to provide a

[07:03] screenshot via the Playright MCP unlocks

[07:07] all of that potential, which as you can

[07:08] imagine, when you're looking at designs,

[07:11] that is a huge, huge help versus not

[07:14] being able to think about things from a

[07:16] visual perspective, but more from an

[07:17] abstract or coding best practices

[07:19] perspective. So the playright MCP

[07:22] getting all that additional visual

[07:24] context unlocks a lot of intelligence as

[07:26] well from cloud code. So if I go back

[07:28] here, we can scroll down to a few of the

[07:31] playright capacities that are most

[07:33] helpful. The first is being able to

[07:35] automatically capture screenshots. So

[07:38] you can imagine allowing claude code to

[07:40] open up pages that you're working on or

[07:42] to automatically trigger that through a

[07:44] cloudMD configuration sub agent or a

[07:47] slash command that you can run which

[07:49] I'll show you in a second here. This is

[07:51] the most powerful piece because it

[07:53] unlocks the vision modality within cloud

[07:55] code and allows you to enhance its

[07:59] ability to think critically through

[08:00] designs and also to see pixel perfect

[08:03] captures of different UI elements that

[08:06] need to change.

[08:07] The second one is being able to read

[08:09] browser console logs. So having access

[08:12] to both the browser console logs and the

[08:14] network logs in order to basically view

[08:17] them and automatically read and make

[08:20] changes as needed.

[08:22] We can also emulate different devices in

[08:24] various browser sizes. So you're

[08:26] essentially setting the Chrome or

[08:28] whatever browser window when it

[08:30] launches. And you can also emulate, for

[08:32] example, an iOS device. You can navigate

[08:35] around the browser. So you can click

[08:36] around, enter form field data and cloud

[08:39] code can automatically look at context

[08:41] and make the next step. Okay, so that's

[08:43] awesome. But what does it actually get

[08:45] us in terms of workflows? These are the

[08:47] best workflows that I found. The first

[08:49] that is mostly the theme of this video

[08:51] is being able to agentically iterate on

[08:53] the front end using the screenshots and

[08:55] the logs that it it gathers. And this is

[08:57] the key to really producing much better

[09:00] looking UIs. The second is automatically

[09:03] being able to fix any obvious UI errors

[09:05] or errors that are in the console. Then

[09:07] you have the ability and this is really

[09:08] cool to navigate the browser. You can

[09:11] imagine if you have a user spec of I do

[09:13] XYZ and I get an error or there's a

[09:15] visual error when this state happens.

[09:17] You can ask cloud code to navigate in

[09:20] that same method. click buttons, enter

[09:22] form field data, and navigate around in

[09:24] order to reproduce a certain state and

[09:26] then grab the console logs or any other

[09:29] context that's needed in order to help

[09:30] solve your issue. Another cool workflow

[09:32] is being able to visually render and

[09:34] screenshot or scrape different reference

[09:36] URLs. So you can imagine if you put in a

[09:39] URL or a couple of them that reference a

[09:42] beautiful design or a website that you

[09:44] would like some inspiration from, you

[09:46] can include that in your prompt or spec

[09:48] and then let playright go out navigate

[09:50] that locally on your browser and take a

[09:52] screenshot of those pages or get any

[09:54] other context. And then you have the

[09:56] original intent of playright which is

[09:57] the automated end toend testing or any

[09:59] accessibility audits being able to ask

[10:01] it to go and look for any accessibility

[10:03] issues. We have mobile responsive

[10:04] testing which is really helpful even if

[10:06] you just do a quick tablet, desktop and

[10:09] mobile view port size or of course

[10:12] emulating like an iOS device to just get

[10:14] a quick gut check on if there are any

[10:16] mobile responsive issues. One kind of

[10:18] cool use case that I actually had cloud

[10:21] code come up with on its own is being

[10:23] able to scrape data. I was using

[10:24] firecrawl to gather some data which is

[10:27] another MCP from a few websites and it

[10:29] got a 403 i.e. it was blocked on a

[10:32] couple of them. So, it went ahead and

[10:34] spun up a new Playright browser in order

[10:36] to load that same web page and then

[10:38] gather all the data on its own, which I

[10:41] thought was pretty clever and just cool

[10:43] to see these emergent properties. And on

[10:45] that note, what's so cool is that these

[10:48] MCPs can allow cloud code to do so much

[10:51] more than just in the coding modality or

[10:54] in how we typically think of, for

[10:55] example, Playright. It really gives it

[10:58] full access to your browser to be a full

[11:00] browser-based agent. And you can imagine

[11:02] from the data scraping idea to

[11:04] automatically logging in and submitting

[11:06] data or getting to a certain end state

[11:07] in your app or just navigating a website

[11:10] to do almost anything. This is a really

[11:12] powerful unlock for cloud code. All

[11:14] right, I'm going to show you a couple

[11:16] key installation details that you may

[11:19] want to consider when configuring

[11:21] playright in addition to my sub agents

[11:24] pod MD file customizations/comands

[11:27] and a few other details that have been a

[11:29] huge game changer for me. So with that

[11:31] you can see we're able to configure

[11:34] different browsers but this is done at

[11:36] the MCP config level. So with some MPC

[11:40] configurations you'll define it in a

[11:42] JSON blob like this and you can see you

[11:45] can just supply different arguments but

[11:47] that could alternatively be the browser

[11:49] that you want. So two I want to call out

[11:51] are the browser that you're using also a

[11:54] device if you want to emulate for

[11:56] example the iPhone 15. And then another

[11:59] one that's really interesting is being

[12:00] able to run in headless or headed mode.

[12:03] I usually run it just in the default

[12:04] which is headed. So I can see it up and

[12:06] and uh navigating the browser. You can

[12:08] easily grab in the installation section

[12:11] for cloud code just this one line here

[12:14] in order to install the MCP. I can just

[12:17] run this sample command. Uh in this case

[12:20] I've already got playright installed of

[12:22] course. So I'll go ahead and fire up

[12:23] claude. Then now if I type for/mcp,

[12:26] you can see that I've got it installed

[12:28] here along with a couple other MCPS.

[12:31] This is just my personal website uh for

[12:33] demonstration purposes. So I don't have

[12:35] I just have a couple MCP options here.

[12:37] Here you can see exactly what

[12:38] configuration it's using and arguments

[12:40] that it's applying. And you can also

[12:42] view the tools which show the many

[12:45] different tools that it gives Cloud Code

[12:47] access to. There is a vision mode for

[12:49] playright which allows it to use

[12:51] coordinate based operations instead of

[12:53] the default which is the accessibility

[12:56] map which is basically just a way to

[12:58] navigate the different elements within a

[13:00] website which is a lot faster and easier

[13:02] but for some applications it can be

[13:05] better to use vision mode. So that's

[13:06] another argument you might want to

[13:08] consider using. I know these config

[13:10] files like a cursor rules or cloudmd can

[13:13] sound pretty boring when you first think

[13:15] about it. But in this case, if you watch

[13:17] Enthropics different YouTube videos or

[13:20] if you read through all their

[13:22] documentation and guides, they really

[13:24] think about these cloudm files as being

[13:26] memory for the agents. So everything you

[13:28] write here is basically put right after

[13:31] the system prompt when you start up any

[13:33] cloud code session. So any details that

[13:35] you want to be brought into every single

[13:37] session that you're using, shortcuts

[13:39] that prevent cloud code from having to

[13:41] go grip around and grab a bunch of

[13:42] context or any best practice or rules

[13:45] that you want it to follow like a style

[13:46] guide or get styles. Uh so like how do

[13:49] you want commits and branches and PR

[13:52] structured all that should live in

[13:53] something like this so that it's pulled

[13:54] in automatically. And what that means is

[13:56] just one less thing. It's essentially an

[13:58] automation. one less thing that you have

[13:59] to worry about every time you're using

[14:01] cloud code that just abstracts it away

[14:02] from your mind and it's also portable so

[14:05] other people on your team can take that

[14:06] exact same cloud config file and move it

[14:09] around. So with that one of the biggest

[14:12] lifts when it comes to playright in

[14:14] terms of getting that agentic loop that

[14:15] keeps moving is to add a configuration

[14:19] down here that speaks to that. So I've

[14:22] got this visual development section and

[14:24] in there I've got a design principles

[14:26] spot here. This basically just points

[14:28] Claude to a few different documents that

[14:31] I provided in this context folder. I'm a

[14:33] big fan of doing this where I'll just

[14:34] drop a bunch of context in this folder.

[14:36] So, in my case, it's like uh for a

[14:39] personal website summary of my LinkedIn

[14:41] uh kind of my life story listed out a

[14:43] bit, but also design principles and a

[14:45] style guide that I want Claude Code to

[14:47] follow. So, if I open up the design

[14:49] principles file, you can see this is

[14:51] just a long list of a bunch of different

[14:53] principles I want Claude Code to follow.

[14:56] In this case, I actually used Gemini

[14:58] deep research on all the best design

[15:01] principles for a specific aesthetic that

[15:03] I like a lot. I had it make that into a

[15:06] much more concise markdown file. Went

[15:08] through, edited a few things, and then I

[15:10] use that as my design principles MD

[15:11] file. I do find that doing the deep

[15:13] research approach for SEO best practices

[15:16] or design best practices or back-end

[15:18] architectural principles is an amazing

[15:20] way to kickstart what you're working on,

[15:22] especially if it's a little bit out of

[15:24] your domain of expertise. An incredible

[15:26] way to use just this massive amount of

[15:28] knowledge and to make it actionable

[15:30] going from collecting that knowledge in

[15:31] a deep research platform into an

[15:34] actionable thing that an agent like

[15:36] Claude Code can take and run with. And

[15:37] then if I go down here, this is where I

[15:40] lay out specifically how I want Claude

[15:42] Code to use the Playright browser on a

[15:45] kind of a normal day-to-day level.

[15:47] Whenever you're doing anything that

[15:48] involves the front end, I want it to go

[15:51] ahead and navigate to the pages that

[15:53] were impacted by those front-end changes

[15:55] and then reference this verification

[15:57] step of the uh orchestration framework

[15:59] by using these markdown documents and

[16:01] then look for any acceptance criteria

[16:04] that may have been laid out in the

[16:05] prompt that I had written. So Cloud Code

[16:07] can look and see what exactly I

[16:09] supplied. So again, this could be a UI

[16:11] mockup. This could be just some text and

[16:13] other instructions that I gave it. A

[16:15] Figma MCP. There's all kinds of

[16:17] acceptance criteria that could have been

[16:18] brought into the prompt. And then I want

[16:20] it to just pull up the normal browser

[16:22] size that I've got here for the desktop

[16:24] viewport. You could also have this be a

[16:27] mobile or tablet size or include all

[16:28] three of them, but just for the sake of

[16:30] time, I just wanted to quickly open up

[16:32] the window and and look. And then of

[16:33] course I also want to check for any

[16:34] console errors because that's a huge

[16:36] timesaver. In addition to that, I want

[16:38] it to sometimes go into a comprehensive

[16:40] design review. So this is where it will

[16:43] use this sub agent that I created that

[16:46] I'll mention in a second here in order

[16:48] to go ahead and do a much deeper dive

[16:50] than just this quick test that I showed

[16:52] above. If I'm creating a PR, I want it

[16:54] to go ahead and do that or any very

[16:56] significant UIUX refactors and a few

[16:59] other key details that I want it to

[17:01] remember just to make sure that it

[17:02] doesn't try to bring in any new

[17:04] frameworks or libraries or anything. One

[17:05] powerful trick I want to call out here,

[17:08] this is a huge tip and I've learned so

[17:10] much by doing this is being able to go

[17:13] reference the examples that Enthropic

[17:16] gives when it comes to how to configure

[17:18] any sort of document, but especially

[17:20] things like sub aents, the cloud MD

[17:22] file, slashcomands, and actions that run

[17:25] in GitHub, for example. So, the first

[17:27] thing I just want to point out is their

[17:29] GitHub. They've got a lot of great stuff

[17:31] in here. some actual courses, uh the

[17:33] cookbook, which is a lot of different

[17:35] examples of interesting ways to use

[17:37] claude, and then also the claude code

[17:39] security review repo. It's a slash

[17:41] command. So, just as a reminder,

[17:43] whenever you type forward slash, it's

[17:44] it's these commands that come up. And

[17:46] I've got a few custom ones that I built

[17:48] in accordance with this convention where

[17:50] you have acloud folder and then in there

[17:52] you've got a commands folder and then

[17:53] you can create these markdown files. So,

[17:55] what I'll do is I'll just look at what

[17:57] is Anthropic doing? Like, how are they

[17:59] structuring these commands or these sub

[18:01] agents? And there's a lot of cool stuff

[18:03] in here. For example, in this case, this

[18:06] ability to basically just take your

[18:08] working or work in progress files that

[18:10] are not in a PR yet. So, this was a

[18:12] great little workflow I borrowed and

[18:14] just looking at how they structure

[18:15] things, how they use capital, all caps

[18:17] in certain cases. Overall, it's it's

[18:19] great to learn from exactly how they're

[18:21] building things. Another guide I would

[18:23] highly recommend, I've recommended this

[18:25] to so many people, is the cloud code

[18:27] best practices for agentic coding guide.

[18:29] This is does a great job especially for

[18:31] things like claude MD of breaking down

[18:33] exactly how to structure things and the

[18:35] methodology behind it all. And then I

[18:37] would also recommend the documentation.

[18:39] It's very well put together. A lot of

[18:41] great examples specifically for cloud

[18:42] code here. All right, so with that I'll

[18:45] go ahead and show you mycloud directory.

[18:47] Then we've got an agents directory and a

[18:49] commands directory. So in agents, you

[18:51] can see I've got the design reviewer.

[18:53] Just as a quick example, in order to

[18:56] invoke this, I'll just do at@ agent

[18:58] design review. I could give it like a PR

[19:00] or more instructions like please review

[19:02] the last three commits that I've made.

[19:05] And that's going to go ahead and kick

[19:06] off the agent design reviewer. You can

[19:10] see here it's pretty intelligent. It's

[19:12] going ahead and using Git to just grab

[19:14] the last three commits and it's going to

[19:16] go ahead and launch the agent in order

[19:19] to follow the exact workflow that I laid

[19:21] out there. So, while it's running, I'm

[19:23] going to go ahead and show you that

[19:24] workflow. So, I've got a name, the

[19:26] description of what it's doing. You can

[19:28] see it's a design review agent that is

[19:30] able to look at pull requests or general

[19:32] UI changes and then I give it specific

[19:35] access to different tools. Uh so I'm

[19:38] able to explicitly ask it to use just

[19:40] basically playright context 7 which is

[19:43] for documentation and really great MCP

[19:45] as well and then also the built-in uh

[19:48] tools that you typically give an agent.

[19:50] I'm having it use sonnet for this kind

[19:52] of work. I feel like I haven't noticed a

[19:54] huge difference or any difference

[19:55] between sonnet and opus and of course

[19:57] sonnet's way cheaper. And then I just

[19:59] give it this description of what I'm

[20:01] asking it to do. So in this case I'm

[20:03] channeling trying to get to the areas

[20:06] within its its circuits or it's its

[20:08] neural net that are to do with design

[20:10] reviews and uh principal level

[20:12] designers. So I'll usually give it

[20:14] persona to try to channel that and then

[20:16] a few examples. So stripe airb uh some

[20:19] some cliche classics in Silicon Valley

[20:22] and then I give it a core methodology

[20:24] and mission to go on here for reviewing.

[20:27] And then I give it a step-by-step guide

[20:29] of uh exactly how to go about doing a

[20:32] robust design review including looking

[20:34] for accessibility, code health or

[20:36] robustness. So you can see it goes

[20:39] through each of these steps and then I

[20:40] also give it a format for how exactly I

[20:43] want the report to look and I just ask

[20:46] it not to do much more than that. So you

[20:48] can see um the structure here and then

[20:51] also the exact uh process for navigating

[20:55] like which tools to use and when. In

[20:57] order to come up with this, I actually

[20:58] used another deep research report. I had

[21:01] it go out and basically collect the best

[21:04] design review practices from essentially

[21:07] all of the internet and had it all

[21:09] filtered through Claude Opus in this

[21:11] case to shape it up using the agent

[21:14] creation tool in Claude code in addition

[21:16] to referencing different examples that

[21:19] Enthropic has put in their GitHub repos.

[21:22] So, just to show that you can go and

[21:25] open up by typing in agents,

[21:28] and that will open this new window that

[21:29] allows you to edit different agents or

[21:32] create a new one. So, I'll start off by

[21:33] just creating a new agent. I usually

[21:35] just do the current project. I will

[21:36] almost always do the generate with

[21:38] Claude. I took the deep research

[21:40] summary. I fed all that into here along

[21:42] with like a paragraph descriptor of

[21:44] exactly what I want the agent to do. And

[21:46] then I let Claude's um built-in process

[21:50] here go ahead and create the initial

[21:51] draft of the agent and then I took that

[21:54] draft which was just a markdown file in

[21:56] the Claude agents directory. But then

[21:59] what I did is I asked Claude code to go

[22:03] ahead and take the documentation from

[22:05] Anthropics website and to review and

[22:08] edit the agent markdown file in

[22:11] accordance to what the best practices

[22:14] lay out and those examples of other ones

[22:16] that I had to work with in order to

[22:17] really get a concise greatlooking

[22:19] document. So I did that exact flow for

[22:22] the slash commands, the agent as I just

[22:23] mentioned, and my uh cloud.md file. And

[22:26] I feel like that really helps you get

[22:28] concise, actionable workflows. By the

[22:31] way, if you are finding value in this

[22:33] YouTube video, it means a ton if you

[22:35] would give it a like and subscribe if

[22:37] you're interested in learning these new

[22:39] AI native workflows. And as a thank you,

[22:41] I will include in the description links

[22:43] to all of these files so that you can

[22:45] download them and reference them and use

[22:47] them as you wish. All right, so let's go

[22:48] ahead and look at our sub agent. Could

[22:50] you please look at the homepage on my

[22:53] website, the main page, and give me a

[22:55] detailed review as outlined in the agent

[22:59] review configuration?

[23:04] So, as you can see, that wasn't the best

[23:05] articulated prompt, but it's enough to

[23:07] get the agent to go ahead and

[23:09] proactively work. I've got here a window

[23:11] that was opened up, so it's identifying

[23:13] that we have the port in use. Okay,

[23:15] great. So, it went ahead and loaded my

[23:17] personal website. Here it is adjusting

[23:19] the screen size and it's grabbing

[23:21] screenshots in order to collect some UI

[23:24] context that it can bring back to see

[23:25] what it needs to fix. It's pretty

[23:27] surreal watching these work and your

[23:30] mind just starts to go a little wild

[23:32] thinking of all the applications that

[23:33] you could use for this to automate

[23:35] different parts of your workflow. I'm

[23:37] just thinking of all the time I spend

[23:38] doing mobile responsive testing and also

[23:41] the times I forget to do it in uh that

[23:43] ends up in a bug where this can just

[23:45] solve that because Claude can come back

[23:46] to us with a fully baked version. So in

[23:48] this case it's asking if it wants to go

[23:50] ahead and try submitting the email

[23:52] signup form that I have on my website.

[23:54] So I'll go ahead and say yeah. You can

[23:55] see it went ahead and typed in uh and

[23:58] subscribe to my newsletter just to get a

[24:00] sense of uh the context there for what

[24:03] it looks like which is just fantastic.

[24:05] Also, every time I click yes and don't

[24:07] ask me again, it will uh save that into

[24:09] my local file so that cloud code knows

[24:12] it can just go ahead and do these

[24:13] things. Another cool element with these

[24:15] is you can have the sub aents call other

[24:17] sub aents which is really helpful when

[24:19] it comes to creating a network of almost

[24:22] like conditional logic. So you could

[24:24] have one design reviewer invoke like a

[24:26] mobile designer for example and uh other

[24:29] reviewers and then in aggregate all of

[24:32] these have their own context and they

[24:33] use their own uh models. You can specify

[24:36] if it's sonnet or opus or or whatever

[24:38] model you want to use and because of

[24:40] that you don't cloud the main context of

[24:43] your your main thread in cloud code. So

[24:46] you can have a bunch of sub aents go do

[24:47] a bunch of work and summarize and bring

[24:49] back the executive report. for example,

[24:52] a list of to-dos that need to be

[24:53] changed, or in this case, a design

[24:55] review report. If you look over here,

[24:57] we've got the official report back from

[24:59] the design review agent. And it's got

[25:02] some uh some constructive feedback, an A

[25:05] minus. I'll uh I'll take it. Uh I don't

[25:07] claim to be an amazing designer. It's

[25:09] got here a few strengths that it lists

[25:11] out, some high priority issues to work

[25:13] on, multiple image preload warnings

[25:15] affecting performance. Okay, that's

[25:17] helpful to know. Third party script air

[25:18] from ptxcloud.net net and misconfigured

[25:22] metatag more subjective things too like

[25:24] newsletter iframe needs a better

[25:25] integration is a great example of where

[25:27] it's using the vision side of its neural

[25:30] net now of course this is a really basic

[25:32] example typically we're using this on

[25:34] much more meaningful or like new

[25:37] development you can imagine how getting

[25:39] this feedback and then having the model

[25:42] actually address the feedback creating

[25:43] that iterative loop is really powerful

[25:46] automatically addressing any errors or

[25:48] issues is helpful but in this case what

[25:50] I typically do is I would just invoke it

[25:54] uh saying like hey could you please

[25:56] address the above issues the you know

[25:59] everything within high priority or maybe

[26:00] I'd outline you know just a couple

[26:02] specifics that I want here but you can

[26:04] also chain these in different loops as I

[26:07] mentioned before with the sub agents

[26:09] that can call each other very powerful

[26:11] way to iterate agentically and

[26:14] automatically to a much better end

[26:16] result than what you get on just a first

[26:18] pull of cloud code one extra bonus I'll

[26:20] throw in for you is this idea of git

[26:23] work trees. So a big concept within

[26:25] using cloud code that I found to be an

[26:28] extremely big unlock is doing multiple

[26:31] things in parallel. You can work on

[26:33] different projects that don't interact

[26:35] with each other. That's nice. But I

[26:37] think another strategy that has been

[26:39] really helpful is trying to change my

[26:41] perspective to have much more of an

[26:43] abundance mindset. Not feeling like I'm

[26:45] wasting Claude's outputs by scrapping

[26:47] what it comes up with. Because these

[26:49] models are stochastic in nature, you get

[26:51] varied outputs upon each poll or each

[26:54] time you prompt it. That can be an issue

[26:56] or you can use that in your favor by

[26:59] running multiple of these at the same

[27:01] time. In order to do that, what I

[27:03] typically will do is I will use git work

[27:05] trees. So in this case, I've got another

[27:07] repository. If I go back here to Patrick

[27:10] to the root, I've got a second one which

[27:13] is two. And that is using a git work

[27:15] tree which is a way to very easily set

[27:17] up essentially a copy of your

[27:19] repository. So you can create multiple

[27:21] work trees and it's almost like you have

[27:22] three separate versions of your

[27:24] repository but it's all within one.git

[27:26] folder in your main repo and each one

[27:28] has its own branch. So in my case I've

[27:30] got Patrick Ellis IO2. I could kick off

[27:33] a cloud code in both of them and have

[27:35] them both iterate on some front-end

[27:37] changes and look at the two to kind of

[27:40] AB contrast which one I think looks the

[27:42] best and go from there. Typically, I'll

[27:44] do this with like three different

[27:46] prompts if I want to or the same prompt

[27:48] but kicked off in three different work

[27:49] trees in order to help get a variety of

[27:53] outputs. One of my friends took this to

[27:55] another level. it will actually kick off

[27:57] three different processes running in

[27:58] GitHub workers using headless cloud

[28:00] codes that will come up with three

[28:02] different outputs and then he'll use

[28:04] another model another opus to judge

[28:06] which of the three is the best. Another

[28:09] thing that I find is really powerful

[28:10] with these workflows is the ability to

[28:13] package up these processes that our team

[28:16] members use. So maybe we've got an

[28:17] excellent designer or an excellent

[28:19] engineering manager who's really good at

[28:21] code review or back-end architect or

[28:23] anything else. What's really neat is

[28:25] being able to package up their expertise

[28:28] into something like a sub agent or a

[28:30] slash command or even an MCP and

[28:33] distribute that across the team so that

[28:35] you can benefit without even knowing the

[28:37] nuances of the workflow from an expert

[28:40] designer. When it comes to providing the

[28:42] model's context in a prompt, I would

[28:44] highly recommend also including as many

[28:47] visual design elements as you can as

[28:49] screenshots. So dragging in things like

[28:51] even a lowfidelity sketch, kind of a UX

[28:54] wireframe that you want, or references

[28:57] to other designs, obviously a style

[28:59] guide if you have it, or a collection of

[29:01] different inspiration or kind of design

[29:04] board elements that you want to bring

[29:05] in. anything that you can use to channel

[29:07] the visual modality of the model's

[29:10] intellectual capacity in addition to all

[29:12] the coding details such as being able to

[29:15] specify front-end frameworks or best

[29:17] practices. Things like hex codes for

[29:19] colors and typography and everything

[29:21] else. Those two combined are very

[29:23] powerful. At the end of the day, the

[29:25] performance of these models comes down

[29:27] to context, tools, and validation steps.

[29:31] So, I hope that this overview of the

[29:33] tools and the validation side has been

[29:35] really helpful and actionable for you.

[29:37] Thank you so much for watching and stay

[29:39] tuned for more videos like this. In the

[29:41] meantime, if you enjoyed this video, I

[29:43] think you'll really enjoy my recent deep

[29:45] dive with my friends Anod and Galen at a

[29:48] Seattle founders group on all of our

[29:50] best practices for Claude Code. At least

[29:52] all that we could fit into our

[29:54] presentation. You can find that video

[29:55] above along with my most recent video.

