*** Settings ***
Library         Collections
Library         RequestsLibrary

Suite Setup     Create Session  mainSession  ${BASE_URL}    verify=true

*** Variables ***
${BASE_URL}    http://localhost:5000

*** Keywords ***
HC Status code should be 200
    ${resp}=    GET On Session    mainSession    /health
    Should Be Equal As Integers    ${resp.status_code}    200
HC Status text should be "UP"
    ${resp}=    GET On Session    mainSession    /health
    ${body}=    Set Variable    ${resp.json()}
    Should Be Equal    ${body["status"]}    UP

*** Test Cases ***
Health Check
    HC Status code should be 200
    HC Status text should be "UP"