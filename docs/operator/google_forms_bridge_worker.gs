// Google Apps Script — Worker Form Bridge
// Copy-paste into Google Apps Script editor: Extensions > Apps Script
// Set up trigger: Edit > Current project's triggers > On form submit
//
// SETUP:
// 1. Replace BACKEND_URL with your server URL
// 2. Replace GOOGLE_FORMS_INTAKE_TOKEN with the token from .env
// 3. Deploy and add On form submit trigger

var BACKEND_URL = "https://YOUR_SERVER/api/intake/google-forms/worker-search";
var TOKEN = "REPLACE_WITH_GOOGLE_FORMS_INTAKE_TOKEN";

function onFormSubmit(e) {
  var formResponse = e.response;
  var itemResponses = formResponse.getItemResponses();
  var payload = {
    Timestamp: formResponse.getTimestamp().toISOString(),
    Row: "",
  };

  for (var i = 0; i < itemResponses.length; i++) {
    var item = itemResponses[i];
    var question = item.getItem().getTitle();
    var answer = item.getResponse();
    payload[question] = answer ? answer.toString() : "";
  }

  var options = {
    method: "post",
    contentType: "application/json",
    headers: {
      "Authorization": "Bearer " + TOKEN
    },
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };

  try {
    var response = UrlFetchApp.fetch(BACKEND_URL, options);
    var result = JSON.parse(response.getContentText());
    Logger.log("Bridge OK: " + result.lead_id + " status=" + result.status);
  } catch (err) {
    Logger.log("Bridge ERROR: " + err.toString());
  }
}
