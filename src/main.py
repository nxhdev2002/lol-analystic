from __facebookToolsV2 import dataGetHome, fbTools
from __messageListenV2 import listeningEvent  # Import the specific class or module you need
import os, json, threading

# Import Command Handler
from commands import CommandHandler

# Import RabbitMQ Publisher
from publishers import MessagePublisher
 
class fbClient:
    def __init__(self, cookies, dataFB, enable_rabbitmq=True):
        self.cookies = cookies
        self.dataFB = dataFB
        self.messageID = None
        self.prefix = "/" # This is the command prompt; when you enter this symbol, the corresponding command will be invoked. Additionally, you can customize it as per your preference (e.g., , . * ! ? etc)
        self.pathFile = ".mqttMessage"
        self.typeAttachment = None
        self.attachmentID = None
        self.typeChat = None # Change this value if you want to send the message to a user instead of a group. If you want to send it to a user, replace it with the value: 'user'
        self.recentReceivedMessages = []
        self.command_handler = CommandHandler()
        
        # Initialize RabbitMQ Publisher
        self.enable_rabbitmq = enable_rabbitmq
        self.message_publisher = None
        if self.enable_rabbitmq:
            try:
                self.message_publisher = MessagePublisher()
                print("RabbitMQ MessagePublisher initialized successfully")
            except Exception as e:
                print(f"Failed to initialize RabbitMQ MessagePublisher: {e}")
                self.enable_rabbitmq = False

    def setDefaultValue(self):
        self.userID, self.bodyMessage, self.replyToID, self.bodySend, self.commandPlugins, self.typeChat, self.attachmentID, self.typeAttachment= [None] * 8

    def receiveCommandAndSend(self):
        if (self.dataFB["FacebookID"] != self.userID):
            # Execute command asynchronously using the command handler
            # This allows multiple commands to be processed in parallel
            future = self.command_handler.execute_command_async(
                self,
                self.dataFB,
                self.commandPlugins,
                self.replyToID,
                self.typeChat
            )
            
            # Reset default values immediately - command runs in background
            self.setDefaultValue()

    def prefixCheck(self):
        if self.bodyMessage[0] == self.prefix:
            self.commandPlugins = self.bodyMessage.split(self.prefix)[1]
        else:
            self.commandPlugins = self.bodyMessage
          

    def receiveMessage(self):
        self.fbt = fbTools(self.dataFB, 0)
        # Pass the message_publisher to listeningEvent if RabbitMQ is enabled
        publisher = self.message_publisher if self.enable_rabbitmq else None
        mainReceiveMessage = listeningEvent(self.fbt, self.dataFB, publisher=publisher)  # Use the specific class or module you imported
        mainReceiveMessage.get_last_seq_id()
        threading.Thread(target=mainReceiveMessage.connect_mqtt, args=()).start()
        """
        Why am I using Threading here? 
        Because when calling connect_mqtt(), the programs after it won't be able to run 
        as it continuously connects to the Facebook server. To overcome this, I've used threading 
        to make it run concurrently with other functions!
        """
        while 1:
           if os.path.isfile(self.pathFile):
               try:
                   self.bodyMain = json.loads(open(self.pathFile, "r", encoding="utf-8").read())
                   # print(f"{self.bodyMain['messageID']} != {self.messageID} {self.bodyMain['messageID'] != self.messageID}")
                   if self.bodyMain['messageID'] != self.messageID:
                       self.userID = self.bodyMain['userID']
                       self.messageID = self.bodyMain['messageID']
                       self.bodyMessage = self.bodyMain['body']
                       self.replyToID = self.bodyMain['replyToID']
                       msg_type = self.bodyMain['type']
                       print(f"> userID: {self.userID}\n> messageID: {self.messageID}\n> messageContents: {self.bodyMessage}\n> From {msg_type}ID: {self.replyToID}\n- - - - -")
                       if (msg_type != 'thread'): self.typeChat = 'user'
                       
                       # Publish message to RabbitMQ if enabled
                       if self.enable_rabbitmq and self.message_publisher:
                           try:
                               self.message_publisher.publish_from_dict({
                                   "message_id": self.messageID,
                                   "user_id": self.userID,
                                   "sender_id": self.userID,
                                   "body": self.bodyMessage,
                                   "reply_to_id": self.replyToID,
                                   "type": msg_type,
                                   "attachments": []
                               })
                           except Exception as e:
                               print(f"Failed to publish message to RabbitMQ: {e}")
                       
                       self.prefixCheck()
                       self.receiveCommandAndSend()
                       self.setDefaultValue()
               except: # If nothing happens, please replace 'except' with 'finally' to check for errors.
                   pass
                   

cookies = "datr=n9JwaeO-9KMyRnM0R5yuBYBL; sb=n9JwaYott_8zwPUyChc_nFwA; locale=vi_VN; ps_l=1; ps_n=1; c_user=100014184491456; wd=1920x919; xs=38%3A1G_1GqQl7Cp15Q%3A2%3A1769655891%3A-1%3A-1%3A%3AAcxYNMU0Mtm5_aCjLCyN45B54d-gS-cn1g9ZxYujHA; fr=1s84sNN4irKFgmgMy.AWfTFMacanCttM1hDCtVJiYcvyx3TTNHqOXg64R3etn1OdIE_-k.Bpe3ho..AAA.0.0.Bpe3o1.AWcMBxLpxHAPvisnMw3nj91tTOo; presence=C%7B%22lm3%22%3A%22g.845664565142543%22%2C%22t3%22%3A%5B%5D%2C%22utc3%22%3A1769699896085%2C%22v%22%3A1%7D"
dataFB = dataGetHome(cookies)
print(dataFB)
_ = fbClient(cookies, dataFB)
_.setDefaultValue()
_.receiveMessage()
print("done!")

""" > A Message from Our Hearts to Our Users < 

Dear Users,

I'm Huy, the owner of the fbchat-v2 project. I'm truly grateful for your time using/reading my project. 
Although it was completed in a short time, I've refined it through numerous tests and 
bug fixes based on user reports, which I greatly appreciate.
Therefore, if you encounter any errors in the project, please report them in the issue section of this repository!
I'd be very thankful for that. Let's be smart and conscious users. Love you all <3

- A note about this source code (main.py): 
It's just a template/sample code to demonstrate:
  + Receiving messages
  + Sending messages
  + Receiving commands from users
  + Sending images
Besides the above, fbchat-v2 has many other powerful features. Please refer to the instructions in DOCS.md to learn how to use them.

"""