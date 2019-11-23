# Halo
BitHalo/BlackHalo/BitBay/Bitmessage public commit

The first commit of Halo contains BitMHalo. This is a custom Bitmessage implementation for running messaging and decentralized markets
in Halo. This is basically the backbone of communication and it is how the markets and communication are kept private and serverless.

BitMHalo for now, uses a series of locking files. BitTMP is what Halo generates with the current command. Other commands are held in a file and this is done without making RPC calls to avoid losing pending commands. There is a more efficient way to do that but until a Halo refactor is done then this is the protocol. So Halo (either BitHalo/BlackHalo/BitBay) must be running for BitMHalo to have any use. This can be made more object oriented and logic separated. Also we could use more threads. It should be noted that Bitmessage doesn't behave properly when run outside of the main thread. This is why the decision was made for it to have it's own binary. Also this helps when permissions are being asked for an entirely separate P2P protocol.

Various things could be improved. Email fetching is slow especially when backlogged. UIDs are saved in a file and sent manually to the
program to avoid reading emails twice. Also encrypted emails can be deleted to prevent bulking things up when a private key is passed.
The program also communicates via RPC to tell Halo if it's doing something to detect when an email provider times out. Unfortunately
IMAP has no good way of signaling this. So there is a timed section that simulates this including an RPC call to Halo to decide if it
needs to be reset. Failed emails get moved to an outbox and sent until things succeed. There is not enough catches for email authentication errors in case a user changes locations. Bitmessage can end up getting tons of messages and there is an eventual clearing of old messages but it's account specific. This is because many accounts might share the same BitMHalo. There is a custom data directory for BitMHalo so keys are stored locally. It is worth noting that Halo should probably encrypt that file with a password or at least give the option so that private Bitmessage keys and subscriptions are not made easy to see. Although, the best security would be to simply have it installed on an encrypted hard drive. BitMHalo manages your inbox automatically. However the checking of emails might be compulsive and redundant. Realize an email might be shared by multiple Halo accounts and in some cases only one account decrypts it. Currently emails are cached in a file so it's a bit faster. It would be nice to add some efficient database management to Halo like MongoDB or something. Also it would be good to add more email providers. Great care must be taken because we have pay to email and we don't want email providers compressing steganography images. One fix is to send those as an attachment but the user experience is not as fun because sometimes those are shown twice as attachment and inline or not shown at all. This is why we send those pay to emails inline as base64 images with secret data burned in the pixels. I've considered adding the option for user to send inline or attachment. We should know in advance if we add email providers how they compress inline images or attachments. Also some providers had restrictions on IMAP and we need to know that in advance before adding them.

Bitmessage itself is perfect for decentralized markets. It is serverless since nodes hold messages. Nodes that can decrypt a message will do so. A message "hops" from user to user to prevent knowledge of the original sender. Although a botnet could probably gain statistics on an IP address and guess who the original sender is. However that attack is unproven. There is also some discussion on security on Bitmessage forums worth reading. Regardless, it's almost impossible to prove a user holds a decryption key for a specific channel as the nodes themselves are usually unaware of the traffic they are routing. This is superior to any blockchain implementation I'm aware of because in a blockchain the person broadcasting is known. Similar hopping logic can be added to a blockchain though and combined with some sort of DPOS system however that is pseudo-centralized. Also the bitmessage network is large and not restricted to one single project. This addition of nodes is what is needed for decentralized internet. Further improvements to Bitmessage itself is of particular interest to computer science. Various sharding techniques, massive servers, etc.

Potential improvements to Bitmessage:
Compare to the main branch as it has been updated. However any changes must work with pyinstaller (I found the newer changes to be a bit tricky to build) Also one drawback of Bitmessage is dropping messages. If for example a node disconnects for a few days, Bitmessage has
a protocol to send that message again. The problem is they skip days. And then they do so exponentially. This is probably to reduce proof of work on nodes that will never connect. However we had to change this code because we cannot afford message loss under any circumstances. In our branch messages are resent every 48 hours if not acknowledged. Any merging with the new branch must keep this in consideration. Message loss must never happen. Halo could track it, but Bitmessage itself should track it.

Bitmessage should give users a way to not have to decrypt and download everything.

Another improvement of Bitmessage is to give the OPTION to allow users to forgo "Proof of work" if they pay a time locked payment
back to themselves using checklocktimeverify. They can pay per kilobyte. This is a good system to prevent spam. Basically
because Bitmessage does a POW. However that POW is too easy for a c++ implementation of Bitmessage or an ASIC. And it's too
hard for consumer grade computers that are old taking them 10 minutes for a big message. The checklocktimeverify option
would connect Bitmessage to a blockchain and have it make an RPC call to verify the transaction(with hash of message) as long
as the signature matches the signature of the public key or public keys involved in the spending of the timelock. The timelock
only freezes funds for a small amount of time to prevent SPAM attacks. Thus the network can scale. Also it would be interesting
to subdivide the traffic on the network based on what is subscribed to and set a limit for subscribers so the network can
compartmentalize and scale and nodes can know what to subscribe to in case of needing to search public channels. Various blockchains
can be used for this proof of timelock method potentially. A protocol would have to be in place if a node chooses not to check
that chain. Or perhaps online explorers can be used however we don't want that to get abused to drain a nodes resources.

Further commits to this branch will probably separate these comments to another file and the readme will be about building and using Halo!

To build this, there is an SH and BAT file for installing dependencies. Notice some of those are Halo dependencies.
Halos obfuscated source code can be found at:
https://bithalo.org/bithalo.github.io/bithalo/downloads/BitHaloSource.html

That link contains the full Halo source with variable names changed. It also has building instructions and binaries.

This branch for now contains BitMHalo. This can be build static with the script or run directly from Python. Halo itself uses
Python 2.711. It's untested with Python 3. Halo also uses PyQT4. To build BitMHalo simply install Python and run the scripts.
