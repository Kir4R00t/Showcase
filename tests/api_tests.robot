*** Settings ***
Library         Collections
Library         RequestsLibrary

Suite Setup     Create Session  mainSession  ${BASE_URL}    verify=true

*** Variables ***
${BASE_URL}    http://localhost:5000

*** Keywords ***
Status code should be 200
    [Arguments]    ${resp}
    Should Be Equal As Integers    ${resp.status_code}    200

Status text should be "UP"
    [Arguments]    ${resp}
    ${body}=    Set Variable    ${resp.json()}
    Should Be Equal    ${body["status"]}    UP

Status text should be "queued"
    [Arguments]    ${resp}
    ${body}=    Set Variable    ${resp.json()}
    Should be Equal    ${body["status"]}    queued

*** Test Cases ***
Health Check
    ${resp}=    GET On Session    mainSession    /health
    Status code should be 200    ${resp}
    Status text should be "UP"    ${resp}
Events
    ${resp}=    GET On Session    mainSession    /events
    Status code should be 200    ${resp}
