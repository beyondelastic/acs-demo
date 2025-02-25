using Azure.Communication;
using Azure.Communication.Sms;

// initialize an SmsClient with your connection string.

string connectionString = <your-connection-string>;
SmsClient smsClient = new SmsClient(connectionString);

// Replace <leased-phone-number> with an SMS-enabled phone number you provisioned via ACS, and <to-phone-number> with the phone number you wish to send a message to.

smsClient.Send(
   from: new PhoneNumber("<leased-phone-number>"),
   to: new PhoneNumber("<to-phone-number>"),
   message: "Hello World via SMS"
);