import { CallClient } from "@azure/communication-calling";
import { AzureCommunicationTokenCredential } from '@azure/communication-common';

const userToken = document.getElementById("token-input"); 
const submitToken = document.getElementById("token-submit");

const calleeInput = document.getElementById("callee-id-input");

const callButton = document.getElementById("call-button");
const hangUpButton = document.getElementById("hang-up-button");

let call;
let callAgent;
let tokenCredential;

submitToken.addEventListener("click", async () => {
    const callClient = new CallClient();
    const userTokenCredential = userToken.value;
  
    try {
      tokenCredential = new AzureCommunicationTokenCredential(userTokenCredential);
      callAgent = await callClient.createCallAgent(tokenCredential);
      callAgent.on('incomingCall', incomingCallHandler);
  
      callButton.disabled = false;
      submitToken.disabled = true;
    } catch(error) {
      window.alert("Please submit a valid token!");
    }
  });

  callButton.addEventListener("click", () => {
    // start a call
    const userToCall = calleeInput.value;
    call = callAgent.startCall(
      [{ id: userToCall }],
      {}
    );
  
    // toggle button states
    hangUpButton.disabled = false;
    callButton.disabled = true;
  });

  hangUpButton.addEventListener("click", () => {
    // end the current call
    call.hangUp({ forEveryone: true });
  
    // toggle button states
    hangUpButton.disabled = true;
    callButton.disabled = false;
  });

  const incomingCallHandler = async (args) => {
    const incomingCall = args.incomingCall;
  
    // Accept the call
    await incomingCall.accept();
  
    // Subscribe to callEnded event and get the call end reason
    incomingCall.on('callEnded', args => {
        console.log(args.callEndReason);
    });
  };