# Azure Communication Service demo repo

## Voice calling web app
```
cd VoiceCallingApp
npm init -y
```
```
npm install --save @azure/communication-common @azure/communication-calling
npm install --save-dev parcel
npx parcel index.html
```

## SMS Quickstart

```
cd SmsQuickstart
dotnet build
dotnet add package Azure.Communication.Sms --version 1.0.0-beta.3
dotnet run
```