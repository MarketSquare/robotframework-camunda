# Camunda & Robot Framework
*Introducing robotframework-camunda library*

Resources:
- [Source Code on GitHub.com](https://github.com/MarketSquare/robotframework-camunda)
- [Example Test Cases](https://github.com/MarketSquare/robotframework-camunda/tree/master/tests)
- [Issue Board](https://github.com/MarketSquare/robotframework-camunda/issues)

**If you are Camunda user, you probably wonder: *What is Robot Framework?***

Robot Framework is an open source automation framework for task automation. Among
other features, it offers a customizable domain language for developing tasks.
It was originally developed for test automation providing the unique advantage
making human readable test description executable.
But most importantly: it comes with the enormous api universe from python.
Meaning any python library can be integrated in to your task automation.

**If you are Robot Framework user, you probably wonder: *What is Camunda?***

2 sentences won't do it justice, just as the above summary about Robot Framework.
In their words: Camunda is a collection of "open source workflow and decision
automation tools [to] enable thousands of developers to automate business
processes and gain the agility, visibility and scale that is needed to achieve
digital transformation".

As Robot Framework enables testers around the world automating their test cases
by simply describing them, Camunda enables process designers to automate processes
by describing in BPMN. You might summerize their power with the slogan: *Automation by documentation*
Both might look like low code, but still offer the full power
for developers to enhance their ecosystem.

## Integrating Camunda and Python

Camunda is primarily built for Java developers, yet implemented the [External Task Pattern](https://docs.camunda.org/manual/7.14/user-guide/process-engine/external-tasks/#the-external-task-pattern)
enabling developers from all programming languages integrating with Camunda through
the very well documented [Camunda REST API](https://docs.camunda.org/manual/7.10/reference/rest/).
For Robot Framework, all you need is implementing a few keywords for convenience
wrapping requests to endpoints from Camunda REST API. Now you'd only need to
package your library, publish it on pypi.org and there you go: the [robotframework-camunda](https://pypi.org/project/robotframework-camunda/) library.
