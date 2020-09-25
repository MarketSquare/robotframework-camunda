*** Settings ***
Library    ../../Camunda/ExternalTask/ExternalTask.py

*** Test Cases ***
Teste 'fetch and lock'
    [Setup]    set camunda url    http://localhost:8080/engine-rest
    ${work_item}    fetch and lock    topic=test
    Should Be Empty    ${work_item}