# Neuro challenge
## Table of contents
1. [Setup](#setup)
2. [Local-Development](#local-development)
3. [Client](#client)
4. [Linting](#linting)
5. [Reference](#reference)
6. [Author Notes](#author-notes)

## Setup


### Requirements

1. Python environment (i.e., python3, virtualenv, pip).
2. Docker


### Setup server

1. Open a terminal on the root of the challenge project
2. Create a virtual environment with your chosen env manager:

        eg.: python -m venv ./venv

3. Activate the virtualenv environment:

        source venv/bin/activate

4. Install python requirements:

        make install

## Local Development

1. Open a terminal on the root of the challenge project
2. Enter the virtualenv environment (if not already active):

        source venv/bin/activate

### Running locally:

        make run-local-service 

### Load testing
To run load tests, on a different terminal, from root of the project run:

        make load-test

### Load testing via Web UI
There is the option of running load tests on the API via a UI and check the results visually rather than on a terminal:
        
        make load-test-ui

Head to http://localhost:8089/neuro to setup the configs for the test
The `Neuro API Data` tab contains peak queue size(as big as it got), current queue size and total running workers

- current queue size tends to appear as `0` because the service empties the queue quite fast for the requests being sent, and it updated on each request so even if it sets a value it quickly gets stepped over by the following request


## Client
---
**Optional**

start the server on a container instead of the local run:
        
        make docker-app


---

### Running single client call:
To run a single client call as the provided example simply run:

        make client-call


modify `client/example.py` file for different uses

### Running 100 concurrent calls:
to run 100 concurrent calls in client debug mode run:

        make multi-call

modify `client/multiple_calls.py` file for different uses

## Linting

For consistency when developing, please use `make lint` for linting!

## Reference

- [cloudpickle](https://github.com/cloudpipe/cloudpickle)
- [tornado](https://www.tornadoweb.org/en/stable/)
- [concurrency on tornado](https://www.tornadoweb.org/en/branch4.5/concurrent.html)
- [click](https://click.palletsprojects.com/en/8.0.x/)
- [locust](https://locust.io/)
- [extend locust UI](https://github.com/locustio/locust/blob/master/examples/extend_web_ui/static/extend.js)

## Author Notes

I tried to keep everything encapsulated in the project and in a sort of plug and play manner, so it's just installing the deps and start doing things. To keep it simple I tried to also not have extra services running.

- I say this because an alternative to my load test monitor would run the load test suite and have logs and stats sent to datadog, but I'd have to run a datadog together with this project and I aimed to keep it simple abd timely
 - would be a followup to do for sure though.

regarding the load test web ui, I would've loved to make a chart with the queue size and running workers but extending the locust UI is quite bothersome and I could not estimate how long it would take me to make JS that plays nice with locust frontend. This would be a nice to have but if we integrate with datadog would not be necessary, since we could send metrics from the server itself regarding this information

The extended locust UI code is basically a copypaste with minimal tweaks to get the proper data displayed
This means HTML classes and ids are not very descriptive.
