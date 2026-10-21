"""Codex-authored reviewable sample scripts. NOT the automatic writer backend."""
import json
from pathlib import Path
from stickfilm.schema import Plan,Scene,Actor,Cue,Prop,NICHES

# Narration, setting, action, prop, camera, editorial label. Each story has its
# own conflict and visual progression. These fixtures intentionally do not adapt
# arbitrary titles; the local model is responsible for that separate path.
STORIES=[
("The Deadline Has a Sofa", "A fictional office comedy about avoiding an intimidating assignment; no neuroscience claims.", [
("Milo has forty minutes to finish one page. He opens the document, takes a brave breath, and decides the desk needs cleaning first.","office","think","book","dolly-in","ONE PAGE. FORTY MINUTES."),
("The desk was already clean. That is inconvenient. Luckily, his phone has discovered a video about a man organizing an even cleaner desk.","office","reach","phone","over-shoulder","VERY IMPORTANT RESEARCH"),
("Across the room, his friend Ada asks what the assignment actually needs. Milo describes it as an enormous, shapeless mountain of professional doom.","abstract","fear","box","wide","THE MOUNTAIN"),
("Ada gives the mountain a name. Write the first sentence. Suddenly the monster is small enough to fit inside a very ordinary box.","abstract","inspect","box","reveal","MAKE THE NEXT MOVE SMALL"),
("Milo reaches for the box, then hesitates. What if the sentence is bad? Ada points out that the current sentence is exceptionally invisible.","office","hesitate","book","close-up","THE INVISIBLE FIRST DRAFT"),
("He types a terrible sentence. Nothing explodes. He writes another. The little plant beside his screen receives less attention, but the page receives more.","office","point","plant","dolly-out","NOTHING EXPLODED"),
("His phone lights up again. Milo moves it across the room. The phone remains fascinating. It is simply fascinating somewhere he cannot reach without standing.","office","walk","phone","follow","LET TEMPTATION TAKE THE LONG WAY"),
("The page is not perfect. It exists. With five minutes left, Milo finally cleans the desk. This time, there is something on it worth keeping.","office","happy","book","wide","A PAGE THAT EXISTS")]),
("The Queue for Absolutely Nothing", "An original escalating comedy about two friends and an unexplained queue.", [
("Ada finds Milo standing in a queue. What are we waiting for? she asks. No idea, he says. But the man ahead looks extremely confident.","city","think","flag","establishing","IT MUST BE SOMETHING GOOD"),
("The queue advances one step. Everyone looks relieved. Nobody has received anything, but movement feels like progress, and progress deserves a small celebration.","city","walk","flag","tracking","ONE WHOLE STEP"),
("A businessperson arrives with a clipboard. How long is the wait? Milo says twenty minutes. He has been here three, but twenty sounds professionally disappointing.","city","point","book","over-shoulder","A HIGHLY QUALIFIED GUESS"),
("Ada walks to the front. There is a box. Inside the box is a sign. The sign says please keep this doorway clear at all times.","city","pickup","box","reveal","THE BIG REVEAL"),
("She carries the evidence back. Milo studies it carefully. Perhaps, he suggests, the queue is waiting for somebody to move the box out of the doorway.","city","inspect","evidence","close-up","A SECOND THEORY"),
("Ada moves the box. Everyone follows her. She stops. They stop. She takes one cautious step sideways. The entire queue takes one cautious step sideways.","city","walk","box","pan","CONGRATULATIONS. YOU ARE THE FRONT."),
("Ada finally announces that there is no queue. People nod respectfully, then ask whether they need a reservation for the next available no queue.","city","frustrated","phone","wide","RESERVATIONS ARE CLOSED"),
("Milo and Ada leave for lunch. Behind them, somebody places the empty box beside the wall. One man stops to look. Another man stands behind him.","restaurant","happy","box","dolly-out","SOMEWHERE, A NEW QUEUE BEGINS")]),
("The Shop That Sold Its Lunch", "A fictional small-business cash-flow story using simple invented transactions, not financial advice.", [
("Milo sells his first handmade notebook. He holds the coin like a tiny golden trophy. At last, he says, the shop is making money.","bank","happy","coin","dolly-in","THE FIRST SALE"),
("Ada asks about the paper. Milo points to a receipt. The binding? Another receipt. The delivery? He produces a third receipt with considerably less ceremony.","office","inspect","book","reveal","A SALE HAS COMPANY"),
("The coin is real. So are the costs. Their imaginary shop has sold something, but that does not mean every coin in the drawer belongs to lunch.","bank","think","coin","close-up","REVENUE IS NOT THE WHOLE STORY"),
("Milo makes three boxes. One holds money for supplies. One holds money for other bills. The last holds what remains after this little example's costs.","office","pickup","box","wide","GIVE EVERY COIN A JOB"),
("Then a customer promises to pay next week. Milo celebrates another sale. Ada points at the empty drawer. A promise cannot buy paper at the counter today.","bank","surprise","box","over-shoulder","SOLD TODAY. PAID LATER."),
("They write the payment date beside the supplier's deadline. The dates do not match. Their problem has moved from how much to when it arrives.","office","point","clock","reveal","TIMING CHANGES THE PICTURE"),
("For this fictional shop, they choose a smaller order they can pay for now. There is less impressive stacking, and considerably less panicked running between counters.","bank","walk","book","follow","SMALLER CAN BE MORE MANAGEABLE"),
("At closing time, Milo buys lunch with money they have actually set aside. The notebook business is still tiny. His understanding of the drawer is larger.","restaurant","happy","coin","dolly-out","COUNT WHAT REMAINS. CHECK WHEN IT ARRIVES.")]),
("A Courier, Two Borders, One Missing Stamp", "Clearly fictional historical-inspired border story; no real war, country, date or event is represented.", [
("In an invented border town, a courier named Ada carries a letter that must arrive before the bridge closes. The envelope looks disappointingly ordinary.","battlefield","walk","book","establishing","A FICTIONAL BORDER TALE"),
("At the first checkpoint, a guard asks for a blue stamp. Ada has a red one. The guard explains that red stamps are perfectly valid, elsewhere.","city","hesitate","flag","over-shoulder","VALID. SOMEWHERE ELSE."),
("She visits the office beside the gate. It needs a signature from the office across the bridge. That office, she discovers, needs permission from this gate.","office","frustrated","door","pan","THE MAP HAS BECOME A CIRCLE"),
("The letter is not a secret military order. It is a request to reopen the town's shared water pump. Both sides have been carrying buckets all morning.","city","inspect","water","reveal","ONE PUMP. TWO SIDES."),
("Ada stops arguing about the envelope and points to the water. The guard's boots are wet. His own family has been using the same broken pump.","battlefield","point","water","close-up","A SHARED PROBLEM"),
("He cannot erase the border. He can summon the clerk. The clerk cannot fix the pump. She can send the maintenance request through the correct office.","office","exchange","book","wide","SMALL POWERS, USED TOGETHER"),
("The bridge bell rings as Ada crosses. She has not defeated a kingdom. She has found a person willing to carry one useful piece of the problem.","city","run","clock","tracking","BEFORE THE GATE CLOSES"),
("That evening, two neighbors meet beside the pump with tools. Our invented town still has two borders on its map. It finally has one conversation at the water.","city","happy","water","dolly-out","FICTION. NOT A HISTORICAL ACCOUNT.")]),
("The Island with One Excellent Plan", "A fictional survival scenario; entertainment, not emergency survival instructions.", [
("Milo wakes on an imaginary island with a box, a bottle, and the confidence of somebody who has watched exactly half a survival documentary.","island","surprise","box","establishing","AN IMAGINARY ISLAND"),
("His first plan is enormous. Build a boat, sail home, open a restaurant, and name the soup after this experience. Ada asks about the next hour.","island","excited","water","dolly-in","THE PLAN IS VERY LARGE"),
("They inspect what they actually have. The bottle holds a little water. The box holds a book. The book is about organizing meetings. This feels personal.","island","pickup","book","reveal","INVENTORY HAS ENTERED THE CHAT"),
("A dark cloud slides across the shore. Milo begins a dramatic speech about courage. Ada moves the box under cover and asks him to help carry it.","island","walk","box","tracking","THE WEATHER DOES NOT WAIT FOR SPEECHES"),
("In their fictional predicament, useful work starts smaller than the grand escape. They mark where they landed, keep their things together, and agree to stay together.","island","point","flag","wide","MAKE THE SITUATION EASIER TO UNDERSTAND"),
("Milo spots something bright beyond the trees and starts running. Ada calls him back. A mysterious sparkle is not yet evidence that help is waiting there.","forest","run","evidence","follow","HOPE STILL NEEDS A SECOND LOOK"),
("The sparkle is a second bottle. Empty. Milo looks defeated, then notices the cap fits their first bottle. Even a small discovery can change the next decision.","island","inspect","water","close-up","SMALL DOES NOT MEAN USELESS"),
("Their story ends before a rescue arrives. The soup restaurant remains imaginary. What changed is their plan: fewer heroic speeches, more checking what the next step needs.","island","think","box","dolly-out","A STORY ABOUT DECISIONS, NOT A SURVIVAL GUIDE")]),
("The Box Nobody Wanted to Carry", "An original fictional short about accepting help, with an emotional payoff.", [
("Every morning, Milo carries a box across the courtyard. Every morning, Ada offers to help. Every morning, he says it is lighter than it looks.","city","walk","box","tracking","LIGHTER THAN IT LOOKS"),
("One wet afternoon, he sits beside it instead. The box has not grown. His arms simply have no impressive explanation left to give the pavement.","city","sit","box","dolly-in","AN ORDINARY BAD AFTERNOON"),
("Ada sits nearby without asking what is inside. Milo tells her anyway. Old drawings. Unfinished ideas. A letter he never sent. Things he meant to sort out.","city","sad","book","close-up","THE THINGS WE KEEP"),
("She does not offer a speech. She asks where the box needs to go. Milo points to a little room on the far side of the courtyard.","city","point","door","over-shoulder","WHERE DOES IT NEED TO GO?"),
("They each take one side. The box tips, and a drawing slips out. It shows the courtyard years earlier, before the tree was taller than the roof.","city","pickup","book","reveal","SOMETHING WORTH KEEPING"),
("Ada recognizes the tree. Milo recognizes the tiny figure he drew beside it. For a moment, neither of them tries to make the afternoon useful.","forest","think","plant","wide","A MOMENT WITHOUT AN ANSWER"),
("They carry the box into the room. Nothing inside has been solved. The letter remains unsent. The difference is smaller, and perhaps more believable than that.","city","walk","box","follow","ONE SIDE EACH"),
("The next morning, Ada arrives carrying a box of her own. Milo starts to ask whether it is heavy. Then he takes one side and asks where they are going.","city","happy","box","dolly-out","WHERE ARE WE GOING?")]),
("Gravity Did Not Read Your Schedule", "A fictional laboratory demonstration of gravity. Simplified physics; no invented measurements.", [
("In our imaginary laboratory, Milo tells a ball to wait until he finishes his presentation. The ball declines to comment and heads toward the floor.","laboratory","surprise","ball","dolly-in","GRAVITY IS NOT TAKING APPOINTMENTS"),
("Ada explains that Earth's gravity pulls objects toward Earth. Holding the ball up requires a supporting force. Removing that support changes what happens next.","laboratory","point","planet","wide","REMOVE THE SUPPORT"),
("Milo offers a heavier ball a stern warning. Weight changes how hard he must hold it, but a warning is still not a force in his diagram.","laboratory","frustrated","ball","close-up","A WARNING IS NOT A FORCE"),
("For an ideal comparison, Ada asks us to imagine no air resistance. Objects dropped together from rest share the same gravitational acceleration at the same location.","abstract","think","planet","reveal","AN IDEALIZED COMPARISON"),
("A sheet of paper in real air complicates the experiment. Air pushes back as objects move through it. Shape and orientation can change that resistance considerably.","laboratory","inspect","book","over-shoulder","THE AIR JOINS THE EXPERIMENT"),
("That is why a useful demonstration says what it leaves out. Our drawings simplify size and time. They illustrate the question, rather than supplying measured experimental data.","laboratory","point","clock","pan","A MODEL HAS LIMITS"),
("Milo finally places the ball on a stand. It stays there. Gravity has not switched off. The support now supplies a force that balances the downward pull.","laboratory","reach","ball","wide","STILL DOES NOT MEAN FORCE-FREE"),
("He bows. The presentation is finished. The ball rolls off the stand, and Milo discovers one final principle: it helps to watch your own demonstration.","laboratory","surprise","ball","dolly-out","WATCH THE DEMONSTRATION")]),
("The Two-Minute Door", "A fictional practical habit story; no promised health or productivity outcomes.", [
("Milo buys a beautiful notebook for his new morning routine. On the first page, he writes become a completely different person. Then he closes it, exhausted.","bedroom","sad","book","dolly-in","AN AMBITIOUS FIRST PAGE"),
("Ada asks what a different person would actually do tomorrow. Milo describes twelve impressive habits and a breakfast that requires considerably more washing up than breakfast should.","restaurant","excited","book","wide","TWELVE HABITS. ONE MORNING."),
("They choose one small action instead. Put on shoes and step outside. The notebook objects by looking expensive, but it does not get a vote.","bedroom","point","door","reveal","ONE OBSERVABLE ACTION"),
("The next morning, Milo stands at the door. He does not feel transformed. He feels like Milo, wearing shoes, with an unusually demanding relationship to a handle.","bedroom","hesitate","door","close-up","STILL MILO. NOW WITH SHOES."),
("He opens it and walks down the path. The walk is short. There is no montage of instant success, because this story has only reached Tuesday.","forest","walk","plant","follow","IT IS ONLY TUESDAY"),
("On Wednesday he forgets. He almost crosses out the entire plan. Ada points to Thursday, which remains stubbornly available despite Wednesday's disappointing performance.","office","frustrated","clock","over-shoulder","THURSDAY IS STILL AVAILABLE"),
("He leaves the shoes beside the door. For Milo, that makes the next choice easier to notice. It is an experiment in his own routine, not a universal guarantee.","bedroom","reach","door","wide","DESIGN FOR THE NEXT TRY"),
("A week later, the notebook has one ordinary sentence on its first page. Open the door. Milo reads it, puts on his shoes, and goes to see what is outside.","forest","happy","book","dolly-out","OPEN THE DOOR")]),
("The Password Guard Took a Day Off", "Fictional cybersecurity metaphor grounded in CISA guidance about MFA and phishing.", [
("Milo guards a digital doorway with one password. He has made it very long. He is delighted. Across the corridor, Ada asks what happens if somebody steals it.","digital","point","door","dolly-in","ONE LOCK. ONE SECRET."),
("Milo adds a second copy of the same password. Ada looks at him. Two identical secrets do not become two independent checks just because you write them twice.","digital","embarrassed","book","close-up","A COPY IS STILL A COPY"),
("Multi-factor authentication asks for another kind of proof. A password plus an appropriate authenticator can make an account harder to enter with only a stolen password.","digital","shield","lock","reveal","ANOTHER KIND OF PROOF"),
("Then an urgent message arrives. Your account expires in four minutes. Click here immediately. Milo starts running toward the button before he has checked who sent it.","digital","run","phone","tracking","URGENCY IS NOT EVIDENCE"),
("Ada stops him beside the doorway. Unexpected links deserve a pause. They open the service through a known route instead of trusting the message's convenient little shortcut.","digital","hesitate","door","over-shoulder","TAKE A KNOWN ROUTE"),
("The service reports no emergency. The message was our fictional attacker's invitation to hand over access. A convincing-looking request was still only a request.","digital","inspect","evidence","wide","THE STORY THE MESSAGE WANTED TO TELL"),
("MFA is useful protection, not a magic shield against every attack. The method matters. Some options resist phishing better than codes that people can accidentally share.","digital","think","lock","pan","PROTECTION HAS LEVELS"),
("Milo keeps the long password, enables the strongest available MFA, and reports the message. The doorway is quieter now. He spends the saved four minutes having lunch.","restaurant","happy","lock","dolly-out","PAUSE. CHECK. PROTECT.")]),
("The Mystery of the Guaranteed Prize", "A fictional scam investigation grounded in FTC prize-scam guidance; invented people and incident.", [
("Ada receives a message saying she has won a magnificent prize. There is just one small delivery fee. She cannot remember entering a competition. The message seems untroubled.","office","surprise","phone","dolly-in","A PRIZE SHE NEVER ENTERED TO WIN"),
("Milo spots a gold badge on the screen. Official, he says. Ada draws the same badge on a box. The box does not immediately become a government department.","office","inspect","box","close-up","A BADGE IS EASY TO DRAW"),
("They list the claims. A prize exists. The sender controls it. Payment will release it. So far, every piece of evidence came from the person asking for money.","abstract","point","evidence","reveal","FOLLOW THE SOURCE OF THE CLAIM"),
("A second message arrives. Pay now or lose everything. The prize has become more urgent without becoming more verified. Milo puts his hand back in his pocket.","office","fear","clock","over-shoulder","THE DEADLINE IS DOING THE SELLING"),
("Ada checks the alleged organization through contact details she finds independently. She does not call the number supplied in the suspicious message and ask the sender to verify itself.","office","reach","phone","wide","CHECK OUTSIDE THE MESSAGE"),
("In our invented case, the organization knows nothing about the offer. The supposed delivery fee was the product. The magnificent prize was merely its advertising.","abstract","surprise","coin","reveal","THE FEE WAS THE PRODUCT"),
("The FTC warns that real prizes do not require payment to collect them. Unexpected prize claims asking for money or sensitive information deserve suspicion, not a rushed transfer.","office","shield","lock","pan","A VERIFIED WARNING"),
("Ada reports and deletes the message. Milo keeps the decorated box. It now contains their receipts, which are less magnificent than a prize and considerably more likely to exist.","office","happy","box","dolly-out","MYSTERY SOLVED. WALLET INTACT.")])]

def main():
    root=Path(__file__).resolve().parents[1]
    for index,(title,brief,rows) in enumerate(STORIES):
        scenes=[]
        for i,(words,env,action,prop,cam,label) in enumerate(rows):
            beat=['hook','setup','progression','discovery','conflict','progression','discovery','payoff'][i]
            actor=Actor(action=action,x=490 if action not in ('pickup','reach','inspect') else 940,travel=360 if action=='walk' else 520 if action=='run' else 0,
                character='scientist' if index==6 else 'business' if index==2 else 'hero',facing=1)
            actors=[actor]
            if i in (2,4,7) and index!=4:actors.append(Actor(character='friend',action='think' if i!=7 else 'happy',x=1210,depth=.87,facing=-1))
            mood=['curious','comic','curious','tense','tense','warm','wonder','warm','curious','tense'][index]
            kind='click' if prop=='phone' else 'pickup' if action=='pickup' else 'chime' if i==7 else 'tick'
            scenes.append(Scene(id=f's{i+1:02}',beat=beat,narration=words,environment=env,actors=actors,prop=prop,camera=cam,label=label,
                music=mood,transition='dissolve' if i in (3,7) else 'cut',lighting='dramatic' if index in (3,9) and i<6 else 'day',
                pause=.55 if index in (1,5,9) else .35,cues=[Cue(at=.52,kind=kind,gain=.2)]))
        # Explicit visual direction: props have ground/hand anchors and timed
        # motion. This is authored sample staging, not a generic AI capability.
        if index==0:
            scenes[0].prop="none";scenes[0].actors[0].x=790;scenes[0].actors[0].action="sit"
            scenes[0].props=[Prop(kind="chair",x=790,y=710),Prop(kind="desk",x=1040,y=710),Prop(kind="laptop",x=1040,y=590,scale=.8)]
            scenes[2].prop="mountain"
        if index==1:
            for z in (0,1,2):
                scenes[z].actors.append(Actor(character="crowd",action="idle",x=250,depth=.9))
        if index==2:
            scenes[1].prop="none";scenes[1].actors[0].x=620;scenes[1].actors[0].action="point"
            scenes[1].props=[Prop(kind="receipt",x=930+j*130,y=710,label=label) for j,label in enumerate(["PAPER","BINDING","DELIVERY"])]
            scenes[3].prop="none";scenes[3].actors[0].x=540;scenes[3].actors[0].action="point"
            scenes[3].props=[Prop(kind="box",x=850+j*180,y=710,label=label) for j,label in enumerate(["SUPPLIES","BILLS","REMAINS"])]
        if index==3:
            for z in (0,6):
                scenes[z].prop="none";scenes[z].props=[Prop(kind="letter",x=0,y=0,scale=.45,attach_to="right-hand")]
            scenes[3].prop="pump";scenes[7].prop="pump"
        if index==4:
            scenes[1].prop="boat";scenes[2].props=[Prop(kind="bottle",x=1200,y=710)]
            scenes[3].props=[Prop(kind="umbrella",x=820,y=660,scale=1.3)]
        if index==5:
            for z in (0,6):
                scenes[z].prop="none";scenes[z].props=[Prop(kind="box",x=5,y=25,scale=.65,attach_to="right-hand")]
        if index==6:
            scenes[0].prop="none";scenes[0].props=[Prop(kind="ball",x=1040,y=500,motion="drop",travel_y=210,start_at=.2,end_at=.60)]
            scenes[3].prop="none";scenes[3].props=[Prop(kind="ball",x=990,y=470,motion="drop",travel_y=240,start_at=.15,end_at=.7),Prop(kind="ball",x=1150,y=470,motion="drop",travel_y=240,start_at=.15,end_at=.7,scale=.7)]
            scenes[6].prop="none";scenes[6].props=[Prop(kind="desk",x=1040,y=710),Prop(kind="ball",x=1040,y=590)]
            scenes[7].prop="none";scenes[7].props=[Prop(kind="desk",x=1040,y=710),Prop(kind="ball",x=1040,y=590,motion="drop",travel=190,travel_y=120,start_at=.25,end_at=.65)]
        if index==7:
            scenes[2].prop="shoe";scenes[3].props=[Prop(kind="shoe",x=830,y=710)]
            scenes[6].prop="door";scenes[6].props=[Prop(kind="shoe",x=950,y=710)]
            scenes[7].prop="door";scenes[7].prop_motion="open"
        # No arbitrary tick under every sentence: reserve foley for visible events.
        for sc in scenes:
            if sc.prop=="clock":sc.cues=[Cue(at=.52,kind="tick",gain=.2)]
            elif sc.prop=="phone":sc.cues=[Cue(at=.52,kind="click",gain=.2)]
            elif sc.actors[0].action=="pickup":sc.cues=[Cue(at=.52,kind="pickup",gain=.2)]
            elif sc.beat=="payoff":sc.cues=[Cue(at=.55,kind="chime",gain=.18)]
            else:sc.cues=[]
        sources=[]
        if index==6:sources=[{'url':'https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/free-falling-objects/','claim':'In the absence of air resistance, free-fall acceleration does not depend on mass; drag changes real trajectories.'}]
        if index==8:sources=[{'url':'https://www.cisa.gov/secure-our-world/turn-mfa','claim':'MFA adds authentication protection; phishing-resistant MFA offers stronger protection than some other methods.'},{'url':'https://www.cisa.gov/secure-our-world/recognize-and-report-phishing','claim':'Recognize suspicious urgent messages, avoid suspicious links, and report phishing.'}]
        if index==9:sources=[{'url':'https://consumer.ftc.gov/articles/fake-prize-sweepstakes-and-lottery-scams','claim':'Real prizes are free; requests for money to collect an unexpected prize are a scam warning.'}]
        plan=Plan(title=title,brief=brief,niche=NICHES[index],requested_minutes=1.25,provenance='authored-example',factual_status='source-grounded' if sources else 'fiction',sources=sources,scenes=scenes)
        (root/'examples/plans'/f'{index:02}.json').write_text(plan.model_dump_json(indent=2))
        print(index,plan.title,sum(len(s.narration.split()) for s in scenes),'words')

if __name__=='__main__':main()
